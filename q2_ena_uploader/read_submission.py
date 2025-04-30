# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import hashlib
from typing import Dict, List
from xml.etree.ElementTree import Element, SubElement, tostring

import pandas as pd
import qiime2
import requests
from q2_types.per_sample_sequences import CasavaOneEightSingleLanePerSampleDirFmt

from q2_ena_uploader.types._types_and_formats import (
    ENAMetadataExperimentFormat,
    ENASubmissionReceiptFormat,
)
from q2_ena_uploader.utils import (
    ActionType,
    DEV_SERVER_URL,
    PRODUCTION_SERVER_URL,
    assert_success,
    assert_credentials,
)
from .metadata.run import _run_set_from_dict


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


def _remove_suffixes(ids: set):
    base_ids = set()
    ids_with_suffixes = set()

    for _id in ids:
        if _id.endswith("_f") or _id.endswith("_r"):
            base_id = _id[:-2]
            ids_with_suffixes.add(base_id)
        else:
            base_ids.add(_id)

    # Check if all base IDs have both suffixes
    for base_id in ids_with_suffixes:
        if f"{base_id}_f" in ids and f"{base_id}_r" in ids:
            base_ids.add(base_id)

    return base_ids


def _validate_sample_ids_match(
    demux_df: pd.DataFrame,
    file_transfer_metadata: qiime2.Metadata,
    submission_receipt_samples: ENASubmissionReceiptFormat,
    experiment: ENAMetadataExperimentFormat,
) -> None:
    """
    Validate that sample IDs match exactly across all four sources.

    Parameters
    ----------
    demux_df : pd.DataFrame
        The demultiplexed sequence manifest with sample IDs as index.
    file_transfer_metadata : qiime2.Metadata
        Metadata from the file transfer operation with sample IDs as index.
    submission_receipt_samples : ENASubmissionReceiptFormat
        Receipt from the sample/study submission containing sample aliases.
    experiment : ENAMetadataExperimentFormat
        Experiment metadata in ENA format.

    Raises
    ------
    ValueError
        If sample IDs don't match across the sources, with details about
        mismatches.
    """
    # 1. Get sample IDs from demux manifest
    demux_sample_ids = set(demux_df.index)

    # 2. Get sample IDs from file_transfer_metadata
    file_transfer_sample_ids = set(file_transfer_metadata.to_dataframe().index)

    # if reads were paired-end, sample ids will have _f and _r suffixes - remove them
    file_transfer_sample_ids = _remove_suffixes(file_transfer_sample_ids)

    # 3. Get sample aliases from submission_receipt_samples XML
    receipt_sample_ids = set()
    receipt_xml = ENASubmissionReceiptFormat.read_ET_from_file(
        str(submission_receipt_samples)
    )
    for sample_elem in receipt_xml.findall(".//SAMPLE"):
        if "alias" in sample_elem.attrib:
            receipt_sample_ids.add(sample_elem.attrib["alias"])

    # 4. Get sample IDs from experiment DataFrame
    experiment_df = experiment.view(pd.DataFrame)
    experiment_sample_ids = set(experiment_df.index)

    # Check if all sets are equal
    mismatch = False
    mismatches = {}

    if demux_sample_ids != file_transfer_sample_ids:
        mismatch = True
        mismatches["file_transfer"] = {
            "missing": demux_sample_ids - file_transfer_sample_ids,
            "extra": file_transfer_sample_ids - demux_sample_ids,
        }

    if demux_sample_ids != receipt_sample_ids:
        mismatch = True
        mismatches["receipt"] = {
            "missing": demux_sample_ids - receipt_sample_ids,
            "extra": receipt_sample_ids - demux_sample_ids,
        }

    if demux_sample_ids != experiment_sample_ids:
        mismatch = True
        mismatches["experiment"] = {
            "missing": demux_sample_ids - experiment_sample_ids,
            "extra": experiment_sample_ids - demux_sample_ids,
        }

    if mismatch:
        error_msg = "Sample IDs don't match across the different sources:\n"

        if "file_transfer" in mismatches:
            if mismatches["file_transfer"]["missing"]:
                error_msg += (
                    f"- Samples in demux artifact but missing in "
                    f"file_transfer_metadata: "
                    f"{', '.join(mismatches['file_transfer']['missing'])}\n"
                )
            if mismatches["file_transfer"]["extra"]:
                error_msg += (
                    f"- Extra samples in file_transfer_metadata not in demux artifact: "
                    f"{', '.join(mismatches['file_transfer']['extra'])}\n"
                )

        if "receipt" in mismatches:
            if mismatches["receipt"]["missing"]:
                error_msg += (
                    f"- Samples in demux artifact but missing "
                    f"in submission_receipt_samples: "
                    f"{', '.join(mismatches['receipt']['missing'])}\n"
                )
            if mismatches["receipt"]["extra"]:
                error_msg += (
                    f"- Extra samples in submission_receipt_samples "
                    f"not in demux artifact: "
                    f"{', '.join(mismatches['receipt']['extra'])}\n"
                )

        if "experiment" in mismatches:
            if mismatches["experiment"]["missing"]:
                error_msg += (
                    f"- Samples in demux artifact but missing in experiment metadata: "
                    f"{', '.join(mismatches['experiment']['missing'])}\n"
                )
            if mismatches["experiment"]["extra"]:
                error_msg += (
                    f"- Extra samples in experiment metadata not in demux artifact: "
                    f"{', '.join(mismatches['experiment']['extra'])}\n"
                )

        raise ValueError(error_msg)


def submit_metadata_reads(
    demux: CasavaOneEightSingleLanePerSampleDirFmt,
    experiment: ENAMetadataExperimentFormat,
    samples_submission_receipt: ENASubmissionReceiptFormat,
    file_transfer_metadata: qiime2.Metadata,
    submission_hold_date: str = "",
    action: str = "ADD",
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
        The demultiplexed sequence data containing the manifest with file paths.
    experiment : ENAMetadataExperimentFormat
        Experiment metadata in ENA format.
    samples_submission_receipt : ENASubmissionReceiptFormat
        Receipt from the sample/study submission.
    file_transfer_metadata : qiime2.Metadata
        Metadata from the file transfer operation.
    submission_hold_date : str, optional
        Date until which the submission should be kept private, by default "".
        Format should be YYYY-MM-DD.
        If not provided, default is two months after submission date.
        Must be within two years of the current date.
    action : str, optional
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
    ValueError
        If sample IDs don't match across the required sources
    """
    username, password = assert_credentials()

    # Get the manifest DataFrame
    df = demux.manifest

    # Validate that sample IDs match across all sources
    _validate_sample_ids_match(
        df, file_transfer_metadata, samples_submission_receipt, experiment
    )

    parsed_data = _process_manifest(df)

    run_xml = _run_set_from_dict(parsed_data)
    submission_xml = _create_submission_xml(
        ActionType.from_string(action), submission_hold_date
    )
    files = {
        "SUBMISSION": ("submission.xml", submission_xml, "text/xml"),
        "EXPERIMENT": ("metadata.xml", experiment.to_xml(), "text/xml"),
        "RUN": ("run.xml", run_xml, "text/xml"),
    }
    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)

    assert_success(response)

    return response.content
