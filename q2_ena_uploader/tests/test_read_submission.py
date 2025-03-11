# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock, mock_open, call
from xml.etree.ElementTree import fromstring

import pandas as pd
import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_ena_uploader.read_submission import (
    _create_submission_xml,
    _calculate_md5,
    _process_manifest,
    submit_metadata_reads,
    _validate_sample_ids_match,
    PRODUCTION_SERVER_URL,
)
from q2_ena_uploader.types import ENASubmissionReceiptFormat
from q2_ena_uploader.utils import ActionType


class TestCreateSubmissionXML(unittest.TestCase):
    """Tests for the _create_submission_xml function in read_submission."""

    def test_create_submission_xml_add_no_hold(self):
        """Test creating submission XML with ADD action and no hold date."""
        xml_str = _create_submission_xml(ActionType.ADD, "")

        # Parse the XML to verify its structure
        root = fromstring(xml_str)

        # Check basic structure
        self.assertEqual(root.tag, "SUBMISSION")

        # Check ACTIONS
        actions = root.find("ACTIONS")
        self.assertIsNotNone(actions)

        # Check specific ACTION
        action = actions.find("ACTION")
        self.assertIsNotNone(action)

        # Check ADD element exists
        add_element = action.find("ADD")
        self.assertIsNotNone(add_element)

        # Ensure there's no HOLD element
        hold_actions = [
            a for a in actions.findall("ACTION") if a.find("HOLD") is not None
        ]
        self.assertEqual(len(hold_actions), 0)

    def test_create_submission_xml_with_hold_date(self):
        """Test creating submission XML with a hold date."""
        hold_date = "2023-12-31"
        xml_str = _create_submission_xml(ActionType.ADD, hold_date)

        # Parse the XML
        root = fromstring(xml_str)

        # Find HOLD element
        actions = root.find("ACTIONS")
        hold_actions = [
            a for a in actions.findall("ACTION") if a.find("HOLD") is not None
        ]

        # Should have one HOLD action
        self.assertEqual(len(hold_actions), 1)

        # Check hold date attribute
        hold_element = hold_actions[0].find("HOLD")
        self.assertEqual(hold_element.get("HoldUntilDate"), hold_date)


class TestCalculateMD5(unittest.TestCase):
    """Tests for the _calculate_md5 function."""

    @patch("builtins.open", new_callable=mock_open, read_data=b"test data")
    def test_calculate_md5(self, mock_file):
        """Test MD5 calculation with mocked file."""
        # The MD5 for "test data" is known
        expected_md5 = "eb733a00c0c9d336e65691a37ab54293"

        file_path = "/path/to/test_file.fastq"
        md5_result = _calculate_md5(file_path)

        # Check the MD5 matches the expected value
        self.assertEqual(md5_result, expected_md5)

        # Verify the file was opened in binary mode
        mock_file.assert_called_once_with(file_path, "rb")


class TestProcessManifest(unittest.TestCase):
    """Tests for the _process_manifest function."""

    @patch("q2_ena_uploader.read_submission._calculate_md5")
    def test_process_manifest_paired_end(self, mock_md5):
        """Test processing a manifest with paired-end reads."""
        # Set up the mock to return predictable values
        mock_md5.side_effect = [
            "md5_forward",
            "md5_reverse",
            "md5_forward2",
            "md5_reverse2",
        ]

        # Create a test dataframe with paired-end data
        data = {
            "sample-id": ["sample1", "sample2"],
            "forward": ["/path/to/sample1_R1.fastq", "/path/to/sample2_R1.fastq"],
            "reverse": ["/path/to/sample1_R2.fastq", "/path/to/sample2_R2.fastq"],
        }
        df = pd.DataFrame(data).set_index("sample-id")

        # Process the manifest
        result = _process_manifest(df)

        # Check the structure of the returned dictionary
        self.assertEqual(len(result), 2)
        self.assertIn("sample1", result)
        self.assertIn("sample2", result)

        # Check the files and checksums for sample1
        self.assertEqual(
            result["sample1"]["filename"], ["sample1_R1.fastq", "sample1_R2.fastq"]
        )
        self.assertEqual(result["sample1"]["checksum"], ["md5_forward", "md5_reverse"])

        # Check the files and checksums for sample2
        self.assertEqual(
            result["sample2"]["filename"], ["sample2_R1.fastq", "sample2_R2.fastq"]
        )
        self.assertEqual(
            result["sample2"]["checksum"], ["md5_forward2", "md5_reverse2"]
        )

        # Verify _calculate_md5 was called with the correct paths
        mock_md5.assert_has_calls(
            [
                call("/path/to/sample1_R1.fastq"),
                call("/path/to/sample1_R2.fastq"),
                call("/path/to/sample2_R1.fastq"),
                call("/path/to/sample2_R2.fastq"),
            ]
        )

    @patch("q2_ena_uploader.read_submission._calculate_md5")
    def test_process_manifest_single_end(self, mock_md5):
        """Test processing a manifest with single-end reads."""
        # Set up the mock to return predictable values
        mock_md5.side_effect = ["md5_forward1", "md5_forward2"]

        # Create a test dataframe with single-end data (NaN for reverse)
        data = {
            "sample-id": ["sample1", "sample2"],
            "forward": ["/path/to/sample1_R1.fastq", "/path/to/sample2_R1.fastq"],
            "reverse": [None, None],
        }
        df = pd.DataFrame(data).set_index("sample-id")

        # Process the manifest
        result = _process_manifest(df)

        # Check the structure of the returned dictionary
        self.assertEqual(len(result), 2)

        # Check the files and checksums for sample1 (should only have forward)
        self.assertEqual(result["sample1"]["filename"], ["sample1_R1.fastq"])
        self.assertEqual(result["sample1"]["checksum"], ["md5_forward1"])

        # Check the files and checksums for sample2 (should only have forward)
        self.assertEqual(result["sample2"]["filename"], ["sample2_R1.fastq"])
        self.assertEqual(result["sample2"]["checksum"], ["md5_forward2"])

        # Verify _calculate_md5 was called only for forward reads
        mock_md5.assert_has_calls(
            [
                call("/path/to/sample1_R1.fastq"),
                call("/path/to/sample2_R1.fastq"),
            ]
        )


