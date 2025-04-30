# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import unittest
import warnings
from unittest.mock import patch, Mock

import requests
from qiime2.plugin.testing import TestPluginBase

from q2_ena_uploader.utils import assert_credentials, assert_success, ActionType


class TestActionType(TestPluginBase):
    """Tests for the ActionType enum."""

    package = "q2_ena_uploader.tests"

    def test_action_type_values(self):
        """Test that ActionType enum has the expected values."""
        self.assertEqual(ActionType.ADD.value, "ADD")
        self.assertEqual(ActionType.MODIFY.value, "MODIFY")

    def test_from_string_valid(self):
        """Test that from_string converts valid string representations correctly."""
        # Test case-insensitive conversion
        self.assertEqual(ActionType.from_string("add"), ActionType.ADD)
        self.assertEqual(ActionType.from_string("ADD"), ActionType.ADD)
        self.assertEqual(ActionType.from_string("Add"), ActionType.ADD)

        self.assertEqual(ActionType.from_string("modify"), ActionType.MODIFY)
        self.assertEqual(ActionType.from_string("MODIFY"), ActionType.MODIFY)
        self.assertEqual(ActionType.from_string("Modify"), ActionType.MODIFY)

    def test_from_string_invalid(self):
        """Test that from_string raises ValueError for invalid action types."""
        with self.assertRaisesRegex(ValueError, "Unknown action type: invalid_action"):
            ActionType.from_string("invalid_action")


class TestAssertCredentials(TestPluginBase):
    """Tests for the assert_credentials function."""

    package = "q2_ena_uploader.tests"

    @patch.dict(os.environ, {"ENA_USERNAME": "test_user", "ENA_PASSWORD": "test_pass"})
    def test_assert_credentials_success(self):
        """Test that assert_credentials returns the credentials when they are set."""
        username, password = assert_credentials()
        self.assertEqual(username, "test_user")
        self.assertEqual(password, "test_pass")

    @patch.dict(os.environ, {"ENA_USERNAME": ""}, clear=True)
    def test_assert_credentials_missing_username(self):
        """Test that assert_credentials raises an error when username is missing."""
        with self.assertRaisesRegex(RuntimeError, "Missing username or password"):
            assert_credentials()

    @patch.dict(os.environ, {"ENA_USERNAME": "test_user"}, clear=True)
    def test_assert_credentials_missing_password(self):
        """Test that assert_credentials raises an error when password is missing."""
        with self.assertRaisesRegex(RuntimeError, "Missing username or password"):
            assert_credentials()

    @patch.dict(os.environ, {}, clear=True)
    def test_assert_credentials_missing_both(self):
        """Test that assert_credentials raises an error
        when both credentials are missing.
        """
        with self.assertRaisesRegex(RuntimeError, "Missing username or password"):
            assert_credentials()


class TestAssertSuccess(TestPluginBase):
    """Tests for the assert_success function."""

    package = "q2_ena_uploader.tests"

    def test_assert_success_with_successful_response(self):
        """Test that assert_success doesn't issue a warning for
        a successful response.
        """
        # Create a mock response with success="true"
        mock_response = Mock(spec=requests.Response)
        mock_response.content = b'<RECEIPT success="true"></RECEIPT>'

        # This should not issue a warning
        with warnings.catch_warnings(record=True) as w:
            assert_success(mock_response)
            self.assertEqual(len(w), 0)

    def test_assert_success_with_unsuccessful_response(self):
        """Test that assert_success issues a warning for
        an unsuccessful response.
        """
        # Create a mock response with success="false" and an error message
        mock_response = Mock(spec=requests.Response)
        mock_response.content = (
            b'<RECEIPT success="false">'
            b"<ERROR>Authentication failed</ERROR>"
            b"</RECEIPT>"
        )

        with warnings.catch_warnings(record=True) as w:
            assert_success(mock_response)
            self.assertEqual(len(w), 1)
            self.assertIn("Authentication failed", str(w[0].message))

    def test_assert_success_with_unsuccessful_response_no_error_message(self):
        """Test assert_success with unsuccessful response but no error message."""
        # Create a mock response with success="false" but no error message
        mock_response = Mock(spec=requests.Response)
        mock_response.content = b'<RECEIPT success="false"></RECEIPT>'

        with warnings.catch_warnings(record=True) as w:
            assert_success(mock_response)
            self.assertEqual(len(w), 1)
            self.assertIn("Unable to parse ENA response", str(w[0].message))

    def test_assert_success_with_malformed_xml(self):
        """Test that assert_success handles malformed XML responses."""
        # Create a mock response with malformed XML
        mock_response = Mock(spec=requests.Response)
        mock_response.content = b"<RECEIPT>Malformed XML"

        with warnings.catch_warnings(record=True) as w:
            assert_success(mock_response)
            self.assertEqual(len(w), 1)
            self.assertIn("Unable to parse ENA response", str(w[0].message))


if __name__ == "__main__":
    unittest.main()
