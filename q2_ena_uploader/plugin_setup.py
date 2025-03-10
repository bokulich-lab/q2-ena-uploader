# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

from q2_types.metadata import ImmutableMetadata
from q2_types.per_sample_sequences import (
    SequencesWithQuality,
    PairedEndSequencesWithQuality,
)
from q2_types.sample_data import SampleData
from qiime2.core.type import Choices
from qiime2.plugin import Plugin
from qiime2.plugin import Str, Bool

import q2_ena_uploader
from q2_ena_uploader import submit_all
from q2_ena_uploader.ftp_file_upload import transfer_files_to_ena
from q2_ena_uploader.read_submission import submit_metadata_reads
from q2_ena_uploader.sample_submission import submit_metadata_samples, cancel_submission
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

plugin = Plugin(
    name="ena-uploader",
    version=q2_ena_uploader.__version__,
    website="https://github.com/bokulich-lab/q2-ena-uploader",
    package="q2_ena_uploader",
    description=(
        "QIIME2 plugin for submitting metadata and raw data files to the "
        "European Nucleotide Archive (ENA)."
    ),
    short_description="Plugin for data upload to ENA.",
)

plugin.methods.register_function(
    function=submit_metadata_samples,
    inputs={
        "study": ENAMetadataStudy,
        "samples": ENAMetadataSamples,
    },
    parameters={
        "submission_hold_date": Str,
        "dev": Bool,
        "action": Str % Choices(["ADD", "MODIFY"]),
    },
    outputs=[("submission_receipt", ENASubmissionReceipt)],
    input_descriptions={
        "study": "Study metadata in ENA-compatible format.",
        "samples": "Sample metadata in ENA-compatible format.",
    },
    parameter_descriptions={
        "submission_hold_date": "Release date when the study and associated data "
        "will become publicly available (format: YYYY-MM-DD).",
        "dev": "Set to True to submit to the ENA development server for testing.",
        "action": "Submission action type (ADD for new data, MODIFY for updating existing data).",
    },
    output_descriptions={
        "submission_receipt": "Receipt containing submission details and accession numbers."
    },
    name="Submit sample and/or study metadata to ENA.",
    description="Submit study and sample metadata to the European Nucleotide Archive.",
    citations=[],
)


plugin.methods.register_function(
    function=cancel_submission,
    inputs={},
    parameters={"accession_number": Str, "dev": Bool},
    outputs=[("submission_receipt", ENASubmissionReceipt)],
    input_descriptions={},
    parameter_descriptions={
        "accession_number": "ENA accession number of the submission to cancel.",
        "dev": "Set to True to use the ENA development server for testing.",
    },
    output_descriptions={
        "submission_receipt": "Receipt containing details of the cancellation."
    },
    name="Cancel ENA submission.",
    description="Cancel an existing submission to the European Nucleotide Archive.",
    citations=[],
)


plugin.methods.register_function(
    function=submit_metadata_reads,
    inputs={
        "demux": SampleData[SequencesWithQuality | PairedEndSequencesWithQuality],
        "experiment": ENAMetadataExperiment,
        "samples_submission_receipt": ENASubmissionReceipt,
        "file_transfer_metadata": ImmutableMetadata,
    },
    parameters={
        "submission_hold_date": Str,
        "action": Str % Choices(["ADD", "MODIFY"]),
        "dev": Bool,
    },
    outputs=[("submission_receipt", ENASubmissionReceipt)],
    input_descriptions={
        "demux": "Demultiplexed sequence data (single-end or paired-end reads).",
        "experiment": "Experiment metadata in ENA-compatible format.",
        "samples_submission_receipt": "Receipt from the sample/study submission.",
        "file_transfer_metadata": "Metadata from the file transfer operation.",
    },
    parameter_descriptions={
        "submission_hold_date": "Release date when the data will become publicly available "
        "(format: YYYY-MM-DD).",
        "action": "Submission action type (ADD for new data, MODIFY for updating existing data).",
        "dev": "Set to True to use the ENA development server for testing.",
    },
    output_descriptions={
        "submission_receipt": "Receipt containing submission details and assigned ENA accession numbers."
    },
    name="Submit raw reads metadata to ENA.",
    description="Submit experiment metadata and raw reads information to the European Nucleotide Archive.",
    citations=[],
)

plugin.methods.register_function(
    function=transfer_files_to_ena,
    inputs={"demux": SampleData[SequencesWithQuality | PairedEndSequencesWithQuality]},
    parameters={"action": Str % Choices(["ADD", "DELETE"])},
    outputs=[("metadata", ImmutableMetadata)],
    input_descriptions={
        "demux": "Demultiplexed sequence data (single-end or paired-end reads)."
    },
    parameter_descriptions={
        "action": "Action type: ADD to upload files to the ENA FTP server, "
        "DELETE to remove previously uploaded files."
    },
    output_descriptions={
        "metadata": "Status report of the file transfer or deletion operation."
    },
    name="Transfer raw reads files to the ENA FTP server.",
    description="Upload sequence files to or delete sequence files from the ENA FTP server.",
    citations=[],
)

plugin.pipelines.register_function(
    function=submit_all,
    inputs={
        "demux": SampleData[SequencesWithQuality | PairedEndSequencesWithQuality],
        "study": ENAMetadataStudy,
        "samples": ENAMetadataSamples,
        "experiment": ENAMetadataExperiment,
    },
    parameters={
        "submission_hold_date": Str,
        "dev": Bool,
        "action": Str % Choices(["ADD", "MODIFY"]),
    },
    outputs=[
        ("sample_submission_receipt", ENASubmissionReceipt),
        ("read_submission_receipt", ENASubmissionReceipt),
        ("file_upload_metadata", ImmutableMetadata),
    ],
    input_descriptions={
        "demux": "Demultiplexed sequence data (single-end or paired-end reads).",
        "study": "Study metadata in ENA-compatible format.",
        "samples": "Sample metadata in ENA-compatible format.",
        "experiment": "Experiment metadata in ENA-compatible format.",
    },
    parameter_descriptions={
        "submission_hold_date": "Release date when the study and associated data "
        "will become publicly available (format: YYYY-MM-DD).",
        "dev": "Set to True to submit to the ENA development server for testing.",
        "action": "Submission action type (ADD for new data, MODIFY for updating existing data).",
    },
    output_descriptions={
        "sample_submission_receipt": "Receipt containing sample/study submission details and assigned ENA accession numbers.",
        "read_submission_receipt": "Receipt containing read metadata submission details and accession numbers.",
        "file_upload_metadata": "Status report of the file transfer operation.",
    },
    name="Submit sample/study metadata and raw reads to ENA.",
    description="Submit study and sample metadata together with raw reads to the European Nucleotide Archive.",
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
