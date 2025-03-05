# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import ftplib
import qiime2
import os
import time
import pandas as pd
from q2_types.per_sample_sequences import CasavaOneEightSingleLanePerSampleDirFmt

from q2_ena_uploader.utils import FTP_HOST


def _upload_files(ftp, filepath, sample_id, retries=3, delay=5):
    """
    Helper function to upload single or paired files to the FTP server and return metadata.
    """

    if os.path.isfile(filepath):
        filename = os.path.basename(filepath)
        attempt = 0
        while attempt < retries:
            try:
                with open(filepath, "rb") as f:
                    ftp.storbinary(f"STOR {filename}", f)
                    break
            except ftplib.all_errors as e:
                attempt += 1
                if attempt < retries:
                    time.sleep(delay)
                else:
                    return (sample_id, filename, False, str(e), "ADD")

        return (sample_id, filename, True, None, "ADD")
    return (sample_id, os.path.basename(filepath), False, "Not a file", "ADD")


def _delete_files(ftp, filepath, sample_id, retries=3, delay=5):
    """
    Helper function to delete single or paired files to the FTP server and return metadata.
    """

    if os.path.isfile(filepath):
        filename = os.path.basename(filepath)
        attempt = 0
        while True:
            try:
                ftp.delete(filename)
                return (sample_id, filename, True, None, "DELETE")
            except ftplib.all_errors as e:
                attempt += 1
                if attempt < retries:
                    time.sleep(delay)
                else:
                    return (sample_id, filename, False, str(e), "DELETE")


def _process_files(ftp, filepath, sample_id, action):
    if action == "ADD":
        return _upload_files(ftp, filepath, sample_id)
    elif action == "DELETE":
        return _delete_files(ftp, filepath, sample_id)
    return None


def transfer_files_to_ena(
    demux: CasavaOneEightSingleLanePerSampleDirFmt, action: str = "ADD"
) -> qiime2.Metadata:
    """
    Transfers or deletes FASTQ files on the ENA FTP server.

    Args:
        demux:
             'The demultiplexed sequence data to be quality filtered.'

        action: Str
             '2 action types are supported : ADD as a default and DELETE.'

    Returns:
        metadata: Qiime immutable metadata object.
    """

    username = os.getenv("ENA_USERNAME")
    password = os.getenv("ENA_PASSWORD")

    if not username or not password:
        raise RuntimeError(
            "Missing ENA FTP credentials. Please set ENA_USERNAME "
            "and ENA_PASSWORD environment variables."
        )

    df = demux.manifest
    metadata = []

    print(f"Connecting to the FTP server {FTP_HOST}...")

    try:
        with ftplib.FTP(FTP_HOST) as ftp:
            ftp.login(user=username, passwd=password)
            print("Connected to FTP.")

            for row in df.itertuples(index=True, name="Pandas"):
                sample_id = row.Index
                if not row.reverse:
                    filepath = row.forward
                    file_metadata = _process_files(ftp, filepath, sample_id, action)
                    metadata.append(file_metadata)
                else:

                    sampleid_forward = f"{sample_id}_f"
                    sampleid_reverse = f"{sample_id}_r"
                    filepath_forward = row.forward
                    filepath_reverse = row.reverse

                    file_metadata_forward = _process_files(
                        ftp, filepath_forward, sampleid_forward, action
                    )
                    metadata.append(file_metadata_forward)

                    file_metadata_reverse = _process_files(
                        ftp, filepath_reverse, sampleid_reverse, action
                    )
                    metadata.append(file_metadata_reverse)
    except ftplib.all_errors as e:
        raise RuntimeError(
            f"An error occurred during the FTP upload/delete procedure: {e}"
        )

    upload_metadata = pd.DataFrame(
        metadata, columns=["sampleid", "filenames", "status", "error", "action"]
    )
    upload_metadata.set_index("sampleid", inplace=True)
    upload_metadata["status"] = upload_metadata["status"].astype(int)

    return qiime2.Metadata(upload_metadata)
