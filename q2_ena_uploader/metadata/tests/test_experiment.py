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

from q2_ena_uploader.metadata.experiment import Experiment, ExperimentSet
from q2_ena_uploader.metadata.tests.test_utils import (
    CustomAssertions,
)


class TestExperiment(TestPluginBase, CustomAssertions):
    package = "q2_ena_uploader.metadata.tests"

    def setUp(self):
        super().setUp()
        self.experiment_data_path = self.get_data_path(
            "experiment/test_experiment1.tsv"
        )
        self.expected_xml_path = self.get_data_path("experiment/test_experiment1.xml")
        self.tsv_data = []
        with open(self.experiment_data_path, "r") as tsv_file:
            reader = csv.DictReader(tsv_file, delimiter="\t")
            for row in reader:
                self.tsv_data.append(row)

        self.expected_xml = ET.parse(self.expected_xml_path)

    def test_experiment_from_dict(self):
        """Test creating an Experiment object from a dictionary."""
        experiment = Experiment.from_dict(self.tsv_data[0])

        # Verify basic attributes
        self.assertEqual(experiment.title, "title12")
        self.assertEqual(experiment.study_ref, "study_ref1")
        self.assertEqual(experiment.sample_description, "sample_description1")
        self.assertEqual(experiment.platform, "ILLUMINA")
        self.assertEqual(experiment.instrument_model, "GENIUS")

        # Verify library attributes
        self.assertIsInstance(experiment.library_attributes, dict)
        self.assertIn("library_strategy", experiment.library_attributes)
        self.assertEqual(experiment.library_attributes["library_strategy"], "WGS")
        self.assertIn("library_source", experiment.library_attributes)
        self.assertEqual(experiment.library_attributes["library_source"], "GENOMIC")
        self.assertIn("library_selection", experiment.library_attributes)
        self.assertEqual(experiment.library_attributes["library_selection"], "RANDOM")
        self.assertIn("library_layout", experiment.library_attributes)
        self.assertEqual(experiment.library_attributes["library_layout"], "SINGLE")

    def test_experiment_to_xml_element(self):
        """Test converting an Experiment object to an XML element."""
        experiment = Experiment.from_dict(self.tsv_data[0])
        xml_element = experiment.to_xml_element()

        # Check basic structure of XML element
        self.assertEqual(xml_element.tag, "EXPERIMENT")
        self.assertEqual(xml_element.attrib["alias"], "exp_sample_description1")

        # Check title
        title_elem = xml_element.find("TITLE")
        self.assertIsNotNone(title_elem)
        self.assertEqual(title_elem.text, "title12")

        # Check study reference
        study_ref = xml_element.find("STUDY_REF")
        self.assertIsNotNone(study_ref)
        self.assertEqual(study_ref.attrib["refname"], "study_ref1")

        # Check sample descriptor
        design = xml_element.find("DESIGN")
        self.assertIsNotNone(design)
        sample_desc = design.find("SAMPLE_DESCRIPTOR")
        self.assertIsNotNone(sample_desc)
        self.assertEqual(sample_desc.attrib["refname"], "sample_description1")

        # Check platform
        platform = xml_element.find("PLATFORM")
        self.assertIsNotNone(platform)
        illumina = platform.find("ILLUMINA")
        self.assertIsNotNone(illumina)
        instrument = illumina.find("INSTRUMENT_MODEL")
        self.assertIsNotNone(instrument)
        self.assertEqual(instrument.text, "GENIUS")

    def test_experiment_set_from_list(self):
        """Test creating an ExperimentSet from a list of dictionaries."""
        experiment_set = ExperimentSet.from_list(self.tsv_data)

        # Verify the number of experiments
        self.assertEqual(len(experiment_set.experiments), 2)

        # Verify attributes of first experiment
        exp1 = experiment_set.experiments[0]
        self.assertEqual(exp1.title, "title12")
        self.assertEqual(exp1.study_ref, "study_ref1")

        # Verify attributes of second experiment
        exp2 = experiment_set.experiments[1]
        self.assertEqual(exp2.title, "title13")
        self.assertEqual(exp2.study_ref, "study_ref2")

    def test_experiment_set_to_xml_element(self):
        """Test converting ExperimentSet to XML tree and compare with expected."""
        experiment_set = ExperimentSet.from_list(self.tsv_data)
        xml_tree = experiment_set.to_xml_element()

        # Compare with expected XML
        self.assert_xml_equal(xml_tree, self.expected_xml)

    def test_experiment_set_empty(self):
        """Test creating an empty ExperimentSet."""
        experiment_set = ExperimentSet()

        # Verify the experiment set is empty
        self.assertEqual(len(experiment_set.experiments), 0)

        # Verify the XML is a valid ExperimentSet with no children
        xml_tree = experiment_set.to_xml_element()
        self.assertEqual(xml_tree.getroot().tag, "EXPERIMENT_SET")
        self.assertEqual(len(xml_tree.getroot()), 0)

    def test_experiment_library_attributes(self):
        """Test that library attributes are properly formatted in the XML."""
        experiment = Experiment.from_dict(self.tsv_data[0])
        xml_element = experiment.to_xml_element()

        # Check that design element exists
        design_element = xml_element.find("DESIGN")
        self.assertIsNotNone(design_element)

        # Check that library descriptor exists and has correct children
        library_descriptor = design_element.find("LIBRARY_DESCRIPTOR")
        self.assertIsNotNone(library_descriptor)

        # Check library strategy
        strategy = library_descriptor.find("LIBRARY_STRATEGY")
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.text, "WGS")

        # Check library source
        source = library_descriptor.find("LIBRARY_SOURCE")
        self.assertIsNotNone(source)
        self.assertEqual(source.text, "GENOMIC")

        # Check library selection
        selection = library_descriptor.find("LIBRARY_SELECTION")
        self.assertIsNotNone(selection)
        self.assertEqual(selection.text, "RANDOM")

        # Check library layout
        layout = library_descriptor.find("LIBRARY_LAYOUT")
        self.assertIsNotNone(layout)
        single = layout.find("SINGLE")
        self.assertIsNotNone(single)

    def test_experiment_missing_library_attributes(self):
        """Test ValueError when required library attributes are missing."""
        # Create a dictionary with missing library attributes
        invalid_data = self.tsv_data[0].copy()
        for field in [
            "library_strategy",
            "library_source",
            "library_selection",
            "library_layout",
        ]:
            invalid_data[field] = ""

        experiment = Experiment.from_dict(invalid_data)

        with self.assertRaisesRegex(
            ValueError, "Some of the library descriptors are empty"
        ):
            experiment.to_xml_element()

    def test_experiment_missing_platform(self):
        """Test that ValueError is raised when platform is missing."""
        # Create a dictionary with missing platform
        invalid_data = self.tsv_data[0].copy()
        invalid_data["platform"] = ""

        experiment = Experiment.from_dict(invalid_data)

        # The XML generation should complain about missing platform
        with self.assertRaisesRegex(ValueError, "Platform record must be present"):
            experiment.to_xml_element()

    def test_experiment_missing_instrument_model(self):
        """Test that ValueError is raised when instrument_model is missing."""
        # Create a dictionary with missing instrument_model
        invalid_data = self.tsv_data[0].copy()
        invalid_data["instrument_model"] = ""

        experiment = Experiment.from_dict(invalid_data)

        # The XML generation should complain about missing instrument_model
        with self.assertRaisesRegex(
            ValueError, "Instrument model record must be present"
        ):
            experiment.to_xml_element()


if __name__ == "__main__":
    unittest.main()
