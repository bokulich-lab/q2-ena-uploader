# Submission

```{image} ena-uploader-workflow-01.png
:alt: Submission workflow
:width: 700
:align: center
```
:::{aside}
```{note}
To run the submission, QIIME 2 requires <span style="color:#60a285;">input artifacts</span>.
You can create these artifacts by following [Step 1](#step-1-import-metadata-into-qiime-artifacts).

After running the initial QIIME 2 <span style="color:#b8332f; font-style:italic;">actions</span>
, an <span style="color: #93669d;"> output artifact</span> will be generated containing the submission status.
Once both initial actions,
 <span style="color:#b8332f; font-style:italic;">submit-metadata-samples</span> ([Step 2](#step-2-upload-sample-and-study-metadata-to-ena)) and 
<span style="color:#b8332f;font-style:italic;">transfer-files-to-ena</span> ([Step 3](#step-3-transfer-raw-reads-to-the-ena-ftp-server)) have successfully completed, you can run <span style="color:#b8332f; font-style:italic;">submit-metadata-reads</span> ([Step 4](#step-4-upload-experiment-metadata-to-ena)) to finalize the submission.

The final submission status will again be provided as a QIIME 2 output artifact - <span style="color: #93669d;"> submission receipt</span>.
```
:::

ENA Submission

