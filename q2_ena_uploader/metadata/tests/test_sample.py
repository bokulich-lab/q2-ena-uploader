# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import csv
import unittest
import xml.etree.ElementTree as ET

from qiime2.plugin.testing import TestPluginBase

from q2_ena_uploader.metadata.sample import Sample, SampleSet
from q2_ena_uploader.metadata.tests.test_utils import (
    CustomAssertions,
)


class TestSample(TestPluginBase, CustomAssertions):
    """Test the Sample class and related functions."""

    package = "q2_ena_uploader.metadata.tests"

    def setUp(self):
        super().setUp()
        # Load test data
        self.sample1_xml_path = self.get_data_path("sample/test_sample1.xml")
        self.sample1_tsv_path = self.get_data_path("sample/test_sample1.tsv")

        # Parse the XML file
        self.sample1_xml = ET.parse(self.sample1_xml_path)

        # Read TSV data
        self.sample1_data = []
        with open(self.sample1_tsv_path, "r") as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter="\t")
            for row in reader:
                self.sample1_data.append(row)

    def test_sample_creation(self):
        """Test creating a Sample object."""
        # Create a basic sample
        sample = Sample(
            alias="test_sample",
            taxon_id="9606",  # Human
            scientific_name="Homo sapiens",
            attributes={
                "collection date": "2023-01-15",
                "geographic location (country and/or sea)": "United States",
            },
        )

        # Check attributes
        self.assertEqual(sample.alias, "test_sample")
        self.assertEqual(sample.taxon_id, "9606")
        self.assertEqual(sample.scientific_name, "Homo sapiens")
        self.assertEqual(len(sample.attributes), 2)
        self.assertEqual(sample.attributes["collection date"], "2023-01-15")

    def test_sample_to_xml_element(self):
        """Test converting a Sample to XML element."""
        # Create a sample with test data
        sample = Sample(
            alias="alias112",
            taxon_id="12",
            attributes={
                "geographic location (country and/or sea)": "Brazil",
                "collection date": "2022-02-02",
            },
        )

        # Convert to XML
        xml_element = sample.to_xml_element()

        # Check basic structure
        self.assertEqual(xml_element.tag, "SAMPLE")
        self.assertEqual(xml_element.attrib["alias"], "alias112")

        # Check taxon ID
        sample_name = xml_element.find("SAMPLE_NAME")
        self.assertIsNotNone(sample_name)
        taxon_id = sample_name.find("TAXON_ID")
        self.assertIsNotNone(taxon_id)
        self.assertEqual(taxon_id.text, "12")

        # Check attributes
        attributes = xml_element.find("SAMPLE_ATTRIBUTES")
        self.assertIsNotNone(attributes)

        attribute_elements = attributes.findall("SAMPLE_ATTRIBUTE")
        self.assertEqual(len(attribute_elements), 2)

        # Check first attribute
        tag1 = attribute_elements[0].find("TAG")
        value1 = attribute_elements[0].find("VALUE")
        self.assertIsNotNone(tag1)
        self.assertIsNotNone(value1)

        # The order might not be guaranteed, so we'll check both possibilities
        if tag1.text == "geographic location (country and/or sea)":
            self.assertEqual(value1.text, "Brazil")
            tag2 = attribute_elements[1].find("TAG")
            value2 = attribute_elements[1].find("VALUE")
            self.assertEqual(tag2.text, "collection date")
            self.assertEqual(value2.text, "2022-02-02")
        else:
            self.assertEqual(tag1.text, "collection date")
            self.assertEqual(value1.text, "2022-02-02")
            tag2 = attribute_elements[1].find("TAG")
            value2 = attribute_elements[1].find("VALUE")
            self.assertEqual(tag2.text, "geographic location (country and/or sea)")
            self.assertEqual(value2.text, "Brazil")

    def test_sample_from_dict(self):
        """Test creating a Sample from a dictionary."""
        # Create a sample from the first row of test data
        sample = Sample.from_dict(self.sample1_data[0])

        # Check attributes
        self.assertEqual(sample.alias, "alias112")
        self.assertEqual(sample.taxon_id, "12")
        self.assertIn("geographic location (country and/or sea)", sample.attributes)
        self.assertEqual(
            sample.attributes["geographic location (country and/or sea)"], "Brazil"
        )
        self.assertIn("collection date", sample.attributes)
        self.assertEqual(sample.attributes["collection date"], "2022-02-02")

    def test_sample_set(self):
        """Test SampleSet functionality."""
        # Create a sample set
        sample_set = SampleSet()

        # Create and add samples
        sample1 = Sample(
            alias="sample1",
            taxon_id="9606",
            attributes={"collection date": "2023-01-01"},
        )
        sample2 = Sample(
            alias="sample2",
            taxon_id="9606",
            attributes={"collection date": "2023-01-02"},
        )

        sample_set.add_sample(sample1)
        sample_set.add_sample(sample2)

        # Check sample count
        self.assertEqual(len(sample_set.samples), 2)

        # Convert to XML and check structure
        xml_tree = sample_set.to_xml_element()
        root = xml_tree.getroot()

        self.assertEqual(root.tag, "SAMPLE_SET")
        self.assertEqual(len(root), 2)

        # Check first sample
        first_sample = root[0]
        self.assertEqual(first_sample.attrib["alias"], "sample1")

    def test_sample_set_from_list_of_dicts(self):
        """Test creating a SampleSet from a list of dictionaries."""
        # Create a sample set from test data
        sample_set = SampleSet.from_list(self.sample1_data)

        # Convert to XML
        xml_tree = sample_set.to_xml_element()

        # Compare with expected XML
        self.assert_xml_equal(xml_tree, self.sample1_xml)


if __name__ == "__main__":
    unittest.main()
