# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from xml.etree import ElementTree


class Run:
    def __init__(self, alias, refname, files=None):
        self.alias = alias
        self.refname = refname
        self.files = files if files is not None else {}

    def to_xml_element(self):
        run_element = ElementTree.Element("RUN", {"alias": self.alias})
        ElementTree.SubElement(run_element, "EXPERIMENT_REF", {"refname": self.refname})
        data_block = ElementTree.SubElement(run_element, "DATA_BLOCK")
        files_element = ElementTree.SubElement(data_block, "FILES")

        for filename, checksum in zip(self.files["filename"], self.files["checksum"]):
            ElementTree.SubElement(
                files_element,
                "FILE",
                {
                    "filename": filename,
                    "filetype": "fastq",
                    "checksum_method": "MD5",
                    "checksum": checksum,
                },
            )

        ElementTree.ElementTree(run_element)
        return run_element


def _run_set_from_dict(row_dict) -> bytes:
    run_set_root = ElementTree.Element("RUN_SET")
    kwargs = {}
    xml_bytes = None
    for alias in row_dict:
        kwargs["alias"] = "run_" + alias
        kwargs["refname"] = "exp_" + alias
        kwargs["files"] = row_dict[alias]
        run_element = Run(**kwargs)
        run_set_root.append(run_element.to_xml_element())
        xml_bytes = ElementTree.tostring(
            run_set_root, encoding="utf-8", xml_declaration=True
        )

    return xml_bytes
