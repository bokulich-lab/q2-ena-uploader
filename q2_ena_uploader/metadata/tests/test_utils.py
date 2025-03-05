# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import xml.etree.ElementTree as ET

from lxml import etree

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


# def fpath(fname):
#     """Return the full path to a test file."""
#     return os.path.join(THIS_DIR, fname)


def data_path(component, fname):
    """Return the full path to a data file in a specific component directory."""
    return os.path.join(THIS_DIR, "data", component, fname)


# def strip_whitespace(elem):
#     # Strip whitespace from the text and tail of the element
#     if hasattr(elem, 'text') and elem.text is not None:
#         elem.text = elem.text.strip()
#     if hasattr(elem, 'tail') and elem.tail is not None:
#         elem.tail = elem.tail.strip()
#     # Recursively apply to all child elements
#     for child in elem:
#         strip_whitespace(child)
#
#
# def elements_equal(e1, e2):
#     """Test if two XML elements are equal."""
#     if e1.tag != e2.tag:
#         return False
#     if e1.text != e2.text:
#         if e1.text and e2.text:
#             return False
#     if e1.tail != e2.tail:
#         if e1.tail and e2.tail:
#             return False
#     if e1.attrib != e2.attrib:
#         return False
#     if len(e1) != len(e2):
#         return False
#     result = all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))
#     return result
#
#
# def is_two_xml_equal(tree1, tree2):
#     """Test if two XML trees are equal."""
#     root1 = tree1.getroot()
#     root2 = tree2.getroot()
#     strip_whitespace(root1)
#     strip_whitespace(root2)
#     return elements_equal(root1, root2)


class CustomAssertions:
    """Custom assertion methods for XML comparisons."""

    def assert_xml_equal(self, xml1, xml2, context=""):
        """Assert that two XML trees are equal with detailed error messages.

        Parameters
        ----------
        xml1 : ElementTree
            First XML tree to compare
        xml2 : ElementTree
            Second XML tree to compare
        context : str, optional
            Additional context to include in error messages

        Raises
        ------
        AssertionError
            If the XML trees are not equal, with detailed diagnostics
        """
        # Convert ElementTree objects to strings
        xml_string1 = ET.tostring(xml1.getroot(), encoding='utf-8')
        xml_string2 = ET.tostring(xml2.getroot(), encoding='utf-8')

        # Parse strings with lxml to create lxml Elements
        lxml_element1 = etree.fromstring(xml_string1)
        lxml_element2 = etree.fromstring(xml_string2)

        # Compare serialized forms of the lxml Elements
        return etree.tostring(lxml_element1) == etree.tostring(lxml_element2)

        # if not is_two_xml_equal(xml1, xml2):
        #     # Build context prefix for error messages
        #     ctx_prefix = f"{context}: " if context else ""
        #
        #     # Provide detailed information about why the XMLs don't match
        #     root1 = xml1.getroot()
        #     root2 = xml2.getroot()
        #
        #     # Check if the root tag names match
        #     if root1.tag != root2.tag:
        #         raise AssertionError(
        #             f"{ctx_prefix}Root tag mismatch: {root1.tag} != {root2.tag}"
        #         )
        #
        #     # Check if number of children match
        #     if len(root1) != len(root2):
        #         raise AssertionError(
        #             f"{ctx_prefix}Number of children mismatch: "
        #             f"{len(root1)} != {len(root2)}"
        #         )
        #
        #     # For experiment sets, provide more detailed diagnostics
        #     if root1.tag == "EXPERIMENT_SET":
        #         for i, (exp1, exp2) in enumerate(zip(root1, root2)):
        #             # Check experiment attributes
        #             exp_attrs1 = exp1.find("EXPERIMENT_ATTRIBUTES")
        #             exp_attrs2 = exp2.find("EXPERIMENT_ATTRIBUTES")
        #
        #             if (exp_attrs1 is None) != (exp_attrs2 is None):
        #                 missing = "first" if exp_attrs1 is None else "second"
        #                 raise AssertionError(
        #                     f"{ctx_prefix}EXPERIMENT_ATTRIBUTES missing in {missing} "
        #                     f"XML for experiment {i}"
        #                 )
        #
        #             # If both have attributes, check if they match
        #             if exp_attrs1 is not None and exp_attrs2 is not None:
        #                 attrs1 = exp_attrs1.findall("EXPERIMENT_ATTRIBUTE")
        #                 attrs2 = exp_attrs2.findall("EXPERIMENT_ATTRIBUTE")
        #
        #                 if len(attrs1) != len(attrs2):
        #                     raise AssertionError(
        #                         f"{ctx_prefix}Number of attributes mismatch in "
        #                         f"experiment {i}: {len(attrs1)} != {len(attrs2)}"
        #                     )
        #
        #                 # Check individual attributes
        #                 for j, (attr1, attr2) in enumerate(zip(attrs1, attrs2)):
        #                     tag1 = attr1.find("TAG")
        #                     tag2 = attr2.find("TAG")
        #                     value1 = attr1.find("VALUE")
        #                     value2 = attr2.find("VALUE")
        #
        #                     if (
        #                         tag1 is not None
        #                         and tag2 is not None
        #                         and tag1.text != tag2.text
        #                     ):
        #                         raise AssertionError(
        #                             f"{ctx_prefix}TAG mismatch in experiment {i}, "
        #                             f"attribute {j}: {tag1.text} != {tag2.text}"
        #                         )
        #
        #                     if (
        #                         value1 is not None
        #                         and value2 is not None
        #                         and value1.text != value2.text
        #                     ):
        #                         raise AssertionError(
        #                             f"{ctx_prefix}VALUE mismatch in experiment {i}, "
        #                             f"attribute {j}: {value1.text} != {value2.text}"
        #                         )
        #
        #     # If we reach here, it's a more complex issue
        #     raise AssertionError(
        #         f"{ctx_prefix}XMLs don't match - there may be an issue with element "
        #         f"structure or attribute format"
        #     )
