# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import ftplib
import unittest
from unittest.mock import patch, MagicMock, mock_open

import numpy as np
import pandas as pd
import qiime2
from pandas.testing import assert_frame_equal

from q2_ena_uploader.ftp_file_upload import (
    _upload_files,
    _delete_files,
    transfer_files_to_ena,
)

# We patch this in our tests using its fully qualified name
# from q2_ena_uploader.ftp_file_upload import _process_files
from q2_ena_uploader.utils import FTP_HOST


class MockCasavaOneEightSingleLanePerSampleDirFmt:
    def __init__(self, manifest):
        self.manifest = manifest


class TestFTPFunctions(unittest.TestCase):

    @patch("ftplib.FTP")
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_upload_files_success(self, mock_isfile, mock_ftp, mock_file):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp.return_value = mock_ftp_instance

        # Test successful upload
        sampleid = "sample1"
        filepath = "path/to/file.fastq"
        result = _upload_files(mock_ftp_instance, filepath, sampleid)

        self.assertEqual(result, (sampleid, "file.fastq", True, None, "ADD"))
        mock_ftp_instance.storbinary.assert_called_once()

    @patch("ftplib.FTP")
    @patch("os.path.isfile", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_upload_files_failure(self, mock_isfile, mock_ftp, mock_file):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp_instance.storbinary.side_effect = ftplib.Error("Meh.")

        # Test failed upload
        sampleid = "sample1"
        filepath = "path/to/file.fastq"
        result = _upload_files(mock_ftp_instance, filepath, sampleid)

        self.assertEqual(
            result,
            (
                sampleid,
                "file.fastq",
                False,
                mock_ftp_instance.storbinary.side_effect.__str__(),
                "ADD",
            ),
        )

    @patch("ftplib.FTP")
    @patch("os.path.isfile", return_value=True)
    def test_delete_files_success(self, mock_isfile, mock_ftp):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp.return_value = mock_ftp_instance

        # Test successful delete
        sampleid = "sample1"
        filepath = "path/to/file.fastq"
        result = _delete_files(mock_ftp_instance, filepath, sampleid)

        self.assertEqual(result, (sampleid, "file.fastq", True, None, "DELETE"))
        mock_ftp_instance.delete.assert_called_once()

    @patch("ftplib.FTP")
    @patch("os.path.isfile", return_value=True)
    def test_delete_files_failure(self, mock_isfile, mock_ftp):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp_instance.delete.side_effect = ftplib.Error("No beer in fridge")

        # Test failed delete
        sampleid = "sample1"
        filepath = "path/to/file.fastq"
        result = _delete_files(mock_ftp_instance, filepath, sampleid)

        self.assertEqual(
            result,
            (
                sampleid,
                "file.fastq",
                False,
                mock_ftp_instance.delete.side_effect.__str__(),
                "DELETE",
            ),
        )


class TestTransferFilesToENA(unittest.TestCase):
    """Test the transfer_files_to_ena function."""

    @patch.dict(
        "os.environ", {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"}
    )
    @patch("q2_ena_uploader.ftp_file_upload._process_files")
    @patch("ftplib.FTP")
    def test_transfer_files_single_end(self, mock_ftp_class, mock_process_files):
        """Test transferring single-end files."""
        # Mock FTP connection
        mock_ftp_instance = MagicMock()
        mock_ftp_class.return_value.__enter__.return_value = mock_ftp_instance

        # Mock process_files to return specific results for each sample
        mock_process_files.side_effect = [
            ("sample1", "sample1.fastq", True, None, "ADD"),
            ("sample2", "sample2.fastq", True, None, "ADD"),
        ]

        # Create mock manifest with single-end data
        data = {
            "sample-id": ["sample1", "sample2"],
            "forward": ["/path/to/sample1.fastq", "/path/to/sample2.fastq"],
            "reverse": [None, None],
        }
        manifest = pd.DataFrame(data).set_index("sample-id")

        # Create mock demux object
        mock_demux = MockCasavaOneEightSingleLanePerSampleDirFmt(manifest)

        # Call function
        result = transfer_files_to_ena(mock_demux)

        # Verify result is a QIIME2 Metadata object with correct structure
        self.assertIsInstance(result, qiime2.Metadata)

        # Get the DataFrame from the Metadata object
        result_df = result.to_dataframe()

        # Check DataFrame structure and content
        self.assertEqual(len(result_df), 2)

        # Create expected DataFrame
        expected_data = {
            "filenames": ["sample1.fastq", "sample2.fastq"],
            "status": [1.0, 1.0],  # True is converted to 1
            "error": [np.nan, np.nan],
            "action": ["ADD", "ADD"],
        }
        expected_df = pd.DataFrame(
            expected_data, index=pd.Index(["sample1", "sample2"], name="sampleid")
        )

        # Check that DataFrames match
        assert_frame_equal(result_df, expected_df, check_dtype=False)

        # Verify FTP connection was established with correct credentials
        mock_ftp_class.assert_called_once_with(FTP_HOST)
        mock_ftp_instance.login.assert_called_once_with(
            user="test_user", passwd="test_pass"
        )

        # Verify _process_files was called twice (once for each sample)
        self.assertEqual(mock_process_files.call_count, 2)
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample1.fastq", "sample1", "ADD"
        )
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample2.fastq", "sample2", "ADD"
        )

    @patch.dict(
        "os.environ", {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"}
    )
    @patch("q2_ena_uploader.ftp_file_upload._process_files")
    @patch("ftplib.FTP")
    def test_transfer_files_paired_end(self, mock_ftp_class, mock_process_files):
        """Test transferring paired-end files."""
        # Mock FTP connection
        mock_ftp_instance = MagicMock()
        mock_ftp_class.return_value.__enter__.return_value = mock_ftp_instance

        # Mock process_files to return a successful result for each file
        mock_process_files.side_effect = [
            ("sample1_f", "sample1_R1.fastq", True, None, "ADD"),
            ("sample1_r", "sample1_R2.fastq", True, None, "ADD"),
            ("sample2_f", "sample2_R1.fastq", True, None, "ADD"),
            ("sample2_r", "sample2_R2.fastq", True, None, "ADD"),
        ]

        # Create mock manifest with paired-end data
        data = {
            "sample-id": ["sample1", "sample2"],
            "forward": ["/path/to/sample1_R1.fastq", "/path/to/sample2_R1.fastq"],
            "reverse": ["/path/to/sample1_R2.fastq", "/path/to/sample2_R2.fastq"],
        }
        manifest = pd.DataFrame(data).set_index("sample-id")

        # Create mock demux object
        mock_demux = MockCasavaOneEightSingleLanePerSampleDirFmt(manifest)

        # Call function
        result = transfer_files_to_ena(mock_demux)

        # Verify result is a QIIME2 Metadata object with correct structure
        self.assertIsInstance(result, qiime2.Metadata)

        # Get the DataFrame from the Metadata object
        result_df = result.to_dataframe()

        # Check DataFrame structure and content
        # 2 samples x 2 files each
        self.assertEqual(len(result_df), 4)

        # Create expected DataFrame
        expected_data = {
            "filenames": [
                "sample1_R1.fastq",
                "sample1_R2.fastq",
                "sample2_R1.fastq",
                "sample2_R2.fastq",
            ],
            "status": [1.0, 1.0, 1.0, 1.0],  # True is converted to 1
            "error": [np.nan, np.nan, np.nan, np.nan],
            "action": ["ADD", "ADD", "ADD", "ADD"],
        }
        expected_df = pd.DataFrame(
            expected_data,
            index=pd.Index(
                ["sample1_f", "sample1_r", "sample2_f", "sample2_r"], name="sampleid"
            ),
        )

        # Check that DataFrames match
        assert_frame_equal(result_df, expected_df, check_dtype=False)

        # Verify FTP connection was established with correct credentials
        mock_ftp_class.assert_called_once_with(FTP_HOST)
        mock_ftp_instance.login.assert_called_once_with(
            user="test_user", passwd="test_pass"
        )

        # Verify _process_files was called 4 times (twice for each sample)
        self.assertEqual(mock_process_files.call_count, 4)
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample1_R1.fastq", "sample1_f", "ADD"
        )
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample1_R2.fastq", "sample1_r", "ADD"
        )
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample2_R1.fastq", "sample2_f", "ADD"
        )
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample2_R2.fastq", "sample2_r", "ADD"
        )

    @patch.dict(
        "os.environ", {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"}
    )
    @patch("q2_ena_uploader.ftp_file_upload._process_files")
    @patch("ftplib.FTP")
    def test_transfer_files_delete_action(self, mock_ftp_class, mock_process_files):
        """Test deleting files with DELETE action."""
        # Mock FTP connection
        mock_ftp_instance = MagicMock()
        mock_ftp_class.return_value.__enter__.return_value = mock_ftp_instance

        # Mock process_files to return a successful result
        mock_process_files.return_value = (
            "sample1",
            "file.fastq",
            True,
            None,
            "DELETE",
        )

        # Create mock manifest
        data = {
            "sample-id": ["sample1"],
            "forward": ["/path/to/sample1.fastq"],
            "reverse": [None],
        }
        manifest = pd.DataFrame(data).set_index("sample-id")

        # Create mock demux object
        mock_demux = MockCasavaOneEightSingleLanePerSampleDirFmt(manifest)

        # Call function with DELETE action
        result = transfer_files_to_ena(mock_demux, action="DELETE")

        # Verify result is a QIIME2 Metadata object with correct structure
        self.assertIsInstance(result, qiime2.Metadata)

        # Get the DataFrame from the Metadata object
        result_df = result.to_dataframe()

        # Check DataFrame structure and content
        self.assertEqual(len(result_df), 1)

        # Create expected DataFrame
        expected_data = {
            "filenames": ["file.fastq"],
            "status": [1.0],  # True is converted to 1
            "error": [np.nan],
            "action": ["DELETE"],
        }
        expected_df = pd.DataFrame(
            expected_data, index=pd.Index(["sample1"], name="sampleid")
        )

        # Check that DataFrames match
        assert_frame_equal(result_df, expected_df, check_dtype=False)

        # Verify _process_files was called with DELETE action
        mock_process_files.assert_called_once_with(
            mock_ftp_instance, "/path/to/sample1.fastq", "sample1", "DELETE"
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_credentials(self):
        """Test error when FTP credentials are missing."""
        # Create mock manifest
        data = {
            "sample-id": ["sample1"],
            "forward": ["/path/to/sample1.fastq"],
            "reverse": [None],
        }
        manifest = pd.DataFrame(data).set_index("sample-id")

        # Create mock demux object
        mock_demux = MockCasavaOneEightSingleLanePerSampleDirFmt(manifest)

        # Should raise RuntimeError for missing credentials
        with self.assertRaisesRegex(RuntimeError, "Missing username or password"):
            transfer_files_to_ena(mock_demux)

    @patch.dict(
        "os.environ", {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"}
    )
    @patch("ftplib.FTP")
    def test_ftp_connection_error(self, mock_ftp_class):
        """Test error handling when FTP connection fails."""
        # Mock FTP to raise an error
        mock_ftp_class.side_effect = ftplib.Error("FTP connection failed")

        # Create mock manifest
        data = {
            "sample-id": ["sample1"],
            "forward": ["/path/to/sample1.fastq"],
            "reverse": [None],
        }
        manifest = pd.DataFrame(data).set_index("sample-id")

        # Create mock demux object
        mock_demux = MockCasavaOneEightSingleLanePerSampleDirFmt(manifest)

        # Should raise RuntimeError for FTP error
        error_msg = "An error occurred during the FTP upload/delete procedure"
        with self.assertRaisesRegex(RuntimeError, error_msg):
            transfer_files_to_ena(mock_demux)

    @patch.dict(
        "os.environ", {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"}
    )
    @patch("q2_ena_uploader.ftp_file_upload._process_files")
    @patch("ftplib.FTP")
    def test_transfer_files_with_errors(self, mock_ftp_class, mock_process_files):
        """Test handling of errors during file transfer."""
        # Mock FTP connection
        mock_ftp_instance = MagicMock()
        mock_ftp_class.return_value.__enter__.return_value = mock_ftp_instance

        # Mock process_files to return a mix of success and failure results
        mock_process_files.side_effect = [
            # First file: successful upload
            ("sample1_f", "sample1_R1.fastq", True, None, "ADD"),
            # Second file: upload fails with a permission error
            ("sample1_r", "sample1_R2.fastq", False, "553 Permission denied", "ADD"),
            # Third file: successful upload
            ("sample2_f", "sample2_R1.fastq", True, None, "ADD"),
            # Fourth file: upload fails with a disk full error
            ("sample2_r", "sample2_R2.fastq", False, "552 Disk quota exceeded", "ADD"),
        ]

        # Create mock manifest with paired-end data
        data = {
            "sample-id": ["sample1", "sample2"],
            "forward": ["/path/to/sample1_R1.fastq", "/path/to/sample2_R1.fastq"],
            "reverse": ["/path/to/sample1_R2.fastq", "/path/to/sample2_R2.fastq"],
        }
        manifest = pd.DataFrame(data).set_index("sample-id")

        # Create mock demux object
        mock_demux = MockCasavaOneEightSingleLanePerSampleDirFmt(manifest)

        # Call function
        result = transfer_files_to_ena(mock_demux)

        # Verify result is a QIIME2 Metadata object with correct structure
        self.assertIsInstance(result, qiime2.Metadata)

        # Get the DataFrame from the Metadata object
        result_df = result.to_dataframe()

        # Check DataFrame structure
        self.assertEqual(len(result_df), 4)

        # Create expected DataFrame with mix of success and error results
        expected_data = {
            "filenames": [
                "sample1_R1.fastq",
                "sample1_R2.fastq",
                "sample2_R1.fastq",
                "sample2_R2.fastq",
            ],
            "status": [1.0, 0.0, 1.0, 0.0],  # True=1, False=0
            "error": [
                np.nan,
                "553 Permission denied",
                np.nan,
                "552 Disk quota exceeded",
            ],
            "action": ["ADD", "ADD", "ADD", "ADD"],
        }
        expected_df = pd.DataFrame(
            expected_data,
            index=pd.Index(
                ["sample1_f", "sample1_r", "sample2_f", "sample2_r"], name="sampleid"
            ),
        )

        # Check that DataFrames match exactly
        assert_frame_equal(result_df, expected_df, check_dtype=False)

        # Verify FTP connection was established with correct credentials
        mock_ftp_class.assert_called_once_with(FTP_HOST)
        mock_ftp_instance.login.assert_called_once_with(
            user="test_user", passwd="test_pass"
        )

        # Verify _process_files was called 4 times (twice for each sample)
        self.assertEqual(mock_process_files.call_count, 4)
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample1_R1.fastq", "sample1_f", "ADD"
        )
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample1_R2.fastq", "sample1_r", "ADD"
        )
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample2_R1.fastq", "sample2_f", "ADD"
        )
        mock_process_files.assert_any_call(
            mock_ftp_instance, "/path/to/sample2_R2.fastq", "sample2_r", "ADD"
        )


if __name__ == "__main__":
    unittest.main()
