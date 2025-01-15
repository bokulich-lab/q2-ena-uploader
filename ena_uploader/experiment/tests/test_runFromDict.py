import unittest
import pandas as pd
import os
from parameterized import parameterized
import xml.etree.ElementTree as ET
from ena_uploader import _runFromDict

def read_run_tsv_to_dict(filename):
    return pd.read_csv(filename,header= None, index_col=0, delimiter='\t' ).squeeze("columns").to_dict() 

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def fpath(fname):
    return os.path.join(THIS_DIR, fname)

def elements_equal(e1, e2):
    if e1.tag != e2.tag: 
        return False
    if e1.text != e2.text: 
        if  e1.text!=None and e2.text!=None :
            return False
    if e1.tail != e2.tail:
        if e1.tail!=None and e2.tail!=None:
            return False
    if e1.attrib != e2.attrib: 
        return False
    if len(e1) != len(e2): 
        return False
    return all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2))

def is_two_xml_equal(tree1, tree2):
    root1 = tree1.getroot()
    root2 = tree2.getroot()
    return elements_equal(root1,root2)


class CustomAssertions:
    def assertXmlEqual(self, xml1,xml2):
        if not is_two_xml_equal(xml1,xml2):
            raise AssertionError('Two xml files are not equal!')


class OptimizationContext_tests(unittest.TestCase,CustomAssertions):

    dict1 =  {
     'alias_1': {
          'filename': ['file1_forward.fastq', 'file1_reverse.fastq'],
          'checksum': ['abc123', 'def456']
        },
     'alias_2': {
        'filename': ['file2_forward.fastq', 'file2_reverse.fastq'],
        'checksum': ['ghi789', 'jkl012']
         }
        }

    dict2 =  {
     'alias_1': {
          'filename': ['file1.fastq'],
          'checksum': ['abc123']
        },
     'alias_2': {
        'filename': ['file2.fastq'],
        'checksum': ['ghi789']
         }
        }

    expected_res_0 = ET.parse(fpath('data/run_1.xml'))
    expected_res_1 = ET.parse(fpath('data/run_2.xml'))

    @parameterized.expand([(dict1,expected_res_0),
                           ])
    def test_xml_structure(self,data,expected_res):
        run =  _runFromDict(data)
        self.assertXmlEqual(run,expected_res)
    


if __name__ == "__main__":
     unittest.main()