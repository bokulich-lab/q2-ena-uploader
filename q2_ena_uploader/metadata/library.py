# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from xml.etree import ElementTree


class Library:
    def __init__(
        self,
        library_strategy=None,
        library_source=None,
        library_selection=None,
        library_layout=None,
        library_nominal_length=None,
        library_nominal_sdev=None,
        library_construction_protocol=None,
    ):
        self.library_strategy = library_strategy
        self.library_source = library_source
        self.library_selection = library_selection
        self.library_layout = library_layout
        self.nominal_length = library_nominal_length
        self.nominal_sdev = library_nominal_sdev
        self.library_construction_protocol = library_construction_protocol

    def to_xml_element(self):
        if self.library_strategy is None:
            raise ValueError(
                "Library strategy must be present for an metadata submission."
            )
        else:
            root = ElementTree.Element("LIBRARY_DESCRIPTOR")
            ElementTree.SubElement(root, "LIBRARY_STRATEGY").text = str(
                self.library_strategy
            )

        if self.library_source is None:
            raise ValueError(
                "Library source must be present for an metadata submission."
            )
        else:
            ElementTree.SubElement(root, "LIBRARY_SOURCE").text = str(
                self.library_source
            )

        if self.library_selection is None:
            raise ValueError(
                "Library selection must be present for an metadata submission."
            )
        else:
            ElementTree.SubElement(root, "LIBRARY_SELECTION").text = str(
                self.library_selection
            )

        if self.library_layout is None:
            raise ValueError(
                "Library layout must be present for an metadata submission."
            )
        else:
            if self.library_layout.lower() == "paired":
                if self.nominal_length is None or self.nominal_sdev is None:
                    raise ValueError(
                        "Paired library layout requires nominal_length and "
                        "nominal_sdev values present for a metadata submission."
                    )
                else:
                    library_layout_el = ElementTree.SubElement(
                        root, "LIBRARY_LAYOUT"
                    )
                    ElementTree.SubElement(
                        library_layout_el,
                        "PAIRED",
                        {
                            "NOMINAL_LENGTH": self.nominal_length,
                            "NOMINAL_SDEV": self.nominal_sdev,
                        },
                    )
            else:
                library_layout_el = ElementTree.SubElement(root, "LIBRARY_LAYOUT")
                ElementTree.SubElement(library_layout_el, "SINGLE")

        if self.library_construction_protocol is not None:
            ElementTree.SubElement(root, "LIBRARY_CONSTRUCTION_PROTOCOL").text = str(
                self.library_construction_protocol
            )

        return root
