import unittest
from unittest.mock import patch, mock_open, MagicMock
from ena_uploader import upload_to_ena, cancel_ena_submission, ActionType

class TestENAUploader(unittest.TestCase):

    @patch('os.getenv')
    @patch('requests.post')
    def test_upload_to_ena(self, mock_post, mock_getenv):
        mock_getenv.side_effect = lambda key: {'ENA_USERNAME': 'test_user', 'ENA_PASSWORD': 'test_pass'}.get(key)
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<RECEIPT>Test receipt</RECEIPT>"
        mock_post.return_value = mock_response

        mock_study = MagicMock()
        mock_study.toXml.return_value = "<PROJECT>Test project</PROJECT>".encode('utf-8')
        
        mock_samples = MagicMock()
        mock_samples.toXml.return_value = "<SAMPLES>Test samples</SAMPLES>".encode('utf-8')

        result = upload_to_ena(study=mock_study, samples=mock_samples, submission_hold_date="2024-10-01", action_type="ADD", dev=True)
        
        self.assertEqual(result, b"<RECEIPT>Test receipt</RECEIPT>")
        submission_xml = "<SUBMISSION><ACTIONS><ACTION><ADD /></ACTION><ACTION><HOLD HoldUntilDate=\"2024-10-01\" /></ACTION></ACTIONS></SUBMISSION>"

        mock_post.assert_called_once_with(
        'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit',
        auth=('test_user', 'test_pass'),
        files={
            'SUBMISSION': ('submission.xml', submission_xml, 'text/xml'),
            'PROJECT': ('project.xml', b"<PROJECT>Test project</PROJECT>", 'text/xml'),
            'SAMPLE': ('samples.xml', b"<SAMPLES>Test samples</SAMPLES>", 'text/xml')
        }
        )
        
    
    @patch('requests.post')
    @patch('os.getenv')
    def test_cancel_ena_submission(self, mock_getenv, mock_post):
        mock_getenv.side_effect = lambda key: {'ENA_USERNAME': 'test_user', 'ENA_PASSWORD': 'test_pass'}.get(key)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"<RECEIPT>Cancel receipt</RECEIPT>"
        mock_post.return_value = mock_response

        result = cancel_ena_submission(accession_number="ABC123", dev=True)

        self.assertEqual(result, b"<RECEIPT>Cancel receipt</RECEIPT>")


        self.assertEqual(mock_getenv.call_count, 2)
        mock_getenv.assert_any_call('ENA_USERNAME')
        mock_getenv.assert_any_call('ENA_PASSWORD')



if __name__ == '__main__':
    unittest.main()
