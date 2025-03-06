# ----------------------------------------------------------------------------
# Copyright (c) 2025, Bokulich Lab.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


def submit_all(
    ctx, demux, study, samples, experiment, submission_hold_date, dev, action
):
    submit_metadata_samples = ctx.get_action("ena_uploader", "submit_metadata_samples")
    submit_metadata_reads = ctx.get_action("ena_uploader", "submit_metadata_reads")
    transfer_files = ctx.get_action("ena_uploader", "transfer_files_to_ena")

    (receipt_study,) = submit_metadata_samples(
        study=study,
        samples=samples,
        submission_hold_date=submission_hold_date,
        dev=dev,
        action=action,
    )
    (receipt_transfer,) = transfer_files(demux=demux, action=action)
    (receipt_reads,) = submit_metadata_reads(
        demux=demux,
        experiment=experiment,
        samples_submission_receipt=receipt_study,
        file_transfer_metadata=receipt_transfer,
        submission_hold_date=submission_hold_date,
        action=action,
        dev=dev,
    )

    return receipt_study, receipt_reads, receipt_transfer
