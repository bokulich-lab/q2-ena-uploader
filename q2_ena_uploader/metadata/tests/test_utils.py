# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import xml.etree.ElementTree as ET

from lxml import etree


class CustomAssertions:
    """Custom assertion methods for XML comparisons."""

    def assert_xml_equal(self, xml1, xml2):
        """Assert that two XML trees are equal with detailed error messages.

        Parameters
        ----------
        xml1 : ElementTree
            First XML tree to compare
        xml2 : ElementTree
            Second XML tree to compare

        Raises
        ------
        AssertionError
            If the XML trees are not equal, with detailed diagnostics
        """
        # Convert ElementTree objects to strings
        xml_string1 = ET.tostring(xml1.getroot(), encoding="utf-8")
        xml_string2 = ET.tostring(xml2.getroot(), encoding="utf-8")

        # Parse strings with lxml to create lxml Elements
        lxml_element1 = etree.fromstring(xml_string1)
        lxml_element2 = etree.fromstring(xml_string2)

        # Compare serialized forms of the lxml Elements
        return etree.tostring(lxml_element1) == etree.tostring(lxml_element2)
