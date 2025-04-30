# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest
import xml.etree.ElementTree as ET

import pandas as pd
from parameterized import parameterized
from qiime2.plugin.testing import TestPluginBase

from q2_ena_uploader.metadata.study import Study
from q2_ena_uploader.metadata.tests.test_utils import CustomAssertions


def read_study_tsv_to_dict(filename):
    return (
        pd.read_csv(filename, header=None, index_col=0, delimiter="\t")
        .squeeze("columns")
        .to_dict()
    )


def get_test_cases():
    """Define the test cases for parameterized testing."""
    return [
        ("case0", 0),
        ("case1", 1),
        ("case2", 2),
        ("case3", 3),
        ("case4", 4),
    ]


class TestStudy(TestPluginBase, CustomAssertions):
    """Test the Study class and related functions."""

    package = "q2_ena_uploader.metadata.tests"

    def setUp(self):
        super().setUp()
        self.INPUT0 = read_study_tsv_to_dict(
            self.get_data_path("study/minimal_study_structure.tsv")
        )
        self.INPUT1 = read_study_tsv_to_dict(self.get_data_path("study/study1.tsv"))
        self.INPUT2 = read_study_tsv_to_dict(self.get_data_path("study/study2.tsv"))
        self.INPUT3 = read_study_tsv_to_dict(self.get_data_path("study/study3.tsv"))
        self.INPUT4 = read_study_tsv_to_dict(self.get_data_path("study/study4.tsv"))

        self.expected_xml_0 = ET.parse(self.get_data_path("study/minimal_study.xml"))
        self.expected_xml_1 = ET.parse(self.get_data_path("study/study1.xml"))
        self.expected_xml_2 = ET.parse(self.get_data_path("study/study2.xml"))
        self.expected_xml_3 = ET.parse(self.get_data_path("study/study3.xml"))
        self.expected_xml_4 = ET.parse(self.get_data_path("study/study4.xml"))

        self.inputs = [self.INPUT0, self.INPUT1, self.INPUT2, self.INPUT3, self.INPUT4]
        self.expected_xmls = [
            self.expected_xml_0,
            self.expected_xml_1,
            self.expected_xml_2,
            self.expected_xml_3,
            self.expected_xml_4,
        ]

    @parameterized.expand(get_test_cases())
    def test_xml_structure(self, name, index):
        """Test XML structure with parameterized test cases."""
        study = Study.from_dict(self.inputs[index])
        xml = study.to_xml_element()
        self.assert_xml_equal(xml, self.expected_xmls[index])


if __name__ == "__main__":
    unittest.main()
