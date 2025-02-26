# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from qiime2.core.type import Choices
from qiime2.plugin import Plugin
from q2_types.metadata import ImmutableMetadata
from qiime2.plugin import Str, Bool

import q2_ena_uploader
from q2_ena_uploader.types._types_and_formats import (
    ENAMetadataSamplesFormat,
    ENAMetadataSamplesDirFmt,
    ENAMetadataSamples,
    ENAMetadataStudyFormat,
    ENAMetadataStudyDirFmt,
    ENAMetadataStudy,
    ENASubmissionReceiptFormat,
    ENASubmissionReceiptDirFmt,
    ENASubmissionReceipt,
    ENAMetadataExperimentFormat,
    ENAMetadataExperiment,
    ENAMetadataExperimentDirFmt,
)
from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (
    SequencesWithQuality,
    PairedEndSequencesWithQuality,
)
from q2_ena_uploader.uploader import submit_metadata_samples, cancel_submission
from q2_ena_uploader.experiment_upload import submit_metadata_reads
from q2_ena_uploader.ftp_file_upload import transfer_files_to_ena

plugin = Plugin(
    name="ena-uploader",
    version=q2_ena_uploader.__version__,
    website="https://github.com/bokulich-lab/q2-ena-uploader",
    package="q2_ena_uploader",
    description=(
        "This is a QIIME2 plugin supporting upload of the metadata and raw data files to ENA."
    ),
    short_description="Plugin for data upload to ENA.",
)

plugin.methods.register_function(
    function=submit_metadata_samples,
    inputs={
        "study": ENAMetadataStudy,
        "samples": ENAMetadataSamples,
    },
    parameters={"submission_hold_date": Str, "dev": Bool, "action_type": Str % Choices(["ADD", "MODIFY"])},
    outputs=[("submission_receipt", ENASubmissionReceipt)],
    input_descriptions={
        "study": "Study submission parameters.",
        "samples": "Submission metadata of the samples.",
    },
    parameter_descriptions={
        "submission_hold_date": "The release date of the study, on which it will become public along with all submitted data.",
        "dev": "Set to True in case of submission to ENA development server (for testing).",
    },
    output_descriptions={
        "submission_receipt": "Submission summary."
    },
    name="Submit sample and/or study metadata to ENA.",
    description="ENA Study and Samples metadata submission.",
    citations=[],
)


plugin.methods.register_function(
    function=cancel_submission,
    inputs={},
    parameters={"accession_number": Str, "dev": Bool},
    outputs=[("submission_receipt", ENASubmissionReceipt)],
    input_descriptions={},
    parameter_descriptions={
        "accession_number": "ENA unique identifier of  the object that is being cancelled.",
        "dev": "Set to True in case of submission to ENA development server (for testing).",
    },
    output_descriptions={
        "submission_receipt": "Submission summary."
    },
    name="Cancel ENA submission.",
    description="Cancellation of the ENA submission.",
    citations=[],
)


plugin.methods.register_function(
    function=submit_metadata_reads,
    inputs={
        "demux": SampleData[SequencesWithQuality | PairedEndSequencesWithQuality],
        "experiment": ENAMetadataExperiment,
    },
    parameters={"submission_hold_date": Str, "action_type": Str % Choices(["ADD", "MODIFY"]), "dev": Bool},
    outputs=[("submission_receipt", ENASubmissionReceipt)],
    input_descriptions={
        "demux": "The demultiplexed sequencing data, either single-end or paired-end reads.",
        "experiment": "Experiment submission parameters.",
    },
    parameter_descriptions={
        "submission_hold_date": "The release date of the study, on which it will become public along with all submitted data.",
        "action_type": "Type of action to perform.",
        "dev": "Set to True when submitting to the ENA development server (for testing).",
    },
    output_descriptions={
        "submission_receipt": "An artifact containing the ENA submission receipt and assigned accession numbers."
    },
    name="Submit raw reads metadata to ENA.",
    description="Submit raw reads and associated metadata to the ENA.",
    citations=[],
)

plugin.methods.register_function(
    function=transfer_files_to_ena,
    inputs={"demux": SampleData[SequencesWithQuality | PairedEndSequencesWithQuality]},
    parameters={"action": Str % Choices(["ADD", "DELETE"])},
    outputs=[("metadata", ImmutableMetadata)],
    input_descriptions={
        "demux": "The demultiplexed sequencing data, either single-end or paired-end reads."
    },
    parameter_descriptions={
        "action": "Type of action to perform. Use ADD for uploading files to the ENA FTP server. Use DELETE to remove files."
    },
    output_descriptions={
        "metadata": "Status of the file transfer or deletion operation."
    },
    name="Transfer raw reads files to the ENA FTP server.",
    description="Transfer or delete raw reads files to/from the ENA FTP server.",
    citations=[],
)

plugin.register_semantic_types(
    ENAMetadataStudy, ENAMetadataSamples, ENAMetadataExperiment, ENASubmissionReceipt
)

plugin.register_formats(
    ENAMetadataSamplesFormat,
    ENAMetadataStudyFormat,
    ENAMetadataSamplesDirFmt,
    ENAMetadataStudyDirFmt,
    ENASubmissionReceiptFormat,
    ENASubmissionReceiptDirFmt,
    ENAMetadataExperimentFormat,
    ENAMetadataExperimentDirFmt,
)


plugin.register_artifact_class(
    ENAMetadataStudy, ENAMetadataStudyDirFmt, description="Study submission tsv file."
)

plugin.register_artifact_class(
    ENAMetadataSamples,
    ENAMetadataSamplesDirFmt,
    description="Samples submission tsv file.",
)

plugin.register_artifact_class(
    ENASubmissionReceipt,
    ENASubmissionReceiptDirFmt,
    description="ENA submission receipt xml file",
)

plugin.register_artifact_class(
    ENAMetadataExperiment,
    ENAMetadataExperimentDirFmt,
    description="Experiment submission tsv file.",
)

importlib.import_module("q2_ena_uploader.types._transformer")
