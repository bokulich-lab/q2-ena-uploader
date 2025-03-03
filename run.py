import qiime2
from qiime2.plugins import ena_uploader

cache = qiime2.Cache("/Users/michal/Downloads/cache")

reads = cache.load("demux")
exp = cache.load("experiment-fixed")

(receipt,) = ena_uploader.methods.submit_metadata_reads(
    demux=reads, experiment=exp, dev=True
)
receipt.save("receipt-01.qza")
