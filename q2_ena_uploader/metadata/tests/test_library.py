# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.plugin.testing import TestPluginBase

from q2_ena_uploader.metadata.library import Library
from q2_ena_uploader.metadata.tests.test_utils import CustomAssertions


class TestLibrary(TestPluginBase, CustomAssertions):
    """Test the Library class."""

    package = "q2_ena_uploader.metadata.tests"

    def test_library_single_layout(self):
        """Test creating a Library with SINGLE layout."""
        # Create a library with single layout
        library = Library(
            library_strategy="WGS",
            library_source="GENOMIC",
            library_selection="RANDOM",
            library_layout="SINGLE",
            library_construction_protocol="Standard protocol",
        )

        # Convert to XML
        xml_element = library.to_xml_element()

        # Check basic structure
        self.assertEqual(xml_element.tag, "LIBRARY_DESCRIPTOR")

        # Check strategy
        strategy = xml_element.find("LIBRARY_STRATEGY")
        self.assertIsNotNone(strategy)
        self.assertEqual(strategy.text, "WGS")

        # Check source
        source = xml_element.find("LIBRARY_SOURCE")
        self.assertIsNotNone(source)
        self.assertEqual(source.text, "GENOMIC")

        # Check selection
        selection = xml_element.find("LIBRARY_SELECTION")
        self.assertIsNotNone(selection)
        self.assertEqual(selection.text, "RANDOM")

        # Check layout
        layout = xml_element.find("LIBRARY_LAYOUT")
        self.assertIsNotNone(layout)
        single = layout.find("SINGLE")
        self.assertIsNotNone(single)

        # Check construction protocol
        protocol = xml_element.find("LIBRARY_CONSTRUCTION_PROTOCOL")
        self.assertIsNotNone(protocol)
        self.assertEqual(protocol.text, "Standard protocol")

    def test_library_paired_layout(self):
        """Test creating a Library with PAIRED layout."""
        # Create a library with paired layout
        library = Library(
            library_strategy="WGS",
            library_source="GENOMIC",
            library_selection="RANDOM",
            library_layout="PAIRED",
            library_nominal_length="300",
            library_nominal_sdev="30",
            library_construction_protocol="Standard paired protocol",
        )

        # Convert to XML
        xml_element = library.to_xml_element()

        # Check basic structure
        self.assertEqual(xml_element.tag, "LIBRARY_DESCRIPTOR")

        # Check layout
        layout = xml_element.find("LIBRARY_LAYOUT")
        self.assertIsNotNone(layout)
        paired = layout.find("PAIRED")
        self.assertIsNotNone(paired)

        # Check paired attributes
        self.assertEqual(paired.attrib["NOMINAL_LENGTH"], "300")
        self.assertEqual(paired.attrib["NOMINAL_SDEV"], "30")

    def test_library_missing_strategy(self):
        """Test that ValueError is raised when library_strategy is missing."""
        library = Library(
            library_source="GENOMIC",
            library_selection="RANDOM",
            library_layout="SINGLE",
        )

        with self.assertRaisesRegex(
            ValueError,
            "Library strategy must be present",
        ):
            library.to_xml_element()

    def test_library_missing_source(self):
        """Test that ValueError is raised when library_source is missing."""
        library = Library(
            library_strategy="WGS", library_selection="RANDOM", library_layout="SINGLE"
        )

        with self.assertRaisesRegex(ValueError, "Library source must be present"):
            library.to_xml_element()

    def test_library_missing_selection(self):
        """Test that ValueError is raised when library_selection is missing."""
        library = Library(
            library_strategy="WGS", library_source="GENOMIC", library_layout="SINGLE"
        )

        with self.assertRaisesRegex(ValueError, "Library selection must be present"):
            library.to_xml_element()

    def test_library_missing_layout(self):
        """Test that ValueError is raised when library_layout is missing."""
        library = Library(
            library_strategy="WGS", library_source="GENOMIC", library_selection="RANDOM"
        )

        with self.assertRaisesRegex(ValueError, "Library layout must be present"):
            library.to_xml_element()

    def test_paired_without_nominal_values(self):
        """Test that paired layout works without nominal values ."""
        library = Library(
            library_strategy="WGS",
            library_source="GENOMIC",
            library_selection="RANDOM",
            library_layout="PAIRED",
        )

        xml_element = library.to_xml_element()
        layout = xml_element.find("LIBRARY_LAYOUT")
        self.assertIsNotNone(layout)
        self.assertEqual(layout[0].tag, "PAIRED")
        paired = layout.find("PAIRED")
        self.assertIsNotNone(paired)
        self.assertEqual(paired.tag, "PAIRED")
        self.assertEqual(len(paired.attrib), 0)
        self.assertIsNone(paired.text)

    def test_no_construction_protocol(self):
        """Test that construction protocol is optional."""
        library = Library(
            library_strategy="WGS",
            library_source="GENOMIC",
            library_selection="RANDOM",
            library_layout="SINGLE",
        )

        xml_element = library.to_xml_element()
        protocol = xml_element.find("LIBRARY_CONSTRUCTION_PROTOCOL")

        # Protocol node should not exist if not provided
        self.assertIsNone(protocol)

    def test_paired_with_only_nominal_length(self):
        """Test paired layout with only NOMINAL_LENGTH (NOMINAL_SDEV optional)."""
        library = Library(
            library_strategy="WGS",
            library_source="GENOMIC",
            library_selection="RANDOM",
            library_layout="PAIRED",
            library_nominal_length="300",
        )

        xml_element = library.to_xml_element()
        layout = xml_element.find("LIBRARY_LAYOUT")
        paired = layout.find("PAIRED")

        # Should have NOMINAL_LENGTH but not NOMINAL_SDEV
        self.assertEqual(paired.attrib["NOMINAL_LENGTH"], "300")
        self.assertNotIn("NOMINAL_SDEV", paired.attrib)

    def test_nominal_sdev_without_nominal_length(self):
        """Test that NOMINAL_SDEV without NOMINAL_LENGTH issues a warning
        and is ignored."""
        library = Library(
            library_strategy="WGS",
            library_source="GENOMIC",
            library_selection="RANDOM",
            library_layout="PAIRED",
            library_nominal_sdev="30",
        )

        with self.assertWarns(
            UserWarning,
            msg=(
                "Nominal_sdev can only be provided when nominal_length "
                "is also present. The nominal_sdev will be ignored."
            ),
        ):
            library.to_xml_element()


if __name__ == "__main__":
    unittest.main()
