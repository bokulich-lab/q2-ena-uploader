# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest
import xml.etree.ElementTree as ET

from qiime2.plugin.testing import TestPluginBase

from q2_ena_uploader.metadata.run import Run, _run_set_from_dict
from q2_ena_uploader.metadata.tests.test_utils import (
    CustomAssertions,
)


class TestRun(TestPluginBase, CustomAssertions):
    """Test the Run class."""

    package = "q2_ena_uploader.metadata.tests"

    def setUp(self):
        super().setUp()
        # Load test data
        self.run1_xml_path = self.get_data_path("run/run1.xml")
        self.run1_tsv_path = self.get_data_path("run/run1.tsv")

        # Parse the XML file
        self.run1_xml = ET.parse(self.run1_xml_path)

        # Read the TSV data
        self.run1_data = {}
        with open(self.run1_tsv_path, "r") as tsv_file:
            for line in tsv_file:
                if line.strip():  # Skip empty lines
                    key, value = line.strip().split("\t")
                    self.run1_data[key] = value

    def test_run_creation(self):
        """Test basic Run object creation."""
        # Create a run with basic information
        run = Run(
            alias="test_run",
            refname="test_experiment",
            files={
                "file1": {
                    "filename": "sample1.fastq",
                    "filetype": "fastq",
                    "checksum_method": "MD5",
                    "checksum": "abc123",
                }
            },
        )

        # Check attributes
        self.assertEqual(run.alias, "test_run")
        self.assertEqual(run.refname, "test_experiment")
        self.assertEqual(len(run.files), 1)
        self.assertIn("file1", run.files)

    def test_run_to_xml_element(self):
        """Test converting a Run to XML."""
        # Create a run with test data
        run = Run(
            alias="run1",
            refname="experiment_ref",
            files={
                "filename": ["filename1", "filename2"],
                "checksum": ["checksum1", "checksum2"],
            },
        )

        # Convert to XML element
        xml_element = run.to_xml_element()

        # Check basic structure
        self.assertEqual(xml_element.tag, "RUN")
        self.assertEqual(xml_element.attrib["alias"], "run1")

        # Check experiment reference
        exp_ref = xml_element.find("EXPERIMENT_REF")
        self.assertIsNotNone(exp_ref)
        self.assertEqual(exp_ref.attrib["refname"], "experiment_ref")

        # Check data block
        data_block = xml_element.find("DATA_BLOCK")
        self.assertIsNotNone(data_block)

        # Check files
        files_element = data_block.find("FILES")
        self.assertIsNotNone(files_element)

        file_elements = files_element.findall("FILE")
        self.assertEqual(len(file_elements), 2)

        # Check attributes of first file
        first_file = file_elements[0]
        self.assertEqual(first_file.attrib["filename"], "filename1")
        self.assertEqual(first_file.attrib["filetype"], "fastq")
        self.assertEqual(first_file.attrib["checksum_method"], "MD5")
        self.assertEqual(first_file.attrib["checksum"], "checksum1")

    def test_run_set_from_dict(self):
        """Test creating a run set XML from a dictionary."""
        # Create row dict for test
        row_dict = {
            "run1": {
                "experiment_ref": "experiment_ref",
                "filename": ["filename1", "filename2"],
                "checksum": ["checksum1", "checksum2"],
            }
        }

        # Generate XML
        xml_str = _run_set_from_dict(row_dict)

        # Parse the XML string
        xml_tree = ET.ElementTree(ET.fromstring(xml_str))

        # Parse the expected XML
        expected_xml = ET.parse(self.run1_xml_path)

        # Compare the XML structures
        self.assert_xml_equal(xml_tree, expected_xml)


if __name__ == "__main__":
    unittest.main()
