import pandas as pd
from collections import defaultdict
import re
import xml.etree.ElementTree as ET

class Run:
    def __init__(self,
                 alias = None,
                 center_name = None,
                 experiment_ref = None,
                 files = []
            ):
        self.alias = alias
        self.center_name = center_name
        self.experiment_ref = experiment_ref
        self.files = files


    def to_xml_element(self):
        root = ET.Element("RUN_SET")
        if self.alias is None:
            raise ValueError("Run alias must have a value for a raw data submission.")
        elif self.center_name is  None:
            run_element = ET.SubElement(root,"RUN", {'alias': self.alias})
        else:
            run_element = ET.SubElement(root,"RUN", {'alias': self.alias , 'center_name': self.center_name})


        if self.experiment_ref is  None:
            raise ValueError("Experiment reference must be present for a run submission.")
        else:
            ET.SubElement(run_element,'EXPERIMENT_REF').text = self.experiment_ref
        
        if len(self.files) == 0:
            raise ValueError("File descriptors must included in a run submission.")
        else:
            data_block = ET.SubElement(run_element,"DATA_BLOCK")
            files_element = ET.SubElement(data_block,'FILES')
            
            files_dicts = defaultdict(dict)
            suffix_pattern = re.compile(r'([a-zA-Z_]+)(\d+)$')
            for key, value in self.files.items():
                match = suffix_pattern.match(key)
                if match:
                    preffix = match.group(1)
                    suffix = match.group(2)
                    files_dicts[suffix][preffix] = value
            sorted_files = list(files_dicts.values())      
            for file in sorted_files:
                file_element = ET.SubElement(files_element,'FILE',{'filename': file['filename'],
                                                                  'filetype': file['filetype'],
                                                                  'checksum_method': file['checksum_method'],
                                                                  'checksum': file['checksum']}
                )
                if file.get('read_type') is not None:
                    values = file['read_type'].split('|')
                    for value in values:
                        ET.SubElement(file_element,'READ_TYPE').text = value
        tree = ET.ElementTree(root)
        return tree


def _runFromRawDict(rowDict):
    specialAttributes = {"alias","center_name","experiment_ref"}
    kwArgs = {k.strip():v.strip() for k,v in rowDict.items() if k.strip() in specialAttributes}
    kwArgs['files'] = { k:v for k,v in rowDict.items() if k.startswith('file') or k.startswith('checksum') or k.startswith('read_type')}
    return Run(**kwArgs)




        