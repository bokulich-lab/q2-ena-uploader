# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from enum import Enum


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
