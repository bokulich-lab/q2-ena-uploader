# q2-ena-uploader
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
| `transfer-files-to-ena`        | Raw files upload to the ENA ftp.                            |
| `upload-reads-to-ena`| Upload experiment and runs to ENA.                                   |

For a more detailed description of each action, refer to the sections below.
