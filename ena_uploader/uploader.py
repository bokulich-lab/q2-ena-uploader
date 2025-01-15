import os
import requests
import sys
import click
from enum import Enum
from xml.etree.ElementTree import Element, SubElement, tostring
from ena_uploader.types._types_and_formats import (
    ENAMetadataSamplesFormat, ENAMetadataSamplesDirFmt,ENAMetadataSamples,
    ENAMetadataStudyFormat, ENAMetadataStudyDirFmt, ENAMetadataStudy,
    ENASubmissionReceiptFormat,ENASubmissionReceiptDirFmt,ENASubmissionReceipt

)

DEV_SERVER_URL =  'https://wwwdev.ebi.ac.uk/ena/submit/drop-box/submit'
PRODUCTION_SERVER_URL = ' https://www.ebi.ac.uk/ena/submit/drop-box/submit'

class ActionType(Enum):
    ADD = "ADD"
    MODIFY = "MODIFY"

def strToActionType(s : str) -> ActionType:
    if s == 'ADD':
        return ActionType.ADD
    elif s == 'MODIFY':
        return ActionType.MODIFY
    raise RuntimeError('Unknown action type {}'.format(s))

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

def uploadToEna(study: ENAMetadataStudyFormat = None, 
                samples: ENAMetadataSamplesFormat = None,
                submission_hold_date: str = '',
                action_type: str = 'ADD',
                dev: bool = True
                ) -> bytes:

    '''
    Function to sumbmit metedata of the study and samples to ENA.
    Args:
        study : Metadata
                Qiime artifact containing a tsv file with the study atrributes.
        samples : Metadata
                Qiime artifact containing a tsv file with the samples metadata attributes.
        username : Str
                 ENA Webin login username
        password : Str
                 ENA Webin login password
        submission_hold_date: Str
                 The release date of the study, on which it will become public along with all submitted data.
                 By default, this date is set to two months after the date of submission. User can 
                 specify any date within two years of the current date.
        action_type : Str
                  2 action types are supported : ADD as a default and MODIFY
        dev : Bool
            True by default. Indicates whether the data submission goes to the development server. If False, the submission 
                goes to the production server. 
    Returns:
        submission_receipt : bytes
                Qiime artifact containing an XML response of  ENA server.
    '''

    username = os.getenv('ENA_USERNAME')
    password = os.getenv('ENA_PASSWORD')

    if username is None or password is None:
        raise RuntimeError('Missing username or password, ' +
                           'make sure ENA_USERNAME and ENA_PASSWORD env vars are set')

    xml_content = _create_submission_xml(strToActionType(action_type), hold_date = submission_hold_date)
    files = {'SUBMISSION': ('submission.xml',  xml_content, 'text/xml')}


    if study is None and samples is None:
        raise RuntimeError("Please ensure that either the Study file or the sample files are included for the ENA submission.")

    if study is not None:
        study_xml = study.toXml()
        with open('study.xml', 'w') as f:
            f.write(str(study_xml))
            files["PROJECT"] = ('project.xml', study_xml, 'text/xml')

 

    if samples is not None:
        samples_xml = samples.toXml()
        with open('samples.xml', 'w') as f:
             f.write(str(samples_xml))
        files['SAMPLE'] = ('samples.xml', samples_xml, 'text/xml')


    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)

    with open('response.xml', 'wb') as f:
        f.write(response.content)
    
    return response.content

def _create_cancalation_xml(target_accession: str) -> str:
    submission = Element('SUBMISSION')
    actions = SubElement(submission, 'ACTIONS')
    action_element = SubElement(actions, 'ACTION')
    cancle = SubElement(action_element, 'CANCEL')
    cancle.set('target', target_accession)
    return tostring(submission, encoding='unicode', method='xml')

    
def cancleENASubmission( accession_number: str, dev: bool = True) -> bytes:
        '''
        Function to cancel a submission to the ENA server. Please note that the CANCEL
        action will be propagated from studies to all associated experiments and analyses,
        and from experiments to all associated runs.

        Args:
            accession_number: Str
                             Points to the object that is being cancelled.
        Dev : Bool
              Indicates whether the data cancellation should be sent to the development server. 
              Set to True by default. If False, the cancellation will be sent to the production server.
                    
        '''

        username = os.getenv('ENA_USERNAME')
        password = os.getenv('ENA_PASSWORD')

        if username is None or password is None:
            raise RuntimeError('Missing username or password, ' +
                           'make sure ENA_USERNAME and ENA_PASSWORD env vars are set')

        xml_content = _create_cancalation_xml(target_accession= accession_number)
        files = {'SUBMISSION': ('submission.xml',  xml_content, 'text/xml')}

        url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
        response = requests.post(url, auth=(username, password), files=files)

        with open('response.xml', 'wb') as f:
            f.write(response.content)
    
        return response.content