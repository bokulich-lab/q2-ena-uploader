import pandas as pd
import xml.etree.ElementTree as ET

class Run:
    def __init__(self,
                 alias = None,
                 refname = None,
                 files = {}
            ):
        self.alias = alias
        self.refname = refname
        self.files = files


    def to_xml_element(self):

        run_element = ET.Element("RUN", {'alias': self.alias})
        ET.SubElement(run_element,'EXPERIMENT_REF',{'refname' : self.refname })
        data_block = ET.SubElement(run_element,"DATA_BLOCK")
        files_element = ET.SubElement(data_block,'FILES')       

        for filename, checksum in zip(self.files['filename'], self.files['checksum']):
            ET.SubElement(files_element,'FILE',{ 'filename': filename,
                                                                'filetype': 'fastq',
                                                                'checksum_method': "MD5",
                                                                'checksum': checksum }
                                    )

        tree = ET.ElementTree(run_element)
        return run_element


def _runFromDict(rowDict):
    run_set_root = ET.Element('RUN_SET')
    kwArgs = {}
    for alias in rowDict:
        kwArgs['alias'] = 'run_'+ alias
        kwArgs['refname'] = 'exp_'+ alias
        kwArgs['files'] = rowDict[alias]
        run_element = Run(**kwArgs)
        run_set_root.append(run_element.to_xml_element())
        xml_bytes = ET.tostring(run_set_root, encoding='utf-8', xml_declaration=True)

    return xml_bytes

        





        