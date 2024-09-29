import pandas as pd
import xml.etree.ElementTree as ET
import csv

class Library:
    def __init__(
            self,
            library_strategy = None,
            library_source = None,
            library_selection = None,
            library_layout = None,
            library_nominal_length = None, 
            library_nominal_sdev = None,
            library_construnction_protocol = None
    ):
        self.library_strategy = library_strategy
        self.library_source = library_source
        self.library_selection = library_selection
        self.library_layout = library_layout
        self.nominal_length = library_nominal_length
        self.nominal_sdev = library_nominal_sdev
        self.library_construnction_protocol = library_construnction_protocol
    
    def to_xm_element(self):
        if self.library_strategy is None:
            raise ValueError("Library strategy must be present for an experiment submission.")
        else:
            root = ET.Element('LIBRARY_DESCRIPTOR')
            ET.SubElement(root,'LIBRARY_STRATEGY').text = str(self.library_strategy)
        if self.library_source is None:
            raise ValueError("Library source must be present for an experiment submission.")
        else:
            ET.SubElement(root,'LIBRARY_SOURCE').text = str(self.library_source)
        if self.library_selection is None:
            raise ValueError("Library selection must be present for an experiment submission.")
        else:
            ET.SubElement(root,'LIBRARY_SELECTION').text = str(self.library_selection)
        if self.library_layout is None:
            raise ValueError("Library layout must be present for an experiment submission.")
        else:
            if self.library_layout.lower() == 'paired':
                if self.nominal_length is None or self.nominal_sdev is None:
                    raise ValueError("Paired library layout requires nominal_leght and nominal_sdev values present for an experiment submission.")
                else:
                    library_layout_el = ET.SubElement(root,"LIBRARY_LAYOUT")
                    ET.SubElement(library_layout_el,"PAIRED",{'NOMINAL_LENGTH': self.nominal_length},{"NOMINAL_SDEV": self.nominal_sdev})
            else:
                library_layout_el = ET.SubElement(root,"LIBRARY_LAYOUT")
                ET.SubElement(library_layout_el,"SINGLE")    

        if self.library_construnction_protocol is not None:
            ET.SubElement(root, 'LIBRARY_CONSTRUCTION_PROTOCOL').text =str(self.library_construnction_protocol)
        
        return root


class Experiment:
    def __init__(self,
                 title = None,
                 study_ref = None,
                 sample_description = None,
                 platform= None, 
                 instrument_model = None,
                 library_attributes = [],
                 attributes = []):
        self.title = title
        self.study_ref = study_ref
        self.sample_description = sample_description
        self.platform = platform
        self.instrument_model = instrument_model
        self.library_attributes = library_attributes
        self.attributes = attributes
    
    def to_xml_element(self):
        
        if self.sample_description is None:
            raise ValueError("Sample reference id must be present for an experiment submission.")
        else:
            root = ET.Element("EXPERIMENT",{'alias': 'exp_'+ str(self.sample_description) })
            
        if self.title is not None:    
            ET.SubElement(root,'TITLE').text = str(self.title)
        
        if self.study_ref is None:
            raise ValueError("Study reference must be present for an experiment submission.")
        else:
            study_element = ET.SubElement(root,'STUDY_REF',{'refname' : self.study_ref})
        
        design_element = ET.SubElement(root,'DESIGN')
        design_description_element = ET.SubElement(design_element,'DESIGN_DESCRIPTION')

        sample_description = ET.SubElement(design_element, 'SAMPLE_DESCRIPTOR', {'refname' : self.sample_description})
        if len(self.platform) is None:
            raise ValueError("Platform record must be present for an experiment submission.")
        else:
            if self.instrument_model is None:
                raise ValueError("Instrument model record must be present for an experiment submission.")
            else:
                platform_el = ET.SubElement(root,"PLATFORM")
                platform_model =  ET.SubElement(platform_el, self.platform.upper())
                ET.SubElement(platform_model,"INSTRUMENT_MODEL").text = self.instrument_model
        if len(self.library_attributes) == 0:
            raise ValueError('Library descriptors must be present for an experiment submission.')
        else:
            library_tree = Library(**self.library_attributes)
            library_tree_element = library_tree.to_xm_element()
            design_element.append(library_tree_element)

        if len(self.attributes) > 0 :
             attributes_element = ET.SubElement(root,"EXPERIMENT_ATTRIBUTES")
             for el in self.attributes:
                 tag,value = el.split("|")
                 attribute_element = ET.SubElement(attributes_element,"EXPERIMENT_ATTRIBUTE")
                 ET.SubElement(attribute_element,"TAG").text = tag
                 ET.SubElement(attribute_element,"VALUE").text = value
        return root
            
        

class ExperimentSet:
    def __init__(self):
        self.experiments = []

    def add_experiment(self, experiment):
        self.experiments.append(experiment)

    def to_xml_element(self):
        experiment_set_element = ET.Element('EXPERIMENT_SET')
        for experiment in self.experiments:
            experiment_element = experiment.to_xml_element()
            experiment_set_element.append(experiment_element)
        
        return ET.ElementTree(experiment_set_element)
        #return experiment_set_element   

def _experimentFromRowDict(rowDict):
    specialAttributes = {"title", "study_ref","sample_description", "platform", "instrument_model"}
    kwArgs = {k.strip():v.strip() for k,v in rowDict.items() if k.strip() in specialAttributes}
    kwArgs['library_attributes'] = {k:v for k,v in rowDict.items() if k.startswith('library')}
    kwArgs['attributes'] = {k:v for k,v in rowDict.items() if k  not in specialAttributes and not k.startswith('library')}
    return Experiment(**kwArgs)

                
def _ExperimentSetFromListOfDicts(listOfDictionary):
    experimentSet = ExperimentSet()
    for rowDict in listOfDictionary:
        experimentSet.add_experiment(_experimentFromRowDict(rowDict))
    return experimentSet

def _parseExperimentSetFromTsv(filename):
    with open(filename) as csvfile:
        return [d for d in csv.DictReader(csvfile, delimiter='\t')]