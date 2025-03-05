# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from typing import Optional

import requests

from q2_ena_uploader.types._types_and_formats import (
    ENAMetadataSamplesFormat,
    ENAMetadataStudyFormat,
)
from q2_ena_uploader.utils import ActionType, DEV_SERVER_URL, PRODUCTION_SERVER_URL


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


def submit_metadata_samples(
    study: Optional[ENAMetadataStudyFormat] = None,
    samples: Optional[ENAMetadataSamplesFormat] = None,
    submission_hold_date: str = "",
    action_type: str = "ADD",
    dev: bool = True,
) -> bytes:
    """
    Submit study and/or sample metadata to the ENA server.

    This function creates the necessary XML documents for study and/or sample
    metadata and submits them to the ENA submission service. At least one of
    study or samples must be provided.

    Parameters
    ----------
    study : ENAMetadataStudyFormat, optional
        Study metadata in ENA format, by default None
    samples : ENAMetadataSamplesFormat, optional
        Sample metadata in ENA format, by default None
    submission_hold_date : str, optional
        Date until which the submission should be kept private, by default ""
        Format should be YYYY-MM-DD.
        If not provided, default is two months after submission date.
        Must be within two years of the current date.
    action_type : str, optional
        Type of submission action, by default "ADD"
        Supported values:
        - "ADD": Add new data
        - "MODIFY": Modify existing data
    dev : bool, optional
        Whether to use the development server, by default True
        - True: Submit to the development server for testing
        - False: Submit to the production server for real submissions

    Returns
    -------
    bytes
        The raw response content from the ENA server

    Raises
    ------
    RuntimeError
        If both study and samples are None
        If ENA username or password environment variables are not set
    """

    username = os.getenv("ENA_USERNAME")
    password = os.getenv("ENA_PASSWORD")

    if username is None or password is None:
        raise RuntimeError(
            "Missing username or password. Please make sure "
            "ENA_USERNAME and ENA_PASSWORD env vars are set."
        )

    xml_content = _create_submission_xml(
        ActionType.from_string(action_type), hold_date=submission_hold_date
    )
    files = {"SUBMISSION": ("submission.xml", xml_content, "text/xml")}

    if study is None and samples is None:
        raise RuntimeError(
            "Please ensure that either the Study file or the sample files are included for the ENA submission."
        )

    if study is not None:
        study_xml = study.to_xml()
        with open("study.xml", "w") as f:
            f.write(str(study_xml))
            files["PROJECT"] = ("project.xml", study_xml, "text/xml")

    if samples is not None:
        samples_xml = samples.to_xml()
        with open("samples.xml", "w") as f:
            f.write(str(samples_xml))
        files["SAMPLE"] = ("samples.xml", samples_xml, "text/xml")

    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)
    return response.content


def _create_cancelation_xml(target_accession: str) -> str:
    """
    Create an XML document for canceling a submission in ENA.

    Parameters
    ----------
    target_accession : str
        The accession number of the submission to cancel

    Returns
    -------
    str
        The cancellation XML as a string
    """
    submission = Element("SUBMISSION")
    actions = SubElement(submission, "ACTIONS")
    action_element = SubElement(actions, "ACTION")
    cancel = SubElement(action_element, "CANCEL")
    cancel.set("target", target_accession)
    return tostring(submission, encoding="unicode", method="xml")


def cancel_submission(accession_number: str, dev: bool = True) -> bytes:
    """
    Cancel a submission to the ENA server.

    This function creates a cancellation request and submits it to the ENA server.
    Note that the cancellation will be propagated from studies to all associated
    experiments and analyses, and from experiments to all associated runs.

    Parameters
    ----------
    accession_number : str
        Accession number of the submission to cancel.
        This identifies the specific object being cancelled.
    dev : bool, optional
        Whether to use the development server, by default True
        - True: Submit to the development server for testing
        - False: Submit to the production server for real cancellations

    Returns
    -------
    bytes
        The raw response content from the ENA server

    Raises
    ------
    RuntimeError
        If ENA username or password environment variables are not set
    """

    username = os.getenv("ENA_USERNAME")
    password = os.getenv("ENA_PASSWORD")

    if username is None or password is None:
        raise RuntimeError(
            "Missing username or password. Please make sure "
            "ENA_USERNAME and ENA_PASSWORD env vars are set."
        )

    files = {
        "SUBMISSION": (
            "submission.xml",
            _create_cancelation_xml(target_accession=accession_number),
            "text/xml",
        )
    }

    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)
    return response.content
