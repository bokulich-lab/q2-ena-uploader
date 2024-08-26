# q2-ena-uploader

## Usage

### Avalilable actions


| Action               | Description                                                       |
|----------------------|-------------------------------------------------------------------|
| `uploadToEna`        | Metadata upload to the ENA repository.                            |
| `cancleENASubmission`| Cancle ENA metadata submission.                                   |


### Import metadata

To import existing metadata into corresponding qiime artifact run:

```shell
qiime tools import \
              --type ENAMetadataStudy \
              --input-path study.tsv \
              --output-path study.qza
```



```shell
qiime tools import \
              --type ENAMetadataSamples \
              --input-path samples.tsv \
              --output-path samples.qza
```

where:
- `--input-path` is a path to the TSV file containing metadata of a study or samples.
- `--output-path` is the output artifact.

__Note:__ (compulsory ids)

### Upload metadata

1) Before uploading to ENA you need to set 2 enviromental variables. To set these environment variables run the following commands in your terminal  `export ENA_USERNAME=<Webin-XXXXXX> ` and `export ENA_PASSWORD=<password>.`

2) Use qiime action to upload Study and Samples to ENA:

```shell
qiime ena-uploader uploadToEna \
              --i-study study_metadata.qza \
              --i-samples samples_metada.qza \
              --p-dev server_type \
              --o-submission-receipt  receipt.qza 
```