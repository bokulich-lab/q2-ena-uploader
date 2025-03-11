# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import xml.etree.ElementTree as ET

from typing_extensions import Self


class Study:
    def __init__(
        self,
        alias=None,
        center_name=None,
        title=None,
        name=None,
        description=None,
        collaborators=[],
        url_links=[],
        xref_links=[],
        attributes=[],
    ):
        self.alias = alias
        self.center_name = center_name
        self.title = title
        self.name = name
        self.description = description
        self.collaborators = collaborators
        self.url_links = url_links
        self.xref_links = xref_links
        self.attributes = attributes

    def to_xml_element(self):

        root = ET.Element("PROJECT_SET")
        if self.alias is None:
            raise ValueError("Study alias must have a value for a study submission.")
        elif self.center_name is None:
            study_element = ET.SubElement(root, "PROJECT", {"alias": self.alias})
        else:
            study_element = ET.SubElement(
                root, "PROJECT", {"alias": self.alias, "center_name": self.center_name}
            )

        if self.name is not None:
            ET.SubElement(study_element, "NAME").text = str(self.name)

        if self.title is None:
            raise ValueError("Study title must have a value for a study submission.")
        else:
            ET.SubElement(study_element, "TITLE").text = str(self.title)

        if self.description is not None:
            ET.SubElement(study_element, "DESCRIPTION").text = str(self.description)

        if len(self.collaborators) > 0:
            collaborators_element = ET.SubElement(study_element, "COLLABORATORS")
            for el in self.collaborators:
                ET.SubElement(collaborators_element, "COLLABORATOR").text = str(el)

        submission_element = ET.SubElement(study_element, "SUBMISSION_PROJECT")
        ET.SubElement(submission_element, "SEQUENCING_PROJECT")

        if len(self.url_links) > 0 or len(self.xref_links) > 0:
            links_element = ET.SubElement(study_element, "PROJECT_LINKS")
            if len(self.url_links) > 0:
                for link in self.url_links:
                    project_link_element = ET.SubElement(links_element, "PROJECT_LINK")
                    url_link_element = ET.SubElement(project_link_element, "URL_LINK")
                    label, url = link.split("|")
                    ET.SubElement(url_link_element, "LABEL").text = label
                    ET.SubElement(url_link_element, "URL").text = url
            if len(self.xref_links) > 0:
                for link in self.xref_links:
                    project_link_element = ET.SubElement(links_element, "PROJECT_LINK")
                    xref_link_element = ET.SubElement(project_link_element, "XREF_LINK")
                    db, id = link.split("|")
                    ET.SubElement(xref_link_element, "DB").text = db
                    ET.SubElement(xref_link_element, "ID").text = id

        if len(self.attributes) > 0:
            attributes_element = ET.SubElement(study_element, "PROJECT_ATTRIBUTES")
            for el in self.attributes:
                tag, value = el.split("|")
                attribute_element = ET.SubElement(
                    attributes_element, "PROJECT_ATTRIBUTE"
                )
                ET.SubElement(attribute_element, "TAG").text = tag
                ET.SubElement(attribute_element, "VALUE").text = value

        tree = ET.ElementTree(root)
        return tree

    @classmethod
    def from_dict(cls, row_dict: dict) -> Self:
        special_attributes = {"alias", "title", "center_name", "name", "description"}
        kwargs = {
            k.strip(): v.strip()
            for k, v in row_dict.items()
            if k.strip() in special_attributes
        }
        kwargs["collaborators"] = [
            v for k, v in row_dict.items() if k.startswith("collaborator")
        ]
        kwargs["attributes"] = [
            v for k, v in row_dict.items() if k.startswith("project_attribute")
        ]
        kwargs["url_links"] = [
            v for k, v in row_dict.items() if k.startswith("url_link")
        ]
        kwargs["xref_links"] = [
            v for k, v in row_dict.items() if k.startswith("xref_link")
        ]
        return Study(**kwargs)
