# Simplified submission

To submit all the metadata and raw reads in a single step, use the `submit-all` action. This action will perform all 
the steps which are required for the submission in the correct order. To see details about the individual steps and 
required inputs please have a look at respective sections [here](submission-full.md).

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
