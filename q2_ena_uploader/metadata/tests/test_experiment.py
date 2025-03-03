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

from parameterized import parameterized
from q2_ena_uploader.metadata.experiment import ExperimentSet

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def fpath(fname):
    return os.path.join(THIS_DIR, fname)


def elements_equal(e1, e2):
    if e1.tag != e2.tag:
        return False
    if e1.text != e2.text:
        if e1.text != None and e2.text != None:
            return False
    if e1.tail != e2.tail:
        if e1.tail != None and e2.tail != None:
            return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))


def is_two_xml_equal(tree1, tree2):
    root1 = tree1.getroot()
    root2 = tree2.getroot()
    return elements_equal(root1, root2)


class CustomAssertions:
    def assertXmlEqual(self, xml1, xml2):
        if not is_two_xml_equal(xml1, xml2):
            raise AssertionError("Two xml files are not equal!")


if __name__ == "__main__":
    unittest.main()
