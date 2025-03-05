# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from typing import List
from xml.etree import ElementTree

from typing_extensions import Self

from q2_ena_uploader.metadata.library import Library


class Experiment:
    def __init__(
        self,
        title=None,
        study_ref=None,
        sample_description=None,
        platform=None,
        instrument_model=None,
        library_attributes=None,
        attributes=None,
    ):
        self.title = title
        self.study_ref = study_ref
        self.sample_description = sample_description
        self.platform = platform
        self.instrument_model = instrument_model
        self.library_attributes = library_attributes if library_attributes else {}
        self.attributes = attributes if attributes else []

    def to_xml_element(self):
        if self.sample_description:
            root = ElementTree.Element(
                "EXPERIMENT", {"alias": "exp_" + str(self.sample_description)}
            )
        else:
            raise ValueError(
                "Sample reference id must be present for an metadata submission."
            )

        if self.title:
            ElementTree.SubElement(root, "TITLE").text = str(self.title)

        if self.study_ref:
            study_element = ElementTree.SubElement(
                root, "STUDY_REF", {"refname": self.study_ref}
            )
        else:
            raise ValueError(
                "Study reference must be present for an metadata submission."
            )

        design_element = ElementTree.SubElement(root, "DESIGN")
        design_description_element = ElementTree.SubElement(
            design_element, "DESIGN_DESCRIPTION"
        )

        sample_description = ElementTree.SubElement(
            design_element, "SAMPLE_DESCRIPTOR", {"refname": self.sample_description}
        )

        if self.platform:
            if not self.instrument_model:
                raise ValueError(
                    "Instrument model record must be present for an metadata submission."
                )
            else:
                platform_el = ElementTree.SubElement(root, "PLATFORM")
                platform_model = ElementTree.SubElement(
                    platform_el, self.platform.upper()
                )
                ElementTree.SubElement(platform_model, "INSTRUMENT_MODEL").text = (
                    self.instrument_model
                )
        else:
            raise ValueError(
                "Platform record must be present for an metadata submission."
            )

        if len(self.library_attributes) == 0:
            raise ValueError(
                "Library descriptors must be present for an metadata submission."
            )
        elif all([not v for k, v in self.library_attributes.items()]):
            raise ValueError(
                "Some of the library descriptors are empty. Please provide values for all library descriptors."
            )
        else:
            library_tree = Library(**self.library_attributes)
            library_tree_element = library_tree.to_xml_element()
            design_element.append(library_tree_element)

        if len(self.attributes) > 0:
            attributes_element = ElementTree.SubElement(root, "EXPERIMENT_ATTRIBUTES")
            for el in self.attributes:
                tag, value = el.split("|")
                attribute_element = ElementTree.SubElement(
                    attributes_element, "EXPERIMENT_ATTRIBUTE"
                )
                ElementTree.SubElement(attribute_element, "TAG").text = tag
                ElementTree.SubElement(attribute_element, "VALUE").text = value

        return root

    @classmethod
    def from_dict(cls, row_dict: dict) -> Self:
        special_attributes = {
            "title",
            "study_ref",
            "sample_description",
            "platform",
            "instrument_model",
        }
        kwargs = {
            k.strip(): v.strip()
            for k, v in row_dict.items()
            if k.strip() in special_attributes
        }
        kwargs["library_attributes"] = {
            k: v for k, v in row_dict.items() if k.startswith("library")
        }
        kwargs["attributes"] = [
            v
            for k, v in row_dict.items()
            if k not in special_attributes and k.startswith("exp_attribute")
        ]
        return cls(**kwargs)


class ExperimentSet:
    def __init__(self):
        self.experiments = []

    def add_experiment(self, experiment):
        self.experiments.append(experiment)

    def to_xml_element(self):
        experiment_set_element = ElementTree.Element("EXPERIMENT_SET")
        for experiment in self.experiments:
            experiment_element = experiment.to_xml_element()
            experiment_set_element.append(experiment_element)

        return ElementTree.ElementTree(experiment_set_element)

    @classmethod
    def from_list(cls, inputs: List[dict]) -> Self:
        experiment_set = ExperimentSet()
        for row_dict in inputs:
            experiment_set.add_experiment(Experiment.from_dict(row_dict))
        return experiment_set
