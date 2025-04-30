# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
from xml.etree.ElementTree import fromstring

from qiime2.plugin.testing import TestPluginBase

from q2_ena_uploader.sample_submission import (
    _create_submission_xml,
    submit_metadata_samples,
    _create_cancelation_xml,
    cancel_submission,
)
from q2_ena_uploader.utils import ActionType, DEV_SERVER_URL, PRODUCTION_SERVER_URL


class TestActionType(unittest.TestCase):
    """Tests for the ActionType enum."""

    def test_action_type_values(self):
        """Test that ActionType enum has the correct values."""
        self.assertEqual(ActionType.ADD.value, "ADD")
        self.assertEqual(ActionType.MODIFY.value, "MODIFY")

    def test_from_string_valid(self):
        """Test conversion from valid string to ActionType."""
        self.assertEqual(ActionType.from_string("ADD"), ActionType.ADD)
        self.assertEqual(ActionType.from_string("add"), ActionType.ADD)
        self.assertEqual(ActionType.from_string("MODIFY"), ActionType.MODIFY)
        self.assertEqual(ActionType.from_string("modify"), ActionType.MODIFY)

    def test_from_string_invalid(self):
        """Test conversion from invalid string raises ValueError."""
        with self.assertRaises(ValueError):
            ActionType.from_string("INVALID")


class TestCreateSubmissionXML(unittest.TestCase):
    """Tests for the _create_submission_xml function."""

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


