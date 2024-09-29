import unittest
from unittest.mock import patch, MagicMock, mock_open
import ftplib
import os
import qiime2
import pandas as pd

class MockCasavaOneEightSingleLanePerSampleDirFmt:
    def __init__(self, manifest):
        self.manifest = manifest

from ena_uploader import _upload_files, _delete_files


class TestFTPFunctions(unittest.TestCase):

    @patch('ftplib.FTP')
    @patch('os.path.isfile', return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_upload_files_success(self, mock_isfile, mock_ftp, mock_file):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp.return_value = mock_ftp_instance
        
        # Test successful upload
        sampleid = 'sample1'
        filepath = 'path/to/file.fastq'
        result = _upload_files(mock_ftp_instance, filepath, sampleid)
        
        self.assertEqual(result, (sampleid, 'file.fastq', True, None, 'ADD'))
        mock_ftp_instance.storbinary.assert_called_once()

    @patch('ftplib.FTP')
    @patch('os.path.isfile', return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_upload_files_failure(self, mock_isfile, mock_ftp, mock_file):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp_instance.storbinary.side_effect = ftplib.Error('Meh.')
        
        # Test failed upload
        sampleid = 'sample1'
        filepath = 'path/to/file.fastq'
        result = _upload_files(mock_ftp_instance, filepath, sampleid)
        
        self.assertEqual(result, (sampleid, 'file.fastq', False, mock_ftp_instance.storbinary.side_effect.__str__(), 'ADD'))

    @patch('ftplib.FTP')
    @patch('os.path.isfile', return_value=True)
    def test_delete_files_success(self, mock_isfile, mock_ftp):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp.return_value = mock_ftp_instance
        
        # Test successful delete
        sampleid = 'sample1'
        filepath = 'path/to/file.fastq'
        result = _delete_files(mock_ftp_instance, filepath, sampleid)
        
        self.assertEqual(result, (sampleid, 'file.fastq', True, None, 'DELETE'))
        mock_ftp_instance.delete.assert_called_once()

    @patch('ftplib.FTP')
    @patch('os.path.isfile', return_value=True)
    def test_delete_files_failure(self, mock_isfile, mock_ftp):
        # Mock FTP instance
        mock_ftp_instance = MagicMock()
        mock_ftp_instance.delete.side_effect = ftplib.Error('No beer in fridge')
        
        # Test failed delete
        sampleid = 'sample1'
        filepath = 'path/to/file.fastq'
        result = _delete_files(mock_ftp_instance, filepath, sampleid)
        
        self.assertEqual(result, (sampleid, 'file.fastq', False, mock_ftp_instance.delete.side_effect.__str__(), 'DELETE'))

if __name__ == '__main__':
    unittest.main()
