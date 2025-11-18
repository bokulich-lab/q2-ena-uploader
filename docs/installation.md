# Installation
## Existing QIIME 2 environment
The _q2-ena-uploader_ plugin can be installed into any QIIME 2 conda environment (see [here](https://docs.qiime2.org) for 
more specific installation instructions). To install the plugin, run the following commands:

```shell
conda activate <your QIIME 2 environment>
```

```shell
pip install git+https://github.com/bokulich-lab/q2-ena-uploader.git
```

Refresh the QIIME 2 cache and check if the plugin is available:
```shell
qiime dev refresh-cache
qiime ena-uploader --help
```
## New QIIME 2 environment
Alternatively, you can also create a dedicated environment by executing:

```shell
conda env create -n uploader-env --file https://raw.githubusercontent.com/bokulich-lab/q2-ena-uploader/main/environment-files/q2-ena-uploader-qiime2-tiny-2025.4.yml
```
