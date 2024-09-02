# q2-ena-uploader
The <b>q2-ena-uploader</b> is a  <a href="https://qiime2.org/">QIIME 2</a> plugin designed for the programmatic submission of metadata and raw sequence reads to the European Nucleotide Archive (ENA).
<p align="center">
<img src="images/ena_submission_image.webp" alt="Alt text" width="500"/>
</p>
To develop this plugin, we followed the <a href="https://ena-docs.readthedocs.io/en/latest/index.html">ENA documentation</a>. The submission process is depicted in the image above.


## Installation

## Usage

### Available actions
The ena-uploader offers several actions for adding, deleting, and modifying your submission. See the list below for details:
| Action               | Description                                                       |
|----------------------|-------------------------------------------------------------------|
| `upload-to-ena`        | Metadata upload to the ENA repository.                            |
| `cancel-ena-submission`| Cancel ENA metadata submission.                                   |

For a more detailed description of each action, refer to the sections below.

### Import metadata

#### 1) Study
To import the metadata of an existing study into the corresponding QIIME artifacts, run:

```shell
qiime tools import \
              --type ENAMetadataStudy \
              --input-path study.tsv \
              --output-path study.qza
```
where:
- `--input-path` is a path to the TSV file containing metadata of a study or samples,
- `--output-path` is the output artifact.

__Note__: When constructing a valid metadata TSV file, consider using one of the provided <a href="ena_uploader/templates/">templates</a>.
To create a valid study TSV file, two mandatory parameters are required: alias and title. All other parameters are optional. For fields such as URL links, both the description and the link should be combined into a single field in the TSV file, separated by a | symbol, as illustrated in the examples.


#### 2) Samples

```shell
qiime tools import \
              --type ENAMetadataSamples \
              --input-path samples.tsv \
              --output-path samples.qza
```


__Note:__  For sample submission, ENA provides metadata checklists detailing the minimal attributes required for different sample types. Please review the full range of checklists <a href="https://www.ebi.ac.uk/ena/browser/checklists">here</a> before submitting your samples. 

__Note:__ When using the default checklist for all your samples, you don’t need to specify the default code <a href="https://www.ebi.ac.uk/ena/browser/view/ERC000011"> ERC000011 </a>. However, if you apply multiple checklists for different samples, you must include all relevant codes in the metadata column checklist. For more examples see <a href="ena_uploader/templates/">templates</a>.

__Note__:Minimal study structure refers to the default data checklist. To create a valid TSV file, four mandatory parameters are needed for each sample: `alias` (qiime sample id), `taxon_id`, `geographic location (country and/or sea)` and `collection date`, see <a href="ena_uploader/templates/">templates</a>.

### Upload metadata

1) Before uploading to ENA, you need to set two environmental variables. To set these environment variables run the following commands in your terminal  `export ENA_USERNAME=<Webin-XXXXXX> ` and `export ENA_PASSWORD=<password>.` 

__Note__: Please ensure that your credentials are set at least 24 hours before your first submission to the ENA server.

2) Use qiime action to upload Study and Samples to ENA:

```shell
qiime ena-uploader upload-to-ena \
              --i-study study_metadata.qza \
              --i-samples samples_metadata.qza \
              --p-action_type\
              --p-dev server_type \
              --p-submission_hold_date \
              --o-submission-receipt  receipt.qza 
```
where:
- ` --i-study` is an artifact containing metadata of a study,
- ` --i-samples` is an artifact containing metadata of the samples,
- `--p-action_type` 2 action types are supported : ADD as a default and MODIFY,
- `--p-dev`  a boolean parameter, defaulting to True, indicating whether the submission is a test.
- `--p-submission_hold_date`  the release date of the study, on which it will become public along with all submitted data.
                                By default, this date is set to two months after the date of submission. Users can specify any date within two years of the current date. Accepted date format is `year-month-day`.
- `--output-path` This is an output artifact containing the assigned ENA accession numbers for the submitted objects.

__Note__: You can submit a study and metadata either separately or together; only one of the corresponding artifacts is required for submission. However, please note that to submit raw reads later, both the study and samples must already exist on the ENA server.

1) Cancel your ENA submission:
```shell
qiime ena-uploader cancel-ena-submission \
                --p-accession_number \
                --p-dev server_type \
                --o-submission-receipt  receipt.qza 
```
where:
- `--p-accession_number`  string parameter, it points to the object that is being cancelled,
- `--p-dev`  a boolean parameter, defaulting to True, indicating whether the submission is a test,
- `--output-path` This is an output artifact containing information about the deletion of ENA objects.

## License
q2-ena-uploader is released under a BSD-3-Clause license. See LICENSE for more details.