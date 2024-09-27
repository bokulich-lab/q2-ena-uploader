import os
import requests
import pandas as pd
import qiime2
import xml.etree.ElementTree as ET

from enum import Enum
from xml.etree.ElementTree import Element, SubElement, tostring
from ena_uploader.types._types_and_formats import (
    ENAMetadataSamplesFormat, ENAMetadataSamplesDirFmt, ENAMetadataSamples,
    ENAMetadataStudyFormat, ENAMetadataStudyDirFmt, ENAMetadataStudy,
    ENASubmissionReceiptFormat, ENASubmissionReceiptDirFmt, ENASubmissionReceipt
)

DEV_SERVER_URL = 'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit'
PRODUCTION_SERVER_URL = 'https://www.ebi.ac.uk/ena/submit/drop-box/submit'

class ActionType(Enum):
    ADD = "ADD"
    MODIFY = "MODIFY"

def str_to_action_type(s: str) -> ActionType:
    if s == 'ADD':
        return ActionType.ADD
    elif s == 'MODIFY':
        return ActionType.MODIFY
    raise RuntimeError(f'Unknown action type {s}')

def _create_submission_xml(action: ActionType, hold_date: str) -> str:
    submission = Element('SUBMISSION')
    actions = SubElement(submission, 'ACTIONS')
    action_element = SubElement(actions, 'ACTION')
    SubElement(action_element, action.value)

    if hold_date:
        hold_action = SubElement(actions, 'ACTION')
        hold = SubElement(hold_action, 'HOLD')
        hold.set('HoldUntilDate', hold_date)

    return tostring(submission, encoding='unicode', method='xml')

def upload_to_ena(study: ENAMetadataStudyFormat = None, 
                  samples: ENAMetadataSamplesFormat = None,
                  submission_hold_date: str = '',
                  action_type: str = 'ADD',
                  dev: bool = True) -> bytes:
    '''
    Function to submit metadata of the study and samples to ENA.
    Args:
        study: ENAMetadataStudyFormat
               Qiime artifact containing a TSV file with the study attributes.
        samples: ENAMetadataSamplesFormat
               Qiime artifact containing a TSV file with the samples metadata attributes.
        submission_hold_date: str
               The release date of the study, on which it will become public along with all submitted data.
               By default, this date is set to two months after the date of submission. Users can 
               specify any date within two years of the current date.
        action_type: str
               2 action types are supported: ADD (default) and MODIFY.
        dev: bool
             True by default. Indicates whether the data submission goes to the development server.
             If False, the submission goes to the production server.
    Returns:
        submission_receipt: bytes
               Qiime artifact containing an XML response from the ENA server.
    '''

    username = os.getenv('ENA_USERNAME')
    password = os.getenv('ENA_PASSWORD')

    if username is None:
        raise RuntimeError('Missing ENA_USERNAME, make sure it is set as an environment variable.')
    if password is None:
        raise RuntimeError('Missing ENA_PASSWORD, make sure it is set as an environment variable.')

    xml_content = _create_submission_xml(str_to_action_type(action_type), hold_date=submission_hold_date)
    files = {'SUBMISSION': ('submission.xml', xml_content, 'text/xml')}

    if study is None and samples is None:
        raise RuntimeError("Please ensure that either the Study file or the sample files are included for the ENA submission.")

    if study is not None:
        study_xml = study.toXml()
        _write_xml_to_file('study.xml', study_xml)
        files["PROJECT"] = ('project.xml', study_xml, 'text/xml')

    if samples is not None:
        samples_xml = samples.toXml()
        _write_xml_to_file('samples.xml', samples_xml)
        files['SAMPLE'] = ('samples.xml', samples_xml, 'text/xml')

    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)

    _write_xml_to_file('response.xml', response.content)

    if response.status_code != 200:
        raise RuntimeError(f'Error from ENA server: {response.status_code} - {response.reason}')

    return response.content

def _create_cancellation_xml(target_accession: str) -> str:
    submission = Element('SUBMISSION')
    actions = SubElement(submission, 'ACTIONS')
    action_element = SubElement(actions, 'ACTION')
    cancel = SubElement(action_element, 'CANCEL')
    cancel.set('target', target_accession)
    return tostring(submission, encoding='unicode', method='xml')

def cancel_ena_submission(accession_number: str, dev: bool = True) -> bytes:
    '''
    Function to cancel a submission to the ENA server. Please note that the CANCEL
    action will be propagated from studies to all associated experiments and analyses,
    and from experiments to all associated runs.

    Args:
        accession_number: str
                         Points to the object that is being canceled.
        dev: bool
             Indicates whether the data cancellation should be sent to the development server. 
             Set to True by default. If False, the cancellation will be sent to the production server.
    Returns:
        submission_receipt: bytes
               Qiime artifact containing an XML response from the ENA server.
    '''

    username = os.getenv('ENA_USERNAME')
    password = os.getenv('ENA_PASSWORD')

    if username is None:
        raise RuntimeError('Missing ENA_USERNAME, make sure it is set as an environment variable.')
    if password is None:
        raise RuntimeError('Missing ENA_PASSWORD, make sure it is set as an environment variable.')

    xml_content = _create_cancellation_xml(target_accession=accession_number)
    files = {'SUBMISSION': ('submission.xml', xml_content, 'text/xml')}

    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)

    _write_xml_to_file('response.xml', response.content)

    if response.status_code != 200:
        raise RuntimeError(f'Error from ENA server: {response.status_code} - {response.reason}')

    return response.content

def _write_xml_to_file(filename: str, content: bytes):
    with open(filename, 'wb') as f:
        f.write(content)


def _parse_all_acccession(
        xml_response: bytes
):
    root = ET.fromstring(xml_response)
    samples_accessions = [sample.get('accession') for sample in root.findall('SAMPLE')]
    project_accessions = [project.get('accession') for project in root.findall('PROJECT')]
    combined_accessions = samples_accessions + project_accessions
    
    return combined_accessions

def _get_submission_status(xml_content: bytes) -> str:
    root = ET.fromstring(xml_content)
    submission_status = root.get('success')
    
    return submission_status

    

def cancel_whole_ena_submission(
        ctx,
        submission_receipt,
        dev = True
):
    '''
    bla bla
    Args:
        submission_receipt: bytes
               Qiime artifact containing an XML response from the ENA server.
    '''
    cancel_ena_submission = ctx.get_action('ena_uploader','cancel_ena_submission')

    res = dict()
    accessions_to_cancel = _parse_all_acccession(submission_receipt)
    for AN in accessions_to_cancel:
        response = cancel_ena_submission(AN,dev)
        status   = _get_submission_status(response)
        res[AN] = status
    df = pd.DataFrame(list(res.items()), columns=['Accession', 'Status'])

    return df



    