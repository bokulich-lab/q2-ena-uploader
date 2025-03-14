# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import csv
import xml.etree.ElementTree as ET
from xml.etree import ElementTree

import pandas as pd
import q2_ena_uploader
import qiime2
from qiime2.plugin import SemanticType, model, ValidationError

from q2_ena_uploader.metadata.experiment import ExperimentSet
from q2_ena_uploader.metadata.sample import SampleSet
from q2_ena_uploader.metadata.study import Study

ENAMetadataSamples = SemanticType("ENAMetadataSamples")
ENAMetadataStudy = SemanticType("ENAMetadataStudy")
ENAMetadataExperiment = SemanticType("ENAMetadataExperiment")
ENASubmissionReceipt = SemanticType("ENASubmissionReceipt")


class ENAMetadataSamplesFormat(model.TextFileFormat):
    """ "
    This format is utilized to store ENA Samples submission metadata,
    including compulsary attributes such as alias and taxon_id,
    along with various other optional attributes for the samples submission.
    """

    REQUIRED_ATTRIBUTES = ["alias", "taxon_id"]

    def _validate(self):
        df = pd.read_csv(str(self), sep="\t")
        missing_cols = [x for x in self.REQUIRED_ATTRIBUTES if x not in df.columns]
        if missing_cols:
            raise ValidationError(
                "Some required sample attributes are missing from the metadata upload file: "
                f'{",".join(missing_cols)}.'
            )

        nans = (df.isnull() | (df == "")).sum(axis=0)[self.REQUIRED_ATTRIBUTES]
        missing_ids = nans.where(nans > 0).dropna().index.tolist()
        if missing_ids:
            raise ValidationError(
                "Some samples are missing values in the following fields: "
                f'{",".join(missing_ids)}.'
            )

    def _validate_(self, level):
        self._validate()

    def to_xml(self) -> bytes:
        with open(str(self), "r") as f:
            dicts = [d for d in csv.DictReader(f, delimiter="\t")]
            elementTree = SampleSet.from_list(dicts).to_xml_element()
            return ElementTree.tostring(elementTree.getroot(), encoding="utf8")


ENAMetadataSamplesDirFmt = model.SingleFileDirectoryFormat(
    "ENAMetadataSamplesDirFmt", "ena_metadata_samples.tsv", ENAMetadataSamplesFormat
)


def is_valid_value(x: object) -> bool:
    return not pd.isnull(x) and len(str(x).strip()) > 0


class ENAMetadataStudyFormat(model.TextFileFormat):
    """ "
    This format is utilized to store ENA Study submission metadata,
    including compulsary attributes such as alias and title,
    along with various other optional attributes for the study submission.
    """

    REQUIRED_ATTRIBUTES = ["alias", "title"]

    def _validate(self):
        df_dict = (
            pd.read_csv(str(self), header=None, index_col=0, sep="\t")
            .squeeze("columns")
            .to_dict()
        )
        missing_keys = [x for x in self.REQUIRED_ATTRIBUTES if x not in df_dict.keys()]
        if missing_keys:
            raise ValidationError(
                "Some required study attributes are missing from the metadata upload file: "
                f'{",".join(missing_keys)}.'
            )
        missing_values = [
            y for y in self.REQUIRED_ATTRIBUTES if not is_valid_value(df_dict[y])
        ]
        if len(missing_values) > 0:
            raise ValidationError(
                "The study is missing values in the following fields: "
                f'{",".join(missing_values)}.'
            )

    def to_xml(self) -> bytes:
        df = pd.read_csv(str(self), header=None, index_col=0, sep="\t")
        df.loc["project_attribute_uploader"] = {
            1: f"q2-ena-uploader|{q2_ena_uploader.__version__}"
        }
        df.loc["project_attribute_qiime2"] = {
            1: f"qiime2|{qiime2.__version__}"
        }
        df_dict = df.squeeze("columns").to_dict()
        elementTree = Study.from_dict(df_dict).to_xml_element()
        return ElementTree.tostring(elementTree.getroot(), encoding="utf8")

    def _validate_(self, level):
        self._validate()


ENAMetadataStudyDirFmt = model.SingleFileDirectoryFormat(
    "ENAMetadataStudyDirFmt", "ena_metadata_study.tsv", ENAMetadataStudyFormat
)


class ENASubmissionReceiptFormat(model.BinaryFileFormat):
    """
    This class provides a structured format to handle and inspect the receipt details
    following a data upload to the ENA.
    The success attribute indicates whether the submission was successful.
    The receipt also contains the accession numbers of the submitted objects.
    """

    @staticmethod
    def read_ET_from_file(filename: str) -> ET.Element:
        with open(filename, "r") as file:
            contents = file.read()
            return ET.fromstring(contents)

    def _validate(self):
        try:
            et = self.read_ET_from_file(str(self))
        except ET.ParseError:
            raise ValidationError("ENA receipt is not a valid xml form.")
        receipt_element = et
        required_att = ["receiptDate", "submissionFile", "success"]
        missing_att = [x for x in required_att if x not in receipt_element.attrib]
        if missing_att:
            raise ValidationError(
                "Xml response is missing values in the following fields: "
                f'{",".join(missing_att)}.'
            )

    def _validate_(self, level):
        return self._validate()


ENASubmissionReceiptDirFmt = model.SingleFileDirectoryFormat(
    "ENASubmissionReceiptDirFmt",
    "ena_submission_receipt.xml",
    ENASubmissionReceiptFormat,
)


class ENAMetadataExperimentFormat(model.TextFileFormat):
    """
    This format is utilized to store ENA Experiment submission metadata,
    including compulsory attributes such as alias, study and sample ids, platform and library description,
    along with various other optional attributes for the metadata submission.
    """

    REQUIRED_ATTRIBUTES = [
        "study_ref",
        "sample_description",
        "platform",
        "instrument_model",
        "library_strategy",
        "library_source",
        "library_selection",
        "library_layout",
    ]

    def _validate(self):
        df = pd.read_csv(str(self), sep="\t")
        missing_cols = [x for x in self.REQUIRED_ATTRIBUTES if x not in df.columns]
        if missing_cols:
            raise ValidationError(
                "Some required metadata attributes are missing from the metadata upload file: "
                f'{",".join(missing_cols)}.'
            )

        nans = (df.isnull() | (df == "")).sum(axis=0)[self.REQUIRED_ATTRIBUTES]
        missing_ids = nans.where(nans > 0).dropna().index.tolist()
        if missing_ids:
            raise ValidationError(
                "Some experiments are missing values in the following fields: "
                f'{",".join(missing_ids)}.'
            )

    def _validate_(self, level):
        self._validate()

    def to_xml(self) -> bytes:
        with open(str(self), "r") as f:
            dicts = [d for d in csv.DictReader(f, delimiter="\t")]
            element = ExperimentSet.from_list(dicts).to_xml_element()
            return ElementTree.tostring(element.getroot(), encoding="utf8")


ENAMetadataExperimentDirFmt = model.SingleFileDirectoryFormat(
    "ENAMetadataExperimentDirFmt",
    "ena_metadata_experiment.tsv",
    ENAMetadataExperimentFormat,
)
