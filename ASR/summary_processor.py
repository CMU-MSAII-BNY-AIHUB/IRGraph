from summarization import Summarizer
import os
import pandas as pd
import torch
from xml.etree import ElementTree as ET

import warnings
warnings.filterwarnings("ignore")

class SummaryProcessor:
    def __init__(self):
        self.summarizer = Summarizer()

    def add_presentation_summary_to_xml(self, root):
        """
        Add summaries to the XML file based on the section presentation.
        
        Args:
            root: ElementTree of the transcript
        """
        print("processing presentation section")
        # Iterate through statements and add summary tags
        for statement_element in root.findall(".//statement"):
            speaker_element = statement_element.find("speaker")
            text_element = speaker_element.find("text")
            text = text_element.text.strip()
            if "operator" in speaker_element.text.lower() or len(text) <=25:
                summary_element = ET.SubElement(text_element, "summary")
                summary_element.text = "None"
                continue
            
            
            # Use summarizer to get the summary for the text
            summary = self.summarizer.summarize(text, "statement")
            # Create and append the summary tag
            summary_element = ET.SubElement(text_element, "summary")
            summary_element.text = summary
        return root


    def add_QA_summary_to_xml(self, root):
        """
        Add summaries to the XML file based on the section Question and Answer.
        
        Args:
            root: ElementTree of the transcript
        """
        print("processing QA section")
        # Find the <section name="Question and Answer"> section
        qa_section = root.find("./body/section[@name='Question and Answer']")

        # Iterate over the elements within the section 
        text_type = ""
        for element in qa_section.iter():
            

            if element.tag == "transition" or element.tag=="ending":
                text_type = "transition"
                
            elif "question" in element.tag.lower():
                text_type = "question"
                
            elif "answer" in element.tag.lower():
                text_type = "answer"
                

            if element.tag == 'text':
                if text_type == "transition":
                    continue
                text = ''
                if element.text is None:
                    print("There is None text in Q&A")
                    print("_________________________________________")
                else:
                    text = element.text.strip()
                
                if len(text) <= 25:
                    summary_element = ET.SubElement(element, "summary")
                    summary_element.text = "None"
                else:
                    # Use summarizer to get the summary for the text
                    summary = self.summarizer.summarize(text, text_type)
                    # Create and append the summary tag
                    summary_element = ET.SubElement(element, "summary")
                    summary_element.text = summary

        return root
    
    def process_file(self, xml_file_path: str):
        """
        Process a single XML file by adding summaries to its presentation and Q&A sections.

        Args:
            xml_file_path: Path to the XML file to be processed.
        """
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Add summaries to presentation and Q&A sections
        root = self.add_presentation_summary_to_xml(root)
        root = self.add_QA_summary_to_xml(root)

        # Write the modified XML back to the same file
        tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)
        print(f"Processed {xml_file_path}")
    

    def process_folder(self, folder_path: str):
        """
        Process all XML files within a folder, adding summaries to presentation and Q&A sections.

        Args:
            folder_path: Path to the folder containing XML files to be processed.
        """
        for filename in os.listdir(folder_path):
            if filename.endswith('.xml'):
                print(f"Start summarize {filename}")
                xml_file_path = os.path.join(folder_path, filename)
                self.process_file(xml_file_path)
                print(f"Processed {filename}")
    
if __name__=="__main__":
    sp = SummaryProcessor()
    # xml_file_path = "sample_output/BK-Q1-2020.xml"
    sp.process_file("xml/STT-Q1-2024.xml")
    # sp.process_folder("xml")