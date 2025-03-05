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

import pandas as pd
import requests
from q2_types.per_sample_sequences import CasavaOneEightSingleLanePerSampleDirFmt

from q2_ena_uploader.types._types_and_formats import (
    ENAMetadataExperimentFormat,
)
from .metadata import _run_set_from_dict
from .utils import ActionType, DEV_SERVER_URL, PRODUCTION_SERVER_URL


def _create_submission_xml(action: ActionType, hold_date: str) -> str:
    submission = Element("SUBMISSION")
    actions = SubElement(submission, "ACTIONS")
    action_element = SubElement(actions, "ACTION")
    SubElement(action_element, action.value)

    if hold_date:
        hold_action = SubElement(actions, "ACTION")
        hold = SubElement(hold_action, "HOLD")
        hold.set("HoldUntilDate", hold_date)

    return tostring(submission, encoding="unicode", method="xml")


def _calculate_md5(file_path):
    hash_md5 = hashlib.md5()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def _process_manifest(df: pd.DataFrame) -> dict:
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
    experiment: ENAMetadataExperimentFormat = None,
    submission_hold_date: str = "",
    action_type: str = "ADD",
    dev: bool = True,
) -> bytes:
    """
    Function to sumbmit metedata of the experiments to ENA.
    Args:
        experiment : Metadata
                Qiime artifact containing a tsv file with the metadata atrributes.
        demux: The demultiplexed sequence data to be quality filtered.

        submission_hold_date: Str
                 The release date of the study, on which it will become public along with all submitted data.
                 By default, this date is set to two months after the date of submission. User can
                 specify any date within two years of the current date.
        action_type : Str
                  2 action types are supported : ADD as a default and MODIFY
        dev : Bool
            True by default. Indicates whether the data submission goes to the development server. If False, the submission
                goes to the production server.
    Returns:
        submission_receipt : bytes
                Qiime artifact containing an XML response of ENA server.
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
