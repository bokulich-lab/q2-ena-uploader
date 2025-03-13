# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import ftplib
import os
import time
from typing import Tuple, Optional
from urllib.parse import urlparse
import socks
import socket

import pandas as pd
import qiime2
from q2_types.per_sample_sequences import CasavaOneEightSingleLanePerSampleDirFmt

from q2_ena_uploader.utils import FTP_HOST, assert_credentials


def _upload_files(
    ftp: ftplib.FTP, filepath: str, sample_id: str, retries: int = 3, delay: int = 5
) -> Tuple[str, str, bool, Optional[str], str]:
    """
    Upload a single file to the ENA FTP server.

    Parameters
    ----------
    ftp : ftplib.FTP
        An active FTP connection to the ENA server
    filepath : str
        Path to the file to upload
    sample_id : str
        Sample ID associated with the file
    retries : int, optional
        Number of upload attempts before giving up, by default 3
    delay : int, optional
        Seconds to wait between retry attempts, by default 5

    Returns
    -------
    tuple
        A 5-tuple containing:
        - sample_id (str): The sample ID
        - filename (str): The base filename that was uploaded
        - status (bool): Whether the upload was successful
        - error (str or None): Error message if status is False, None otherwise
        - action (str): Always "ADD" for uploads
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


def _delete_files(
    ftp: ftplib.FTP, filepath: str, sample_id: str, retries: int = 3, delay: int = 5
) -> Tuple[str, str, bool, Optional[str], str]:
    """
    Delete a single file from the ENA FTP server.

    Parameters
    ----------
    ftp : ftplib.FTP
        An active FTP connection to the ENA server
    filepath : str
        Path to the local file whose basename will be deleted from the server
    sample_id : str
        Sample ID associated with the file
    retries : int, optional
        Number of delete attempts before giving up, by default 3
    delay : int, optional
        Seconds to wait between retry attempts, by default 5

    Returns
    -------
    tuple
        A 5-tuple containing:
        - sample_id (str): The sample ID
        - filename (str): The base filename that was deleted
        - status (bool): Whether the deletion was successful
        - error (str or None): Error message if status is False, None otherwise
        - action (str): Always "DELETE" for deletions
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


def _process_files(
    ftp: ftplib.FTP, filepath: str, sample_id: str, action: str
) -> Optional[Tuple[str, str, bool, Optional[str], str]]:
    """
    Process a file on the ENA FTP server based on the specified action.

    Parameters
    ----------
    ftp : ftplib.FTP
        An active FTP connection to the ENA server
    filepath : str
        Path to the file to process
    sample_id : str
        Sample ID associated with the file
    action : str
        Action to perform, either "ADD" for upload or "DELETE" for deletion

    Returns
    -------
    tuple or None
        A 5-tuple containing processing results, or None if the action is invalid.
        See _upload_files or _delete_files for details on the return tuple.
    """
    if action == "ADD":
        return _upload_files(ftp, filepath, sample_id)
    elif action == "DELETE":
        return _delete_files(ftp, filepath, sample_id)
    return None


def setup_proxy():
    """
    Set up a proxy connection using environment variables.

    Returns
    -------
    tuple
        A tuple containing the proxy host, proxy port, and proxy type.
    """
    proxy_url = os.getenv("http_proxy") or os.getenv("https_proxy")
    proxy_host, proxy_port, proxy_type = None, None, "HTTP"

    if proxy_url:
        parsed_url = urlparse(proxy_url)
        proxy_host = parsed_url.hostname
        proxy_port = parsed_url.port
        proxy_type = "HTTP" if parsed_url.scheme == "http" else "HTTPS"
        print(f"Proxy detected: {proxy_type} proxy at {proxy_host}:{proxy_port}")

    if proxy_host and proxy_port:
        print("Setting up proxy connection...")
        socks.set_default_proxy(socks.HTTP, proxy_host, proxy_port)
        socket.socket = socks.socksocket
        print("Proxy connection established.")

    return proxy_host, proxy_port, proxy_type


def transfer_files_to_ena(
    demux: CasavaOneEightSingleLanePerSampleDirFmt, action: str = "ADD"
) -> qiime2.Metadata:
    """
    Transfer FASTQ files to or delete them from the ENA FTP server.

    This function connects to the ENA FTP server using credentials from
    environment variables, then uploads or deletes files specified in the
    demultiplexed sequence data manifest. For paired-end reads, both forward
    and reverse reads are processed.

    Parameters
    ----------
    demux : CasavaOneEightSingleLanePerSampleDirFmt
        The demultiplexed sequence data with a manifest containing file paths
    action : str, optional
        Action to perform on the files, by default "ADD".
        Supported values:
        - "ADD": Upload files to the ENA server
        - "DELETE": Delete files from the ENA server

    Returns
    -------
    qiime2.Metadata
        A QIIME 2 Metadata object containing details of the FTP operations:
        - Sample IDs (index)
        - Filenames uploaded/deleted
        - Status of each operation (1=success, 0=failure)
        - Error messages if any operations failed
        - Action performed on each file

    Raises
    ------
    RuntimeError
        If FTP credentials are missing or if any FTP error occurs
    """

    username, password = assert_credentials()

    setup_proxy()

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