class TestSubmitMetadataReads(TestPluginBase):
    """Tests for the submit_metadata_reads function."""

    package = "q2_ena_uploader.tests"

    @patch.dict(os.environ, {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"})
    @patch("q2_ena_uploader.read_submission._validate_sample_ids_match")
    @patch("q2_ena_uploader.read_submission._create_submission_xml")
    @patch("q2_ena_uploader.read_submission._process_manifest")
    @patch("q2_ena_uploader.read_submission._run_set_from_dict")
    @patch("q2_ena_uploader.read_submission.requests.post")
    def test_submit_metadata_reads(
        self, mock_post, mock_run_set, mock_process, mock_create_xml, mock_validate
    ):
        """Test submitting metadata reads with all necessary parameters."""
        # Create mock response
        mock_response = MagicMock()
        mock_response.content = b"<xml>Success</xml>"
        mock_post.return_value = mock_response

        # Set up other mocks
        mock_create_xml.return_value = "<SUBMISSION>test-submission</SUBMISSION>"
        mock_process.return_value = {
            "sample1": {"filename": ["file1.fastq"], "checksum": ["md5"]}
        }
        mock_run_set.return_value = "<RUN_SET>test-run-set</RUN_SET>"

        # Create mock experiment and demux objects
        mock_experiment = MagicMock()
        mock_experiment.to_xml.return_value = (
            "<EXPERIMENT_SET>test-experiment</EXPERIMENT_SET>"
        )

        # Create mock receipt and transfer metadata
        mock_receipt_samples = MagicMock()
        mock_transfer_metadata = MagicMock(spec=qiime2.Metadata)

        # Create mock demux with test data
        mock_demux = MagicMock()
        mock_demux.manifest = pd.DataFrame(
            {"forward": ["/path/to/file1.fastq"], "reverse": [None]}, index=["sample1"]
        )

        # Call the function
        result = submit_metadata_reads(
            demux=mock_demux,
            experiment=mock_experiment,
            samples_submission_receipt=mock_receipt_samples,
            file_transfer_metadata=mock_transfer_metadata,
            submission_hold_date="2023-12-31",
            action="MODIFY",
            dev=False,
        )

        # Check result
        self.assertEqual(result, b"<xml>Success</xml>")

        # Verify all mocks were called with the correct arguments
        mock_validate.assert_called_once_with(
            mock_demux.manifest,
            mock_transfer_metadata,
            mock_receipt_samples,
            mock_experiment,
        )
        mock_process.assert_called_once_with(mock_demux.manifest)
        mock_run_set.assert_called_once_with(
            {"sample1": {"filename": ["file1.fastq"], "checksum": ["md5"]}}
        )
        mock_create_xml.assert_called_once_with(ActionType.MODIFY, "2023-12-31")
        mock_experiment.to_xml.assert_called_once_with()

        # Verify the POST request
        mock_post.assert_called_once_with(
            PRODUCTION_SERVER_URL,  # Using production URL as dev=False
            auth=("test_user", "test_pass"),
            files={
                "SUBMISSION": (
                    "submission.xml",
                    "<SUBMISSION>test-submission</SUBMISSION>",
                    "text/xml",
                ),
                "EXPERIMENT": (
                    "metadata.xml",
                    "<EXPERIMENT_SET>test-experiment</EXPERIMENT_SET>",
                    "text/xml",
                ),
                "RUN": ("run.xml", "<RUN_SET>test-run-set</RUN_SET>", "text/xml"),
            },
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials(self):
        """Test that error is raised when credentials are missing."""
        mock_experiment = MagicMock()
        mock_demux = MagicMock()
        mock_receipt_samples = MagicMock()
        mock_transfer_metadata = MagicMock(spec=qiime2.Metadata)

        with self.assertRaisesRegex(RuntimeError, "Missing username or password"):
            submit_metadata_reads(
                mock_demux,
                mock_experiment,
                mock_receipt_samples,
                mock_transfer_metadata,
            )


class TestValidateSampleIDsMatch(TestPluginBase):
    """Tests for the _validate_sample_ids_match function."""

    package = "q2_ena_uploader.tests"

    def setUp(self):
        super().setUp()
        # Create mock data for demux_df
        self.demux_df = pd.DataFrame(
            {
                "forward": ["/path/to/sample1_R1.fastq", "/path/to/sample2_R1.fastq"],
                "reverse": ["/path/to/sample1_R2.fastq", "/path/to/sample2_R2.fastq"],
            },
            index=pd.Index(["sample1", "sample2"], name="id"),
        )

        # Create mock data for file_transfer_metadata
        self.file_transfer_metadata = qiime2.Metadata(
            pd.DataFrame(index=pd.Index(["sample1", "sample2"], name="id"))
        )

        # Create mock data for experiment
        self.experiment = MagicMock()
        self.experiment.view.return_value = pd.DataFrame(
            index=pd.Index(["sample1", "sample2"], name="id")
        )

        # Set up paths to XML files
        self.sample_xml = self.get_data_path("sample_receipt.xml")
        self.sample_xml_mismatch = self.get_data_path("sample_receipt_mismatch.xml")
        self.submission_receipt_samples = ENASubmissionReceiptFormat(
            self.sample_xml, "r"
        )
        self.submission_receipt_samples_mismatch = ENASubmissionReceiptFormat(
            self.sample_xml_mismatch, "r"
        )

    def test_all_sample_ids_match(self):
        """Test that no error is raised when all sample IDs match."""

        _validate_sample_ids_match(
            self.demux_df,
            self.file_transfer_metadata,
            self.submission_receipt_samples,
            self.experiment,
        )

    def test_mismatch_in_file_transfer_metadata(self):
        """Test mismatch between demux and file transfer metadata."""

        # Modify file_transfer_metadata to introduce a mismatch
        self.file_transfer_metadata = qiime2.Metadata(
            pd.DataFrame(index=pd.Index(["sample1", "sample3"], name="id"))
        )

        with self.assertRaisesRegex(ValueError, "missing in file_transfer_metadata"):
            _validate_sample_ids_match(
                self.demux_df,
                self.file_transfer_metadata,
                self.submission_receipt_samples,
                self.experiment,
            )

    def test_mismatch_in_submission_receipt_samples(self):
        """Test mismatch between demux and submission receipt samples."""

        with self.assertRaisesRegex(
            ValueError, "missing in submission_receipt_samples"
        ):
            _validate_sample_ids_match(
                self.demux_df,
                self.file_transfer_metadata,
                self.submission_receipt_samples_mismatch,
                self.experiment,
            )

    def test_mismatch_in_experiment_metadata(self):
        """Test mismatch between demux and experiment metadata."""
        # Modify experiment to introduce a mismatch
        self.experiment.view.return_value = pd.DataFrame(
            index=pd.Index(["sample1", "sample3"], name="id")
        )

        with self.assertRaisesRegex(ValueError, "missing in experiment metadata"):
            _validate_sample_ids_match(
                self.demux_df,
                self.file_transfer_metadata,
                self.submission_receipt_samples,
                self.experiment,
            )

    def test_multiple_mismatches(self):
        """Test multiple mismatches across different sources."""
        # Modify all sources to introduce multiple mismatches
        self.file_transfer_metadata = qiime2.Metadata(
            pd.DataFrame(index=pd.Index(["sample1", "sample3"], name="id"))
        )
        self.submission_receipt_samples.read_ET_from_file.return_value = ET.Element(
            "RECEIPT",
            attrib={"success": "true"},
            children=[
                ET.Element("SAMPLE", attrib={"alias": "sample1"}),
                ET.Element("SAMPLE", attrib={"alias": "sample3"}),
            ],
        )
        self.experiment.view.return_value = pd.DataFrame(
            index=pd.Index(["sample1", "sample3"], name="id")
        )

        with self.assertRaises(ValueError) as context:
            _validate_sample_ids_match(
                self.demux_df,
                self.file_transfer_metadata,
                self.submission_receipt_samples_mismatch,
                self.experiment,
            )

        self.assertIn("missing in file_transfer_metadata", str(context.exception))
        self.assertIn("missing in submission_receipt_samples", str(context.exception))
        self.assertIn("missing in experiment metadata", str(context.exception))


if __name__ == "__main__":
    unittest.main()
