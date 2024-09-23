import importlib
from qiime2.plugin import Plugin,  Metadata
from q2_types.metadata import ImmutableMetadata
from qiime2.plugin import Str, Bool
from ena_uploader.types._types_and_formats import (
    ENAMetadataSamplesFormat, ENAMetadataSamplesDirFmt,ENAMetadataSamples,
    ENAMetadataStudyFormat, ENAMetadataStudyDirFmt, ENAMetadataStudy,
    ENASubmissionReceiptFormat,ENASubmissionReceiptDirFmt,ENASubmissionReceipt,
    ENAMetadataExperimentFormat,ENAMetadataExperiment,ENAMetadataExperimentDirFmt

)
from q2_types.sample_data import SampleData
from q2_types.per_sample_sequences import (
    SequencesWithQuality, PairedEndSequencesWithQuality)
from ena_uploader.uploader import uploadToEna, cancleENASubmission
from ena_uploader.experiment_upload import upload_reads_to_ena
from ena_uploader.ftp_file_upload import transfer_files_to_ena

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



plugin.methods.register_function(
    function=upload_reads_to_ena,
    inputs={
        'demux': SampleData[SequencesWithQuality |
                                PairedEndSequencesWithQuality],
        'experiment' : ENAMetadataExperiment

    },
    parameters={
            'submission_hold_date': Str,
            'action_type': Str,
            'dev' : Bool
    },
    outputs=[('submission_receipt', ENASubmissionReceipt)],
    
    input_descriptions={
            'demux': 'The demultiplexed sequencing data, either single-end or paired-end reads.',
            'experiment': 'Artifact containing experiment submission parameters for ENA.'
            },

    parameter_descriptions={
        'submission_hold_date': "The release date of the study, on which it will become public along with all submitted data.",
        'action_type': 'Type of action to perform, such as ADD (default) or MODIFY for updating submissions.',
        'dev' : 'Boolean parameter (default: False). Set to True when submitting to the ENA development server.'
    
    },
    output_descriptions={
        'submission_receipt': 'An artifact containing the ENA submission receipt and assigned accession numbers.'
    },
    name='ENA Raw Reads Submission',
    description="Submit raw reads and associated metadata to the ENA.",
    citations=[]


)

plugin.methods.register_function(
    function=transfer_files_to_ena,
    inputs={
        'demux': SampleData[SequencesWithQuality |
                                PairedEndSequencesWithQuality]
        

    },
    parameters={
        'action': Str
            
    },
    outputs=[('metadata', ImmutableMetadata)],
    
    input_descriptions={
            'demux': 'The demultiplexed sequencing data, either single-end or paired-end reads.'
            },

    parameter_descriptions={
            'action': 'Specifies the action to perform. Default is ADD for uploading files to the ENA FTP server. Use DELETE to remove files.'
    },
    output_descriptions={
        'metadata': 'An artifact containing the status of the file transfer or deletion operation.'},

    name='ENA Raw Reads File Transfer',
    description="Transfer or delete raw reads files on the ENA FTP server.",
    citations=[]
)



importlib.import_module('ena_uploader.types._transformer')