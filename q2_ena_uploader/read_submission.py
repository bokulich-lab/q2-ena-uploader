# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import hashlib
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from typing import Dict, List, Any, Optional

import pandas as pd
import requests
from q2_types.per_sample_sequences import CasavaOneEightSingleLanePerSampleDirFmt

from q2_ena_uploader.types._types_and_formats import (
    ENAMetadataExperimentFormat,
)
from .metadata import _run_set_from_dict
from .utils import ActionType, DEV_SERVER_URL, PRODUCTION_SERVER_URL


def _create_submission_xml(action: ActionType, hold_date: str) -> str:
    """
    Create an XML submission document for ENA.

    Parameters
    ----------
    action : ActionType
        The type of action to perform (ADD or MODIFY)
    hold_date : str
        Optional date to hold the data private until.
        Format should be YYYY-MM-DD.

    Returns
    -------
    str
        The submission XML as a string
    """
    submission = Element("SUBMISSION")
    actions = SubElement(submission, "ACTIONS")
    action_element = SubElement(actions, "ACTION")
    SubElement(action_element, action.value)

    if hold_date:
        hold_action = SubElement(actions, "ACTION")
        hold = SubElement(hold_action, "HOLD")
        hold.set("HoldUntilDate", hold_date)

    return tostring(submission, encoding="unicode", method="xml")


def _calculate_md5(file_path: str) -> str:
    """
    Calculate the MD5 hash of a file.

    Parameters
    ----------
    file_path : str
        Path to the file to calculate the hash for

    Returns
    -------
    str
        The MD5 hash of the file as a hexadecimal string
    """
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def _process_manifest(df: pd.DataFrame) -> Dict[str, Dict[str, List[str]]]:
    """
    Process a QIIME2 manifest dataframe to extract file information.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the manifest information with columns:
        'forward', 'reverse' (optional), and sample IDs as the index

    Returns
    -------
    dict
        Dictionary with sample IDs as keys and dictionaries as values.
        Each inner dictionary contains:
        - 'filename': List of filenames (1 for single-end, 2 for paired-end)
        - 'checksum': List of MD5 checksums matching the filenames
    """
    parsed_data = {}
    for row in df.itertuples(index=True, name="Pandas"):
        alias = str(row.Index)
        parsed_data[alias] = {"filename": [], "checksum": []}

        forward_file = str(row.forward).split("/")[-1]
        forward_checksum = _calculate_md5(str(row.forward))
        parsed_data[alias]["filename"].append(forward_file)
        parsed_data[alias]["checksum"].append(forward_checksum)

        if pd.notna(row.reverse):
            reverse_file = str(row.reverse).split("/")[-1]
            reverse_checksum = _calculate_md5(str(row.reverse))
            parsed_data[alias]["filename"].append(reverse_file)
            parsed_data[alias]["checksum"].append(reverse_checksum)

    return parsed_data


def submit_metadata_reads(
    demux: CasavaOneEightSingleLanePerSampleDirFmt,
    experiment: Optional[ENAMetadataExperimentFormat] = None,
    submission_hold_date: str = "",
    action_type: str = "ADD",
    dev: bool = True,
) -> bytes:
    """
    Submit experiment metadata and run information to the ENA server.

    This method creates the necessary XML documents and submits them to the ENA
    submission service. It requires that the sequence files have already been
    uploaded to the ENA FTP server using the transfer_files_to_ena function.

    Parameters
    ----------
    demux : CasavaOneEightSingleLanePerSampleDirFmt
        The demultiplexed sequence data containing the manifest with file paths
    experiment : ENAMetadataExperimentFormat, optional
        Experiment metadata in ENA format, by default None.
        This parameter is required for submission.
    submission_hold_date : str, optional
        Date until which the submission should be kept private, by default "".
        Format should be YYYY-MM-DD.
        If not provided, default is two months after submission date.
        Must be within two years of the current date.
    action_type : str, optional
        Type of submission action, by default "ADD".
        Supported values:
        - "ADD": Add new data
        - "MODIFY": Modify existing data
    dev : bool, optional
        Whether to use the development server, by default True.
        - True: Submit to the development server for testing
        - False: Submit to the production server for real submissions

    Returns
    -------
    bytes
        The raw response content from the ENA server

    Raises
    ------
    ValueError
        If the experiment file is not provided
    RuntimeError
        If ENA username or password environment variables are not set
    """

    if experiment is None:
        raise ValueError("Experiment file is required for ENA submission.")

    df = demux.manifest
    parsed_data = _process_manifest(df)
    run_xml = _run_set_from_dict(parsed_data)

    username = os.getenv("ENA_USERNAME")
    password = os.getenv("ENA_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Missing username or password. Please make sure "
            "ENA_USERNAME and ENA_PASSWORD env vars are set."
        )

    submission_xml = _create_submission_xml(
        ActionType.from_string(action_type), submission_hold_date
    )
    files = {
        "SUBMISSION": ("submission.xml", submission_xml, "text/xml"),
        "EXPERIMENT": ("metadata.xml", experiment.to_xml(), "text/xml"),
        "RUN": ("run.xml", run_xml, "text/xml"),
    }
    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)
    return response.content
