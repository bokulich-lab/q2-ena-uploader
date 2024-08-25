import pandas as pd
import os
import hashlib
import requests 
from enum import Enum
from .experiment import _runFromDict
from q2_types.per_sample_sequences import \
    (CasavaOneEightSingleLanePerSampleDirFmt)

from xml.etree.ElementTree import Element, SubElement, tostring
from ena_uploader.types._types_and_formats import (
    ENAMetadataExperimentFormat, ENAMetadataExperimentDirFmt,ENAMetadataExperiment,
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


def calculate_md5(file_path):
    # Create an md5 hash object
    hash_md5 = hashlib.md5()
    
    # Open the file in binary mode and read it in chunks
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    
    # Return the hexadecimal digest of the hash
    return hash_md5.hexdigest()


def uploadReadsToEna(demux: CasavaOneEightSingleLanePerSampleDirFmt,
                     experiment: ENAMetadataExperimentFormat = None,
                     submission_hold_date: str = '',
                     action_type: str = 'ADD',
                     dev: bool = True
                     ) -> bytes:
    
    '''
    Function to sumbmit metedata of the experiments to ENA.
    Args:
        experiment : Metadata
                Qiime artifact containing a tsv file with the experiment atrributes.
        demux: 
             'The demultiplexed sequence data to be quality filtered.'

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
                Qiime artifact containing an XML response of ENA server.
    '''
    df = demux.manifest
  
    parsed_data = {}
    for row in df.itertuples(index=True, name ='Pandas'):
        sample_id = row.Index
        alias = str(sample_id)
        parsed_data[alias]={'filename' : [],
                            'checksum' :[]
        }

        filename = str(row.forward).split('/')[-1]
        checksum = calculate_md5(str(row.forward))
        parsed_data[alias]['filename'].append(filename)
        parsed_data[alias]['checksum'].append(checksum)

        if not df['reverse'].isna().all():
            filename = str(row.reverse).split('/')[-1]
            checksum = calculate_md5(str(row.reverse))
            parsed_data[alias]['filename'].append(filename)
            parsed_data[alias]['checksum'].append(checksum)

    data_for_df = []

    for alias, values in parsed_data.items():
        data_for_df.append({
            'alias': alias,
            'filename': values['filename'],
            'checksum': values['checksum']
    })      

    run_xml = _runFromDict(parsed_data) 

    username = os.getenv('ENA_USERNAME')
    password = os.getenv('ENA_PASSWORD')

    if username is None or password is None:
        raise RuntimeError('Missing username or password, ' +
                           'make sure ENA_USERNAME and ENA_PASSWORD env vars are set')

    xml_content = _create_submission_xml(strToActionType(action_type), hold_date = submission_hold_date)
    files = {'SUBMISSION': ('submission.xml',  xml_content, 'text/xml')}


    if experiment is None:
        raise RuntimeError("Please ensure that the Experiment file is included for the ENA submission.")

    if experiment is not None:
        experiment_xml = experiment.toXml()
        with open('experiment', 'w') as f1:
            f1.write(str(experiment_xml))
        files["EXPERIMENT"] = ('expetiment.xml', experiment_xml, 'text/xml')
        with open('run','w') as f2:
            f2.write(str(run_xml))
        files['RUN'] = ('run.xml',run_xml,'text/xml')



    url = DEV_SERVER_URL if dev else PRODUCTION_SERVER_URL
    response = requests.post(url, auth=(username, password), files=files)

    with open('response.xml', 'wb') as f:
          f.write(response.content)
        
    return response.content









    






