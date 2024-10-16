from summarization import Summarizer
import os
import pandas as pd
import torch
import yfinance as yf
from xml.etree import ElementTree as ET
from datetime import datetime,timedelta

import warnings
warnings.filterwarnings("ignore")

class IndexProcessor:
    def __init__(self):
        pass

    @staticmethod
    def get_stock_info(ticker_symbol, time):
        open_price,close_price, high_price, low_price = None, None, None, None

        try:
            ticker = yf.Ticker(ticker_symbol)

            date_str = time
            date_format = "%A, %B %d, %Y %I:%M %p %Z"
            datetime_obj = datetime.strptime(date_str, date_format)

            formatted_date = datetime_obj.strftime("%Y-%m-%d")
            datetime_obj_plus_one = datetime_obj + timedelta(days=1)
            # print(formatted_date)
            data = ticker.history(start=formatted_date, end=datetime_obj_plus_one)

            if not data.empty:
                open_price =  data['Open'].iloc[0]
                close_price = data['Close'].iloc[0]
                high_price = data['High'].iloc[0] 
                low_price = data['Low'].iloc[0]
            else:
                print("No data available for the specified date.")
        except Exception as e:
            print("An error occurred:", str(e))

        return open_price,close_price, high_price, low_price
    
    def add_index_prices_to_xml(self, root):
        print("processing header")
        header = root.find("header")
        
        if header is not None:
            time = header.find("time").text
            sp_open_price = ET.SubElement(header, "S_P500_open")
            sp_close_price = ET.SubElement(header, "S_P500_close")
            sp_open_price.text = format(self.get_stock_info("^GSPC", time)[0], ".6f")
            sp_close_price.text = format(self.get_stock_info("^GSPC", time)[1], ".6f")
            
            kbw_open_price = ET.SubElement(header, "KBWBankIndex_open")
            kbw_close_price = ET.SubElement(header, "KBWBankIndex_close")
            kbw_open_price.text = format(self.get_stock_info("^BKX", time)[0], ".6f")
            kbw_close_price.text = format(self.get_stock_info("^BKX", time)[1], ".6f")
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
        root = self.add_index_prices_to_xml(root)

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
    ip = IndexProcessor()
    # xml_file_path = "sample_output/BK-Q1-2020.xml"
    # ip.process_file("xml/BK-Q1-2018.xml")
    ip.process_folder("xml")