After completing the [installation](./installation.md) and creating an [ENA account](https://www.ebi.ac.uk/ena/submit/webin/login), the submission process using the _q2-ena-uploader_ consists of several steps:

:::{aside}
```{tip}
It is recommended to create an ENA account and obtain credentials at least 24 hours prior to submission.
```
:::

1. Import data into QIIME 2 artifacts.
2. Upload sample and study metadata to ENA.
3. Transfer raw reads to the ENA FTP server.
4. Upload experiment metadata to ENA.

```{attention}
Steps 2-4 should be performed in the specified order. Alternatively, the `submit-all` action can be used to 
submit metadata and raw reads in a single step. To jump to the section on simplified submission, click [here](submission-simple.md).
```

### Step 1: Import data into QIIME 2 artifacts

Data imported into QIIME 2 are organized as data [artifacts](https://amplicon-docs.qiime2.org/en/latest/explanations/archives.html). Each artifact is assigned a Semantic Type, which determines its corresponding Artifact Class within the QIIME 2 framework.

Within our ENA submission workflow:

- Raw reads can be imported into QIIME 2 using several different artifact classes, depending on the specific data format. An overview of these supported formats and import choices is available in the official [QIIME 2](https://amplicon-docs.qiime2.org/en/latest/how-to-guides/how-to-import.html) documentation.

- Metadata — including studies, samples, and experiments — are imported as QIIME 2 artifacts with the Semantic Types `ENAMetadataStudy`, `ENAMetadataSamples`, and `ENAMetadataExperiment`, respectively.

These artifacts represent all required inputs for the ENA submission workflow. Once imported, they are stored as .qza files within the QIIME 2 environment.
Proceed to the next sections to import all necessary input data into QIIME 2.

#### Raw reads
This is a simple example illustrating the import of FASTQ sequencing data into QIIME 2 artifacts. More import options are described [here](https://amplicon-docs.qiime2.org/en/latest/how-to-guides/how-to-import.html) .

```shell
qiime tools import \
  --type 'SampleData[PairedEndSequencesWithQuality]' \
  --input-path my-sequence-data/ \
  --input-format CasavaOneEightSingleLanePerSampleDirFmt \
  --output-path demux.qza
```
The  sections bellow describe all types of metadata imports.

#### {term}`Study` 
To import the metadata of a study into the corresponding QIIME 2 artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataStudy \
  --input-path study_metadata.tsv \
  --output-path study_metadata.qza
```
```{important}
To create a valid study TSV file, two mandatory parameters are required: **alias** and **title**. All other parameters are optional.
When constructing a valid study metadata TSV file, consider consulting one of the provided examples in the [Templates](./templates.md) section.
```



#### {term}`Sample` 
To import the sample metadata into the corresponding QIIME 2 artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataSamples \
  --input-path sample_metadata.tsv \
  --output-path sample_metadata.qza
```
##### Checklists

1. For sample submission, ENA provides metadata checklists detailing the minimal attributes required for different sample types. 
Please review the full range of ENA [sample checklists](https://www.ebi.ac.uk/ena/browser/checklists) before submitting your samples.


2. When using the ENA default sample checklist for all your samples, you do not need to specify the default code [ERC000011](https://www.ebi.ac.uk/ena/browser/view/ERC000011). 
 However, if you apply multiple checklists for different samples, you must include all relevant ENA [sample checklists](https://www.ebi.ac.uk/ena/browser/checklists) codes in the metadata column checklist. In this case, create a single metadata TSV file that combines all columns from these checklists and fill in values only where applicable.


:::{aside}
```{note}
Using multiple checklists within the same sample set can be useful when samples originate from different environments, such as gut microbiomes and soil. Conversely, allowing [missing values](https://www.insdc.org/technical-specifications/missing-value-reporting/) (e.g., for control samples) is appropriate for special cases within a single checklist.
```
:::
```{tip}
Sample checklist templates are available in this GitHub [repository](https://github.com/ELIXIR-Belgium/ENA-metadata-templates)
. Each folder contains a sample.tsv file ready for submission. Remember to add an ENA checklist column to indicate which checklist is used. You can also combine columns from multiple checklists in a single submission.

Alternatively, you can download a similar TSV directly from the ENA web [portal](https://www.ebi.ac.uk/ena/submit/webin/login)
 after logging in and selecting “Register Samples.” Just make sure to add the ENA checklist column and remove the first line of the downloaded file.
```
```{attention} Minimal sample structure
:class: dropdown
Minimal sample structure refers to the ENA default sample checklist data structure. To create a valid TSV file, four mandatory parameters are needed for each sample: 
- `alias` (sample ID) 
- `taxon_id` 
- `geographic location (country and/or sea)`
- `collection date`

When constructing a valid study metadata TSV file, consider consulting one of the provided examples in the [Templates](./templates.md) section.
```

#### {term}`Experiment` 
To import the experiment metadata into the corresponding QIIME 2 artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataExperiment \
  --input-path experiment_metadata.tsv \
  --output-path experiment_metadata.qza
```

:::{aside}
```{important}
For experiment submission, ENA supports controlled vocabulary in the metadata fields, which can be accessed [here](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html).
```
:::

```{attention} Minimal experiment structure
:class: dropdown
The minimal experiment structure requires the following mandatory fields: 
- `title`
- `study_ref` (study alias or accession number - should correspond to the alias indicated in the study metadata)
- `sample_description` (sample ID)
- `platform`
- `instrument_model`
- `library_strategy`
- `library_source`
- `library_selection`
- `library_layout`
- `library_nominal_length` (only for paired reads)
- `library_nominal_sdev` (only for paired reads)

The field `library_construction_protocol` is optional.

When constructing a valid experiment metadata TSV file, consider consulting one of the provided examples, see more in [Templates](./templates.md) section.
```

### Step 2: Upload sample and study metadata to ENA

#### Set ENA credentials
Before uploading to ENA, you need to set two environmental variables containing your ENA credentials:

``` shell
   export ENA_USERNAME=<Webin-XXXXXX>
   export ENA_PASSWORD=<password>
```
   
```{warning}
Please ensure that your credentials were created at least 24 hours before your first submission to the ENA server.
```

#### Upload metadata
 Execute the following QIIME 2 action to submit {term}`Study` and {term}`Sample` metadata to perform a test submission to the ENA _dev_ server:

   ```shell
   qiime ena-uploader submit-metadata-samples \
     --i-study study_metadata.qza \
     --i-samples sample_metadata.qza \
     --p-action ADD \
     --p-dev \
     --p-submission-hold-date <hold date> \
     --o-submission-receipt samples_receipt.qza
   ```

   - `--i-study`: Artifact containing metadata of the study.
   - `--i-samples`: Artifact containing metadata of the samples.
   - `--p-action-type`: 2 action types are supported: ADD (default) and MODIFY.
   - `--p-dev`: A boolean parameter indicating whether the submission is a test.
   - `--p-submission-hold-date`: The release date of the study, on which it will become public along with all submitted data. By default, this date is set to two years after the date of submission. Users can specify any date within two years of the current date. Accepted date format is `YYYY-MM-DD`.
   - `--o-submission-receipt`: The output artifact containing the assigned ENA accession numbers for the submitted objects.


```{note}
You can submit a study and sample metadata either separately or together, only one of the corresponding artifacts is required for submission. However, please note that to submit raw reads later, both the study and samples must already exist on the ENA server.
```

```{important}
The submission hold date is required for all submissions to the ENA server.

To perform a test submission, set the `--p-dev` parameter to `True` (this is also the default). This will submit the data to the ENA _dev_ server 
(this data will be removed automatically after 24h). To submit the data to the production server, set the parameter to `False` or use the `--p-no-dev` flag.
```

### Step 3: Transfer raw reads to the ENA FTP server

```{important} Credentails required
Before submitting the {term}`Experiment`, you must first transfer your files to the ENA FTP server. 
Ensure again that your environment variables `ENA_USERNAME` and `ENA_PASSWORD` are properly [set](#set-ena-credentials).
```

Execute the following QIIME 2 action to transfer the FASTQ files to the ENA FTP server.

```shell
qiime ena-uploader transfer-files-to-ena \
  --i-demux <your reads artifact> \
  --p-action ADD \
  --o-metadata transfer_metadata.qza
```

- `--i-demux`: The demultiplexed sequencing data, either single-end or paired-end.
- `--p-action`: Specifies the action to take. The default is ADD, but you can use DELETE to remove files from the ENA FTP server.
- `--o-metadata`: This is the output artifact containing information about the transfer or deletion status of files on the ENA FTP server.

### Step 4: Upload experiment metadata to ENA
```{important} Credentials required
Make sure that your credentials are configured through the environment variables `ENA_USERNAME` and `ENA_PASSWORD`, as described [here](#set-ena-credentials).
```

Execute the following QIIME 2 action to submit {term}`Experiment`/{term}`Run` metadata to ENA:
```shell
qiime ena-uploader submit-metadata-reads \
  --i-demux <your reads artifact> \
  --i-experiment experiment_metadata.qza \
  --i-samples-submission-receipt samples_receipt.qza \
  --i-file-transfer-metadata transfer_metadata.qza \
  --p-submission-hold-date <hold date> \
  --p-action ADD \
  --p-dev \
  --o-submission-receipt receipt.qza
```

- `--i-demux`: The demultiplexed sequencing data, either single-end or paired-end.
- `--i-experiment`: Artifact containing experiments submission parameters.
- `--i-samples-submission-receipt`: Artifact containing the submission receipt of the study and samples.
- `--i-file-transfer-metadata`: Artifact containing the metadata of the file transfer to the ENA FTP server.
- `--p-action`: 2 action types are supported: ADD (default) and MODIFY.
- `--p-dev`: A boolean parameter indicating whether the submission is a test.
- `--p-submission-hold-date`: The release date for the data submission, determining when it will become public. The accepted date format is YYYY-MM-DD.
- `--submission-receipt`: The output artifact containing the assigned ENA accession numbers for the submitted objects.

```{important}
To perform a test Submission, set the `--p-dev` parameter to `True` (this is also the default). This will submit the data to the ENA _dev_ server 
(this data will be removed automatically after 24h). To submit the data to the production server, set the parameter to `False` or use the `--p-no-dev` flag.
```
