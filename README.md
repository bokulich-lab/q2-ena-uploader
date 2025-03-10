# q2-ena-uploader

The **q2-ena-uploader** is a [QIIME 2](https://qiime2.org/) plugin designed for the programmatic submission of metadata and raw sequence reads to the European Nucleotide Archive (ENA).

<p align="center">
  <img src="img/ena_submission.webp" alt="ENA Submission" width="700"/>
</p>

To develop this plugin, we followed the [ENA documentation](https://ena-docs.readthedocs.io/en/latest/index.html). The submission process is depicted in the image above.

## Installation

<!-- Add installation instructions here -->

## Usage

### Available Actions

The ena-uploader offers several actions for adding, deleting, and modifying your submission. See the list below for details:

| Action                    | Description                                  |
|---------------------------|----------------------------------------------|
| `submit-metadata-samples` | Upload sample and/or study metadata to ENA.  |
| `submit-metadata-reads`   | Upload experiment/runs metadata to ENA.      |
| `transfer-files-to-ena`   | Upload raw read files to the ENA FTP server. |
| `cancel-submission`       | Cancel ENA metadata submission.              |
| `submit-all`              | Submit metadata and raw reads to ENA.        |

For a more detailed description of each action, refer to the sections below.

### Submission workflow

The submission process using q2-ena-iploader consists of several steps:
1. Import metadata into QIIME artifacts.
2. Upload sample and study metadata to ENA.
3. Transfer raw reads to the ENA FTP server.
4. Upload experiment metadata to ENA.

Steps 2-4 should be performed in the specified order. Alternatively, the `submit-all` action can be used to 
submit metadata and raw reads in a single step.

#### Import Metadata

##### Study
To import the metadata of a study into the corresponding QIIME artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataStudy \
  --input-path study.tsv \
  --output-path study.qza
```
> [!TIP]
> To create a valid study TSV file, two mandatory parameters are required: **alias** and **title**. All other parameters are optional.
> 
> For fields such as URL links, both the description and the link should be combined into a single field in the TSV file, separated by a `|` symbol.
> The name of the filed should start with the **project_attribute_** prefix.
> 
> When constructing a valid study metadata TSV file, consider consulting one of the provided examples:
> - [minimal](./templates/study-minimal.tsv)
> - [extended](./templates/study-extended.tsv)

##### Samples
To import the sample metadata into the corresponding QIIME artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataSamples \
  --input-path samples.tsv \
  --output-path samples.qza
```

> [!TIP]
> For sample submission, ENA provides metadata checklists detailing the minimal attributes required for different sample types. 
> Please review the full range of checklists [here](https://www.ebi.ac.uk/ena/browser/checklists) before submitting your samples.

> [!NOTE]
> When using the default checklist for all your samples, you don't need to specify the default code [ERC000011](https://www.ebi.ac.uk/ena/browser/view/ERC000011). 
> However, if you apply multiple checklists for different samples, you must include all relevant codes in the metadata column checklist.

> [!IMPORTANT]
> Minimal sample structure refers to the default data checklist. To create a valid TSV file, four mandatory parameters are needed for each sample: 
> - `alias` (sample ID) 
> - `taxon_id` 
> - `geographic location (country and/or sea)`
> - `collection date`
>
> When constructing a valid study metadata TSV file, consider consulting one of the provided examples:
> - [minimal](./templates/sample-minimal.tsv)
> - [extended](./templates/sample-extended.tsv)

##### Experiments
To import the experiment metadata into the corresponding QIIME artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataExperiment \
  --input-path metadata.tsv \
  --output-path metadata.qza
```

> [!IMPORTANT]
> For experiment submission, ENA supports controlled vocabulary in the metadata fields, which can be accessed [here](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html).

> [!IMPORTANT]
> The minimal experiment structure requires the following mandatory fields: 
> - `title`
> - `study_ref` (study alias or accession number - should correspond to the alias indicated in the study metadata)
> - `sample_description` (sample id)
> - `platform`
> - `instrument_model`
> - `library_strategy`
> - `library_source`
> - `library_selection`
> - `library_layout`
> - `library_nominal_length` (only for paired reads)
> - `library_nominal_sdev` (only for paired reads)
> The field `library_construction_protocol` is optional.
>
> When constructing a valid experiment metadata TSV file, consider consulting one of the provided examples:
> - [minimal](./templates/experiment-minimal.tsv)
> - [extended](./templates/exmperiment-extended.tsv)

### Upload Metadata

1. Before uploading to ENA, you need to set two environmental variables. Run the following commands in your terminal:

   ```shell
   export ENA_USERNAME=<Webin-XXXXXX>
   export ENA_PASSWORD=<password>
   ```

   **Note**: Please ensure that your credentials are set at least 24 hours before your first submission to the ENA server.

2. Use the QIIME action to upload Study and Samples to ENA:

   ```shell
   qiime ena-uploader upload-to-ena \
     --i-study study_metadata.qza \
     --i-samples samples_metadata.qza \
     --p-action_type \
     --p-dev server_type \
     --p-submission_hold_date \
     --o-submission-receipt receipt.qza
   ```

   - `--i-study`: Artifact containing metadata of a study.
   - `--i-samples`: Artifact containing metadata of the samples.
   - `--p-action-type`: 2 action types are supported: ADD as a default and MODIFY.
   - `--p-dev`: A boolean parameter (default: True), indicating whether the submission is a test.
   - `--p-submission-hold-date`: The release date of the study, on which it will become public along with all submitted data. By default, this date is set to two months after the date of submission. Users can specify any date within two years of the current date. Accepted date format is `year-month-day`.
   - `--output-path`: This is an output artifact containing the assigned ENA accession numbers for the submitted objects.

   **Note**: You can submit a study and metadata either separately or together; only one of the corresponding artifacts is required for submission. However, please note that to submit raw reads later, both the study and samples must already exist on the ENA server.

### Upload Raw Reads

1. Before submitting the experiment, you must first transfer your files to the ENA FTP server. Ensure again that your environment variables ENA_USERNAME and ENA_PASSWORD are properly set.

2. Use the QIIME action to transfer the fastq file to ENA FTP.

   ```shell
   qiime ena-uploader transfer-files-to-ena \
     --i-demux CasavaOneEightSingleLanePerSampleDirFmt \
     --p-action ADD \
     --o-metadata metadata.qza
   ```

   - `--i-demux`: The demultiplexed sequencing data, either single-end or paired-end reads.
   - `--p-action`: Specifies the action to take. The default is ADD, but you can use DELETE to remove files from the ENA FTP server.
   - `--metadata`: This is an output artifact containing information about the transfer or deletion status of files on the ENA FTP server.

3. Use the QIIME action to upload Experiment to ENA:

   ```shell
   qiime ena-uploader upload-reads-to-ena \
     --i-demux CasavaOneEightSingleLanePerSampleDirFmt \
     --i-metadata experiment_metadata.qza \
     --p-submission-hold-date \
     --p-action-type server_type \
     --p-dev \
     --o-submission-receipt receipt.qza
   ```

   - `--i-demux`: The demultiplexed sequencing data, either single-end or paired-end reads.
   - `--i-experiment`: Artifact containing experiments submission parameters.
   - `--p-action_type`: 2 action types are supported: ADD as a default and MODIFY.
   - `--p-dev`: A boolean parameter (default: True) indicating whether the submission is a test.
   - `--p-submission_hold_date`: The release date for the data submission, determining when it will become public. The accepted date format is YYYY-MM-DD.
   - `--output-path`: This is an output artifact containing the assigned ENA accession numbers for the submitted objects.

## License

q2-ena-uploader is released under a BSD-3-Clause license. See LICENSE for more details.


