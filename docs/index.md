# q2-ena-uploader
![ENA Studies](https://img.shields.io/badge/ENA%20Studies-9-blue)
![ENA Samples](https://img.shields.io/badge/ENA%20Samples-5638-blue)

The **q2-ena-uploader** is a [QIIME 2](https://qiime2.org) plugin designed for the programmatic submission of metadata and raw sequence reads to the European Nucleotide Archive (ENA).


<p align="center">
  <img src="https://raw.githubusercontent.com/bokulich-lab/q2-ena-uploader/main/img/ena_submission.webp" alt="ENA Submission" width="700"/>
</p>



:::{aside}
```{note}
{term}`Study`: Groups together data submitted to the archive and controls its release date. 

{term}`Sample`: Contains information about the sequenced source material. 

{term}`Experiment`: Contains information about a sequencing experiment.

{term}`Run`: Refers to data files containing sequence reads.
::: 

To develop this plugin, we followed the [ENA documentation](https://ena-docs.readthedocs.io). The submission process is depicted in the image above (courtesy of the ENA).



## Submission workflow
<p align="center">
  <img src="ena-uploader-workflow-01.png" alt="Submission workflow" width="700"/>
</p>

:::{aside}
```{note}
To run the submission, QIIME requires  <span style="color:#60a285;">input artifacts</span>.
You can create these artifacts by following [Step 1](#step-1-import-metadata-into-qiime-artifacts).



After running the initial QIIME <span style="color:#b8332f; font-style:italic;">actions</span>
, an <span style="color: #93669d;"> output artifact</span> will be generated containing the submission status.
Once both initial actions,
 <span style="color:#b8332f; font-style:italic;">submit-metadata-samples</span> ([Step 2](#step-2-upload-sample-and-study-metadata-to-ena)) and 
<span style="color:#b8332f;font-style:italic;">transfer-files-to-ena</span> ([Step 3](#step-3-transfer-raw-reads-to-the-ena-ftp-server)) have successfully completed, you can run <span style="color:#b8332f; font-style:italic;">submit-metadata-reads</span> ([Step 4](#step-4-upload-experiment-metadata-to-ena)) to finalize the submission.

The final submission status will again be provided as a QIIME output artifact - <span style="color: #93669d;"> submission receipt</span>.
:::

After completing the [installation](./installation.md) and creating an [ENA account](https://www.ebi.ac.uk/ena/submit/webin/login), the submission process using the _q2-ena-uploader_ consists of several steps:

:::{aside}
```{tip}
It is recommended to create an ENA account and obtain credentials at least 24 hours prior to submission.
:::

1. Import metadata into QIIME artifacts.
2. Upload sample and study metadata to ENA.
3. Transfer raw reads to the ENA FTP server.
4. Upload experiment metadata to ENA.

Steps 2-4 should be performed in the specified order. Alternatively, the `submit-all` action can be used to 
submit metadata and raw reads in a single step. To jump to the section on simplified submission, click [here](#simplified-submission-workflow).


### Step 1: Import metadata into QIIME artifacts

#### {term}`Study`
To import the metadata of a study into the corresponding QIIME artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataStudy \
  --input-path study_metadata.tsv \
  --output-path study_metadata.qza
```
>[!IMPORTANT]
>To create a valid study TSV file, two mandatory parameters are required: **alias** and **title**. All other parameters are optional.
When constructing a valid study metadata TSV file, consider consulting one of the provided examples in the [Templates](./templates.md) section.





#### {term}`Sample` 
To import the sample metadata into the corresponding QIIME artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataSamples \
  --input-path sample_metadata.tsv \
  --output-path sample_metadata.qza
```
##### Checklists

1. For sample submission, ENA provides metadata checklists detailing the minimal attributes required for different sample types. 
Please review the full range of [ENA checklists](https://www.ebi.ac.uk/ena/browser/checklists) before submitting your samples.


2. When using the ENA default sample checklist for all your samples, you do not need to specify the default code [ERC000011](https://www.ebi.ac.uk/ena/browser/view/ERC000011). 
 However, if you apply multiple checklists for different samples, you must include all relevant [ENA checklists](https://www.ebi.ac.uk/ena/browser/checklists) codes in the metadata column checklist. In this case, create a single metadata TSV file that combines all columns from these checklists and fill in values only where applicable.
 

:::{aside}
```{tip}
Using multiple checklists within the same sample set can be useful when samples originate from different environments, such as gut microbiomes and soil. Conversely, allowing [missing values](https://www.insdc.org/technical-specifications/missing-value-reporting/) (e.g., for control samples) is appropriate for special cases within a single checklist.
:::



> [!IMPORTANT]
> Minimal sample structure refers to the ENA default sample checklist data structure. To create a valid TSV file, four mandatory parameters are needed for each sample: 
> - `alias` (sample ID) 
> - `taxon_id` 
> - `geographic location (country and/or sea)`
> - `collection date`
>
> When constructing a valid study metadata TSV file, consider consulting one of the provided examples in the [Templates](./templates.md) section.


#### {term}`Experiment`
To import the experiment metadata into the corresponding QIIME artifacts, run:

```shell
qiime tools import \
  --type ENAMetadataExperiment \
  --input-path experiment_metadata.tsv \
  --output-path experiment_metadata.qza
```

> [!IMPORTANT]
> For experiment submission, ENA supports controlled vocabulary in the metadata fields, which can be accessed [here](https://ena-docs.readthedocs.io/en/latest/submit/reads/webin-cli.html).

> [!IMPORTANT]
> The minimal experiment structure requires the following mandatory fields: 
> - `title`
> - `study_ref` (study alias or accession number - should correspond to the alias indicated in the study metadata)
> - `sample_description` (sample ID)
> - `platform`
> - `instrument_model`
> - `library_strategy`
> - `library_source`
> - `library_selection`
> - `library_layout`
> - `library_nominal_length` (only for paired reads)
> - `library_nominal_sdev` (only for paired reads)
>
> The field `library_construction_protocol` is optional.
>
> When constructing a valid experiment metadata TSV file, consider consulting one of the provided examples, see more in [Templates](./templates.md) section.

### Step 2: Upload sample and study metadata to ENA

#### Set ENA credentials
Before uploading to ENA, you need to set two environmental variables containing your ENA credentials:

``` shell
   export ENA_USERNAME=<Webin-XXXXXX>
   export ENA_PASSWORD=<password>
```
   
> [!WARNING]
> Please ensure that your credentials are set at least 24 hours before your first submission to the ENA server.

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
   - `--p-submission-hold-date`: The release date of the study, on which it will become public along with all submitted data. By default, this date is set to two months after the date of submission. Users can specify any date within two years of the current date. Accepted date format is `YYYY-MM-DD`.
   - `--o-submission-receipt`: The output artifact containing the assigned ENA accession numbers for the submitted objects.


> [!NOTE]
> You can submit a study and sample metadata either separately or together, only one of the corresponding artifacts is required for submission. However, please note that to submit raw reads later, both the study and samples must already exist on the ENA server.

> [!IMPORTANT]
> To perform a test submission, set the `--p-dev` parameter to `True` (this is also the default). This will submit the data to the ENA _dev_ server 
> (this data will be removed automatically after 24h). To submit the data to the production server, set the parameter to `False` or use the `--p-no-dev` flag.

### Step 3: Transfer raw reads to the ENA FTP server

> [!IMPORTANT]
> Before submitting the {term}`Experiment`, you must first transfer your files to the ENA FTP server. 
> Ensure again that your environment variables `ENA_USERNAME` and `ENA_PASSWORD` are properly [set](#set-ena-credentials).


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
> [!IMPORTANT]
> Make sure that your credentials are configured through the environment variables `ENA_USERNAME` and `ENA_PASSWORD`, as described [here](#set-ena-credentials).

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

> [!IMPORTANT]
> To perform a test Submission, set the `--p-dev` parameter to `True` (this is also the default). This will submit the data to the ENA _dev_ server 
> (this data will be removed automatically after 24h). To submit the data to the production server, set the parameter to `False` or use the `--p-no-dev` flag.

## Simplified submission workflow
To submit all the metadata and raw reads in a single step, use the `submit-all` action. This action will perform all 
the steps which are required for the submission in the correct order. To see details about the individual steps and 
required inputs please have a look at respective sections above.

To submit using the simplified procedure, execute the following command:

```shell
qiime ena-uploader submit-all \
  --i-study study_metadata.qza \
  --i-samples sample_metadata.qza \
  --i-experiment experiment_metadata.qza \
  --i-demux <your reads artifact> \
  --p-submission-hold-date <hold date> \
  --p-dev \
  --p-action ADD \
  --o-sample-submission-receipt samples_receipt.qza \
  --o-read-submission-receipt reads_receipt.qza \
  --o-file-upload-metadata upload_metadata.qza
```

## License
q2-ena-uploader is released under a BSD-3-Clause license. See LICENSE for more details.


