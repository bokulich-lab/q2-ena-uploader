# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from enum import Enum


DEV_SERVER_URL = "https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit"
PRODUCTION_SERVER_URL = "https://www.ebi.ac.uk/ena/submit/drop-box/submit"
FTP_HOST = "webin2.ebi.ac.uk"


class ActionType(Enum):
    ADD = "ADD"
    MODIFY = "MODIFY"

    @classmethod
    def from_string(cls, action_type: str) -> "ActionType":
        """Convert a string to an ActionType enum value."""
        try:
            return cls(action_type.upper())
        except ValueError:
            raise ValueError(f"Unknown action type: {action_type}")
