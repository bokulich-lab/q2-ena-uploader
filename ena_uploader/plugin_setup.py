import importlib
from qiime2.plugin import Plugin
from qiime2.plugin import Str, Bool
from q2_types.ordination import PCoAResults
from ena_uploader.types._types_and_formats import (
    ENAMetadataSamplesFormat, ENAMetadataSamplesDirFmt,ENAMetadataSamples,
    ENAMetadataStudyFormat, ENAMetadataStudyDirFmt, ENAMetadataStudy,
    ENASubmissionReceiptFormat,ENASubmissionReceiptDirFmt,ENASubmissionReceipt,
    ENAMetadataExperimentFormat,ENAMetadataExperiment,ENAMetadataExperimentDirFmt

)
from ena_uploader.uploader import uploadToEna, cancleENASubmission

plugin = Plugin(
    name='ena_uploader',
    version='1.0',
    website='https://github.com/TBD',
    package='ena_uploader',
    description=('This is a QIIME2 plugin supporting upload of the metadata and raw data files to ENA.'),
    short_description='Plugin for data upload to ENA.',
)


plugin.register_semantic_types(ENAMetadataStudy,ENAMetadataSamples,ENAMetadataExperiment,ENASubmissionReceipt)

plugin.register_formats(
    ENAMetadataSamplesFormat,ENAMetadataStudyFormat,
    ENAMetadataSamplesDirFmt,ENAMetadataStudyDirFmt,
    ENASubmissionReceiptFormat,ENASubmissionReceiptDirFmt,
    ENAMetadataExperimentFormat,ENAMetadataExperimentDirFmt
)


plugin.register_artifact_class(ENAMetadataStudy,
                               ENAMetadataStudyDirFmt,
                               description = "Study submission tsv file."

)

plugin.register_artifact_class(ENAMetadataSamples,
                               ENAMetadataSamplesDirFmt,
                               description = "Samples submission tsv file."

)

plugin.register_artifact_class(ENASubmissionReceipt,
                               ENASubmissionReceiptDirFmt,
                               description = "ENA submission receipt xml file")

plugin.register_artifact_class(ENAMetadataExperiment,
                               ENAMetadataExperimentDirFmt,
                               description = "Experiment submission tsv file."
)

plugin.methods.register_function(
    function=uploadToEna,
    inputs = {
            'study': ENAMetadataStudy,
            'samples': ENAMetadataSamples,
            },
    parameters={
            'submission_hold_date': Str,
            'dev' : Bool,
            'action_type': Str
            },
    outputs=[('submission_receipt', ENASubmissionReceipt)],
    
    input_descriptions={
            'study': 'Artifact containing study submission parameters.',
            'samples': 'Artifact containing submission metadata of the samples.',
            },
    parameter_descriptions={
        'submission_hold_date':"The release date of the study, on which it will become public along with all submitted data.",
        'dev' : ('False by default, true in case of submission to ENA dev server.')
    },
    output_descriptions={
        'submission_receipt': 'Artifact containing the submission summary.'
    },
    name='ENA Submission',
    description=("ENA Study and Samples Metadata submission upload."),
    citations=[]
)


plugin.methods.register_function(
    function=cancleENASubmission,
    inputs = {},
    parameters={
            'accession_number' : Str,
            'dev' : Bool
            },
    outputs=[('submission_receipt', ENASubmissionReceipt)],
    
    input_descriptions= {},
    parameter_descriptions={
        'accession_number': "ENA unique identifier of  the object that is being cancelled.",
        'dev' : ('False by default, true in case of submission to ENA dev server.')
    },
    output_descriptions={
        'submission_receipt': 'Artifact containing the submission summary.'
    },
    name='Cancle ENA Submission',
    description=("Cancelation of the ENA submission."),
    citations=[]
)

importlib.import_module('ena_uploader.types._transformer')