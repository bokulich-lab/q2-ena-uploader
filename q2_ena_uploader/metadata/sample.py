# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import xml.etree.ElementTree as ET
from typing import List

from typing_extensions import Self


class Sample:
    def __init__(
        self,
        alias=None,
        center_name=None,
        title=None,
        taxon_id=None,
        scientific_name=None,
        common_name=None,
        description=None,
        url_links=[],
        xref_links=[],
        attributes=dict(),  # should contain ENA-CHECKLIST items
    ):
        self.alias = alias
        self.center_name = center_name
        self.title = title
        self.description = description
        self.taxon_id = taxon_id
        self.scientific_name = scientific_name
        self.common_name = common_name
        self.url_links = url_links
        self.xref_links = xref_links
        self.attributes = attributes

    def to_xml_element(self):
        if self.alias is None:
            raise ValueError("Sample alias must have a value for a sample submission.")
        elif self.center_name is None:
            sample_element = ET.Element("SAMPLE", {"alias": self.alias})
        else:
            sample_element = ET.Element(
                "SAMPLE", {"alias": self.alias, "center_name": self.center_name}
            )

        if self.title is not None:
            ET.SubElement(sample_element, "TITLE").text = self.title

        if self.taxon_id is None:
            raise ValueError(
                "Sample taxon id must have a value for a sample submission."
            )
        else:
            sample_name_element = ET.SubElement(sample_element, "SAMPLE_NAME")
            ET.SubElement(sample_name_element, "TAXON_ID").text = self.taxon_id
            if self.scientific_name is not None:
                ET.SubElement(sample_name_element, "SCIENTIFIC_NAME").text = (
                    self.scientific_name
                )
            if self.common_name is not None:
                ET.SubElement(sample_name_element, "COMMON_NAME").text = (
                    self.common_name
                )

        if self.description is not None:
            ET.SubElement(sample_element, "DESCRIPTION").text = self.description

        if len(self.url_links) > 0 or len(self.xref_links) > 0:
            links_element = ET.SubElement(sample_element, "SAMPLE_LINKS")
            if len(self.url_links) > 0:
                for link in self.url_links:
                    project_link_element = ET.SubElement(links_element, "SAMPLE_LINK")
                    url_link_element = ET.SubElement(project_link_element, "URL_LINK")
                    label, url = link.split("|")
                    ET.SubElement(url_link_element, "LABEL").text = label
                    ET.SubElement(url_link_element, "URL").text = url
            if len(self.xref_links) > 0:
                for link in self.xref_links:
                    project_link_element = ET.SubElement(links_element, "SAMPLE_LINK")
                    xref_link_element = ET.SubElement(project_link_element, "XREF_LINK")
                    db, id = link.split("|")
                    ET.SubElement(xref_link_element, "DB").text = db
                    ET.SubElement(xref_link_element, "ID").text = id

        if len(self.attributes) > 0:
            sample_atts_element = ET.SubElement(sample_element, "SAMPLE_ATTRIBUTES")
            for k, v in self.attributes.items():
                att_element = ET.SubElement(sample_atts_element, "SAMPLE_ATTRIBUTE")
                ET.SubElement(att_element, "TAG").text = k
                if "|" not in str(v):
                    ET.SubElement(att_element, "VALUE").text = v
                else:
                    value, units = v.split("|")
                    ET.SubElement(att_element, "VALUE").text = value
                    ET.SubElement(att_element, "UNITS").text = units

        return sample_element

    @classmethod
    def from_dict(cls, row_dict: dict) -> Self:
        special_attributes = {
            "alias",
            "center_name",
            "title",
            "taxon_id",
            "scientific_name",
            "common_name",
            "description",
        }
        kwargs = {
            k.strip(): v.strip()
            for k, v in row_dict.items()
            if k.strip() in special_attributes
        }
        kwargs["url_links"] = [
            v for k, v in row_dict.items() if k.startswith("url_link")
        ]
        kwargs["xref_links"] = [
            v for k, v in row_dict.items() if k.startswith("xref_link")
        ]
        kwargs["attributes"] = {
            k: v
            for k, v in row_dict.items()
            if k not in special_attributes
            and not k.startswith("url")
            and not k.startswith("xref")
        }
        return cls(**kwargs)


class SampleSet:
    def __init__(self):
        self.samples = []

    def add_sample(self, sample):
        self.samples.append(sample)

    def to_xml_element(self):
        sample_set_element = ET.Element("SAMPLE_SET")
        for sample in self.samples:
            sample_element = sample.to_xml_element()
            sample_set_element.append(sample_element)

        return ET.ElementTree(sample_set_element)

    @classmethod
    def from_list(cls, inputs: List[dict]) -> Self:
        sample_set = SampleSet()
        for row_dict in inputs:
            sample_set.add_sample(Sample.from_dict(row_dict))
        return sample_set
