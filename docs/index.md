# q2-ena-uploader documentation

The **q2-ena-uploader** is a [QIIME 2](https://qiime2.org) plugin designed for the programmatic submission of metadata and raw sequence reads to the European Nucleotide Archive (ENA).


<p align="center">
  <img src="https://raw.githubusercontent.com/bokulich-lab/q2-ena-uploader/main/img/ena_submission.webp" alt="ENA Submission" width="700"/>
</p>


To develop this plugin, we followed the [ENA documentation](https://ena-docs.readthedocs.io). The submission process is depicted in the image above (courtesy of the ENA).

```{note} Definitions
**Study:** groups together data submitted to the archive and controls its release date. 

**Sample:** contains information about the sequenced source material. 

**Experiment:** contains information about a sequencing experiment.

**Run:** refers to the data files containing sequence reads.
```

Before you proceed with the submission, you should follow the [installation instructions](installation.md).

If you already have a working installation of q2-ena-uploader, you can jump straight to the [submission tutorial](submission-full.md).
