import unittest
import pandas as pd
import os
from parameterized import parameterized
import xml.etree.ElementTree as ET
from ena_uploader import  _parseExperimentSetFromTsv, _ExperimentSetFromListOfDicts

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

    INPUT1 = _parseExperimentSetFromTsv(fpath("data/test_experiment1.tsv"))
    INPUT2 = _parseExperimentSetFromTsv(fpath("data/test_experiment2.tsv"))

 


    exp_res1 = ET.parse(fpath('data/test_experiment1.xml'))
    exp_res2 = ET.parse(fpath('data/test_experiment2.xml'))



    @parameterized.expand([ (INPUT1,exp_res1),
                            (INPUT2,exp_res2)
                           ])
    
    def test_xml_structure(self,data,expected_res):
        experiment_xml =  _ExperimentSetFromListOfDicts(data).to_xml_element()
        #print(ET.tostring(experiment_xml, encoding='utf-8'))
        self.assertXmlEqual(experiment_xml,expected_res)


if __name__ == "__main__":
     unittest.main()