class TestSubmitMetadataSamples(TestPluginBase):
    """Tests for the submit_metadata_samples function."""

    package = "q2_ena_uploader.tests"

    @patch.dict(os.environ, {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"})
    @patch("q2_ena_uploader.sample_submission._create_submission_xml")
    @patch("q2_ena_uploader.sample_submission.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    def test_submit_metadata_study_only(self, mock_file, mock_post, mock_create_xml):
        """Test submitting only study metadata."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b"<xml>Success</xml>"
        mock_post.return_value = mock_response

        # Mock study format
        mock_study = MagicMock()
        mock_study.to_xml.return_value = "<PROJECT>test-study</PROJECT>"

        # Mock XML creation
        mock_create_xml.return_value = "<SUBMISSION>test-submission</SUBMISSION>"

        # Call the function
        result = submit_metadata_samples(study=mock_study, dev=True)

        # Check result
        self.assertEqual(result, b"<xml>Success</xml>")

        # Verify calls with specific arguments
        mock_create_xml.assert_called_once_with(ActionType.ADD, hold_date="")
        mock_post.assert_called_once_with(
            DEV_SERVER_URL,
            auth=("test_user", "test_pass"),
            files={
                "SUBMISSION": (
                    "submission.xml",
                    "<SUBMISSION>test-submission</SUBMISSION>",
                    "text/xml",
                ),
                "PROJECT": ("project.xml", "<PROJECT>test-study</PROJECT>", "text/xml"),
            },
        )
        mock_study.to_xml.assert_called_once_with()

    @patch.dict(os.environ, {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"})
    @patch("q2_ena_uploader.sample_submission._create_submission_xml")
    @patch("q2_ena_uploader.sample_submission.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    def test_submit_metadata_samples_only(self, mock_file, mock_post, mock_create_xml):
        """Test submitting only sample metadata."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b"<xml>Success</xml>"
        mock_post.return_value = mock_response

        # Mock samples format
        mock_samples = MagicMock()
        mock_samples.to_xml.return_value = "<SAMPLE>test-sample</SAMPLE>"

        # Mock XML creation
        mock_create_xml.return_value = "<SUBMISSION>test-submission</SUBMISSION>"

        # Call the function
        result = submit_metadata_samples(samples=mock_samples, dev=True)

        # Check result
        self.assertEqual(result, b"<xml>Success</xml>")

        # Verify calls with specific arguments
        mock_create_xml.assert_called_once_with(ActionType.ADD, hold_date="")
        mock_post.assert_called_once_with(
            DEV_SERVER_URL,
            auth=("test_user", "test_pass"),
            files={
                "SUBMISSION": (
                    "submission.xml",
                    "<SUBMISSION>test-submission</SUBMISSION>",
                    "text/xml",
                ),
                "SAMPLE": ("samples.xml", "<SAMPLE>test-sample</SAMPLE>", "text/xml"),
            },
        )
        mock_samples.to_xml.assert_called_once_with()

    @patch.dict(os.environ, {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"})
    @patch("q2_ena_uploader.sample_submission._create_submission_xml")
    @patch("q2_ena_uploader.sample_submission.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    def test_submit_both_study_and_samples(self, mock_file, mock_post, mock_create_xml):
        """Test submitting both study and sample metadata."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b"<xml>Success</xml>"
        mock_post.return_value = mock_response

        # Mock study and samples format
        mock_study = MagicMock()
        mock_study.to_xml.return_value = "<PROJECT>test-study</PROJECT>"

        mock_samples = MagicMock()
        mock_samples.to_xml.return_value = "<SAMPLE>test-sample</SAMPLE>"

        # Mock XML creation
        mock_create_xml.return_value = "<SUBMISSION>test-submission</SUBMISSION>"

        # Call the function
        result = submit_metadata_samples(
            study=mock_study,
            samples=mock_samples,
            submission_hold_date="2023-12-31",
            action="MODIFY",
            dev=False,
        )

        # Check result
        self.assertEqual(result, b"<xml>Success</xml>")

        # Verify all mocks were called with the correct arguments
        mock_create_xml.assert_called_once_with(
            ActionType.MODIFY, hold_date="2023-12-31"
        )
        mock_post.assert_called_once_with(
            PRODUCTION_SERVER_URL,
            auth=("test_user", "test_pass"),
            files={
                "SUBMISSION": (
                    "submission.xml",
                    "<SUBMISSION>test-submission</SUBMISSION>",
                    "text/xml",
                ),
                "PROJECT": ("project.xml", "<PROJECT>test-study</PROJECT>", "text/xml"),
                "SAMPLE": ("samples.xml", "<SAMPLE>test-sample</SAMPLE>", "text/xml"),
            },
        )
        mock_study.to_xml.assert_called_once_with()
        mock_samples.to_xml.assert_called_once_with()

    @patch.dict(os.environ, {})
    def test_missing_credentials(self):
        """Test that error is raised when credentials are missing."""
        with self.assertRaisesRegex(RuntimeError, "Missing username or password"):
            submit_metadata_samples()

    def test_missing_study_and_samples(self):
        """Test that error is raised when both study and samples are None."""
        with self.assertRaisesRegex(
            RuntimeError, "Please ensure that either the Study file"
        ):
            with patch.dict(
                os.environ, {"ENA_USERNAME": "user", "ENA_PASSWORD": "pass"}
            ):
                submit_metadata_samples()


class TestCancelSubmission(TestPluginBase):
    """Tests for the cancel_submission function."""

    package = "q2_ena_uploader.tests"

    def test_create_cancelation_xml(self):
        """Test creating cancelation XML."""
        accession = "ERP123456"
        xml_str = _create_cancelation_xml(accession)

        # Parse XML
        root = fromstring(xml_str)

        # Check structure
        self.assertEqual(root.tag, "SUBMISSION")

        # Check ACTIONS
        actions = root.find("ACTIONS")
        self.assertIsNotNone(actions)

        # Check CANCEL action
        action = actions.find("ACTION")
        self.assertIsNotNone(action)

        cancel_element = action.find("CANCEL")
        self.assertIsNotNone(cancel_element)

        # Check target attribute
        self.assertEqual(cancel_element.get("target"), accession)

    @patch.dict(os.environ, {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"})
    @patch("q2_ena_uploader.sample_submission._create_cancelation_xml")
    @patch("q2_ena_uploader.sample_submission.requests.post")
    @patch("builtins.open", new_callable=mock_open)
    def test_cancel_submission(self, mock_file, mock_post, mock_create_xml):
        """Test canceling a submission."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = b"<xml>Canceled</xml>"
        mock_post.return_value = mock_response

        # Mock XML creation
        cancel_xml = (
            "<SUBMISSION><ACTIONS><ACTION>"
            "<CANCEL target='ERP123456'/>"
            "</ACTION></ACTIONS></SUBMISSION>"
        )
        mock_create_xml.return_value = cancel_xml

        # Call the function
        result = cancel_submission("ERP123456", dev=True)

        # Check result
        self.assertEqual(result, b"<xml>Canceled</xml>")

        # Verify calls with specific arguments
        mock_create_xml.assert_called_once_with("ERP123456")
        mock_post.assert_called_once_with(
            DEV_SERVER_URL,
            auth=("test_user", "test_pass"),
            files={"SUBMISSION": ("submission.xml", cancel_xml, "text/xml")},
        )

    @patch.dict(os.environ, {}, clear=True)  # This completely clears os.environ
    def test_cancel_missing_credentials(self):
        """Test error raised when credentials are missing for cancellation."""
        # The actual error message includes more text than just
        # "Missing username or password"
        expected_msg = "Missing username or password"
        with self.assertRaisesRegex(RuntimeError, expected_msg):
            cancel_submission("ERP123456")


if __name__ == "__main__":
    unittest.main()
