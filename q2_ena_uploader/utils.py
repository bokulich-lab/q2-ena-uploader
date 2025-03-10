# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import warnings
from enum import Enum
from typing import Tuple
from xml.etree.ElementTree import fromstring

import requests

# URL for the ENA development server submission endpoint
DEV_SERVER_URL = "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit"

# URL for the ENA production server submission endpoint
PRODUCTION_SERVER_URL = "https://www.ebi.ac.uk/ena/submit/drop-box/submit"

# Hostname for the ENA FTP server for file uploads
FTP_HOST = "webin2.ebi.ac.uk"


class ActionType(Enum):
    """
    Enumeration of supported action types for ENA submissions.

    These actions determine how the submission should be processed.
    - ADD: Add new data to the archive
    - MODIFY: Modify existing data in the archive
    """

    ADD = "ADD"
    MODIFY = "MODIFY"

    @classmethod
    def from_string(cls, action_type: str) -> "ActionType":
        """
        Convert a string representation to an ActionType enum value.

        Parameters
        ----------
        action_type : str
            String representation of the action type.
            Case-insensitive (will be converted to uppercase).

        Returns
        -------
        ActionType
            The matching ActionType enum value

        Raises
        ------
        ValueError
            If the provided string doesn't match any known action type
        """
        try:
            return cls(action_type.upper())
        except ValueError:
            raise ValueError(f"Unknown action type: {action_type}")


def assert_credentials() -> Tuple[str, str]:
    username = os.getenv("ENA_USERNAME")
    password = os.getenv("ENA_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Missing username or password. Please set ENA_USERNAME "
            "and ENA_PASSWORD environment variables."
        )

    return username, password


def assert_success(response: requests.Response) -> None:
    try:
        receipt = fromstring(response.content)
        success = receipt.get("success", "").lower()
        if success == "false":
            error_msg = receipt.find(".//ERROR").text
            warnings.warn(
                "The response from the ENA server contained an error: '%s' - "
                "please inspect the output artifact to learn more." % error_msg
            )
    except Exception:
        # If parsing fails, we don't want to interrupt the normal flow
        warnings.warn(
            "Unable to parse ENA response. Please inspect the returned data manually."
        )
