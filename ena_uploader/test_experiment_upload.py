import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import pandas as pd
from ena_uploader import register_reads, _process_manifest

class TestUploadReadsToEna(unittest.TestCase):

    @patch('requests.post')
    @patch('os.getenv')
    @patch('builtins.open', new_callable=mock_open, read_data=b'binary_data_for_md5')
    @patch('ena_uploader._process_manifest')
    @patch('ena_uploader._runFromDict')
    def test_upload_reads_to_ena(
        self, mock_run_from_dict, mock_process_manifest, mock_open_file, mock_getenv, mock_post
    ):
        # Arrange
        demux = MagicMock()
        experiment = MagicMock()
        df = pd.DataFrame({
            'forward': ['/path/to/forward.fastq'],
            'reverse': ['/path/to/reverse.fastq']
        })
        demux.manifest = df
        
        # Mock return values
        mock_process_manifest.return_value = {
            'sample1': {
                'filename': ['forward.fastq', 'reverse.fastq'],
                'checksum': ['1d6cb0f96a77cc7d374818ce7113e6e7', '1d6cb0f96a77cc7d374818ce7113e6e7']
            }
        }
        mock_run_from_dict.return_value = b"""<?xml version='1.0' encoding='utf-8'?>
        <RUN_SET><RUN alias="run_0"><EXPERIMENT_REF refname="exp_0" />
        <DATA_BLOCK><FILES>
        <FILE filename="forward.fastq" filetype="fastq" checksum_method="MD5" checksum="1d6cb0f96a77cc7d374818ce7113e6e7" />
        <FILE filename="reverse.fastq" filetype="fastq" checksum_method="MD5" checksum="1d6cb0f96a77cc7d374818ce7113e6e7" />
        </FILES></DATA_BLOCK></RUN></RUN_SET>"""
        mock_getenv.side_effect = lambda key: 'mock_user' if key == 'ENA_USERNAME' else 'mock_pass'
        mock_post.return_value = MagicMock(status_code=200, content=b'<RECEIPT>Success</RECEIPT>')
        
        # Act
        result = register_reads(
            demux=demux,
            experiment=experiment,
            submission_hold_date='2023-01-01',
            action_type='ADD',
            dev=True
        )


        mock_post.assert_called_once()

        actual_call_args = mock_post.call_args[1]  

        self.assertIn('SUBMISSION', actual_call_args['files'])
        self.assertIn('EXPERIMENT', actual_call_args['files'])
        self.assertIn('RUN', actual_call_args['files'])

        submission_content = actual_call_args['files']['SUBMISSION'][1]
        self.assertIn('<SUBMISSION>', submission_content)
        self.assertIn('<ACTION><ADD /></ACTION>', submission_content)

        run_content = actual_call_args['files']['RUN'][1]
        self.assertIn(b'<RUN_SET>', run_content)
        self.assertIn(b'<FILE filename="forward.fastq"', run_content)
        self.assertIn(b'<FILE filename="reverse.fastq"', run_content)

        self.assertEqual(result, b'<RECEIPT>Success</RECEIPT>')
        mock_open_file.assert_called_with('response.xml', 'wb')
        mock_open_file().write.assert_called_once_with(b'<RECEIPT>Success</RECEIPT>')

if __name__ == '__main__':
    unittest.main()
