# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from .all import submit_all
from .ftp_file_upload import transfer_files_to_ena
from .read_submission import submit_metadata_reads
from .sample_submission import cancel_submission, submit_metadata_samples

try:
    from ._version import __version__
except ModuleNotFoundError:
    __version__ = "0.0.0+notfound"

__all__ = [
    "transfer_files_to_ena",
    "submit_metadata_reads",
    "cancel_submission",
    "submit_metadata_samples",
    "submit_all",
]
