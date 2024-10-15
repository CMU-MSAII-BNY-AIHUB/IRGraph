import whisper
import os
import pandas as pd
import torch
from xml.etree import ElementTree as ET
import nltk
import warnings
import numpy as np
import re
import pytz
from datetime import datetime,timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import yfinance as yf
import json
nltk.download('punkt')
warnings.filterwarnings("ignore")

from configparser import ConfigParser
from pathlib import Path
import difflib
import re
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR =Path.cwd().parent
print(BASE_DIR)
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")
POLYGON_KEY = CONFIG.get("UPSTREAM", "polygon_api_key")


# audio_path = "recording"
# audio_file = "The Bank of New York Mellon Corporation (NYSE_BK) Apr-16-2024 - Audio.mp3"
# store_path = "S2T"
# store_S2T = "S2T/BK-Q1-2024-S2T.json"
# xml_path = "xml"
# # xml_file = "BK-Q1-2024.xml"
# xml_file = "BK-Q1-2024.xml"
# output_file = "BK-Q1-2024_timestamp.xml"
# stock_folder = "stock"

class TimeStampStockProcessor():
    def __init__(self):
        self.model = whisper.load_model("base")
        self.xml_file = ""
        self.result = ""
        self.global_time = []
        self.global_price = []

    def audio2text(self, audio_path,audio_file):
        print("whisper model processing takes about 10mins per file")
        self.result = self.model.transcribe(os.path.join(audio_path, audio_file))
        self.store_audio2text_result()
        return self.result
    
    def store_audio2text_result(self, store_path="S2T", store_S2T=""):
        if store_S2T == "":
            store_S2T = self.xml_file.replace(".xml", "-S2T.json")
        if not os.path.exists(store_path):
            os.makedirs(store_path)
        with open(os.path.join(store_path,store_S2T), 'w') as f:
            json.dump(self.result, f)
        print(f"Store file in {store_S2T} under {store_path}")
    
    def load_audio2text_result(self, store_path="S2T", store_S2T=""):
        if store_S2T == "":
            store_S2T = self.xml_file.replace(".xml", "-S2T.json")
        with open(os.path.join(store_path,store_S2T), 'r') as file:
            self.result = json.load(file)
        print("Load file successfully!")
        return self.result
    
    def check_audio2text_result(self):
        if self.result == "":
            print("Result is empty. Please load existing file or run model processing")
        for segment in self.result["segments"]:
            print(f"Start: {segment['start']}s, End: {segment['end']}s, Text: {segment['text']}")
    
    def find_best_match(self, original_text, transcribed_segments):
        matcher = difflib.SequenceMatcher(None, original_text, transcribed_segments)
        match = matcher.find_longest_match(0, len(original_text), 0, len(transcribed_segments))
        return original_text[match.a: match.a + match.size]
    
    def parse_time(self, time_str):
    
        return datetime.strptime(time_str, '%A, %B %d, %Y %I:%M %p %Z')

    def timeAndTicker(self, root):
        time_element = root.find(".//header/time")
        if time_element is not None:
            time_element = self.parse_time(time_element.text)
        ticker =  root.find(".//header/ticker").text
        return time_element, ticker
    
    def preprocess_text(self, text):

        return re.sub(r'\W+', ' ', text.lower()).strip()

    def calculate_similarity(self, text1, text2):
        
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([text1, text2])
        return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    
    def split_text_into_sentences(self, text):

        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        return tokenizer.tokenize(text)
    
    def find_most_similar_sentence(self, sentence, segments):
        vectorizer = TfidfVectorizer()

        max_similarity = 0
        best_segment = None
        best_index = -1
        target_length = len(self.preprocess_text(sentence))

        
        for start_index in range(len(segments)):
            combined_text = ""
            for end_index in range(start_index, len(segments)):
                combined_text += " " + segments[end_index]['text']
                combined_length = len(self.preprocess_text(combined_text))


                if combined_length < target_length * 1.5 or (target_length< 10 and combined_length < target_length * 56):  # 允许一定的长度超出
                    processed_combined_text = self.preprocess_text(combined_text)
                    all_texts = [self.preprocess_text(sentence), processed_combined_text]
                    tfidf_matrix = vectorizer.fit_transform(all_texts)
                    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                    # print(similarity)
                
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_segment = segments[end_index]
                        best_index = end_index
                else:
                    break  
        
        return best_segment, max_similarity, best_index
    
    def get_last_two_sentences(self, text):

        sentences = self.split_text_into_sentences(text)
        # Combine the last two sentences, handle texts with less than two sentences.
        last_two_sentences = " ".join(sentences[-2:]) if len(sentences) >= 2 else " ".join(sentences)
        return last_two_sentences
    

    def convert_gmt_to_et(self, gmt_time):
    
        # print(f"gmt_time: {gmt_time}") 
        if gmt_time.tzinfo is None or gmt_time.tzinfo.utcoffset(gmt_time) is None:
            gmt_timezone = pytz.timezone('GMT')
            gmt_time = gmt_timezone.localize(gmt_time)  # 给 naive datetime 设置 GMT 时区

        et_timezone = pytz.timezone('America/New_York')
        et_time = gmt_time.astimezone(et_timezone)  # 转换到 ET 时区
        # print(f"et_time: {et_time}")  
        return et_time

    def load_daily_stock_data(self, ticker, date):

        start_date = date
        end_date = pd.to_datetime(date).date() + pd.Timedelta(days=1)
        data = yf.download(ticker, start=start_date, end=end_date, interval='1m')
        return data
    
    def get_specific_data(self, specific_time, stock_data):
        specific_time = pd.to_datetime(specific_time)  # datetime obj
        # print(specific_time)
        specific_data = None
        if specific_time in stock_data.index:
            specific_data = stock_data.loc[specific_time]
            # print(specific_data)
        else:
            print("No data available for the specified time.")
        return specific_data

    def round_time_to_nearest_minute(self, dt):

        # rounding, if more tham 30s, add a minute
        new_minute = dt + timedelta(minutes=1) if dt.second >= 30 else dt
        return new_minute.replace(second=0, microsecond=0)
    
    def add_presentation_stockprice_to_xml(self, root, time, stock_data, SP500_data, KBW_data, result):
        """
        Add summaries to the XML file based on the section presentation.
        
        Args:
            root: ElementTree of the transcript
        """
        
        print("processing presentation section")
        # Assume result is accessible and contains the whisper_segments
        whisper_segments = result["segments"]
        prev_time = None
        for statement_element in root.findall(".//statement"):
            speaker_element = statement_element.find("speaker")
            text_element = speaker_element.find("text")
            text = text_element.text.strip()

            last_sentence = self.get_last_two_sentences(text)

            best_segment, best_similarity, best_index = self.find_most_similar_sentence(last_sentence, whisper_segments)

            # Print the best matching segment's text, similarity score, and times
            # print("Target sentence: ", last_sentence)
            # print("Best Matching Segment:", best_segment['text'])
            # print("Similarity Score:", best_similarity)
            # print(f"Start Time: {best_segment['start']}s, End Time: {best_segment['end']}s")
            
            
            end_time_gmt = time + timedelta(seconds=best_segment['end'])
            rounded_end_time_gmt = self.round_time_to_nearest_minute(end_time_gmt)
            end_time_et = self.convert_gmt_to_et(rounded_end_time_gmt)
            stock_time_str = end_time_et.strftime('%Y-%m-%d %H:%M:%S')
            stock_price = self.get_specific_data(stock_time_str, stock_data)
            SP500 = self.get_specific_data(stock_time_str, SP500_data)
            KBW = self.get_specific_data(stock_time_str, KBW_data)
            # print(f"Global time: {end_time_gmt}")
            # print(f"stock_data: ", stock_data)
            # print(stock_data)
            # print("----------------------------------------------------")
            timestamp_element = ET.SubElement(text_element, "timeStamp")

            timestamp_element.text = end_time_gmt.strftime('%H:%M:%S')
            stock_element = ET.SubElement(text_element, "stock_price")
            stock_element.text = f"{stock_price['Close']:.6f}"
            S_P500_element = ET.SubElement(text_element, "S_P500")
            
            S_P500_element.text = f"{SP500['Close']:.6f}" 
            KBW_element = ET.SubElement(text_element, "KBW")
            KBW_element.text = f"{KBW['Close']:.6f}"
            self.global_time.append(end_time_et)
            self.global_price.append(stock_price)

            # if "[" in text:
            #     print("\nTrigger\n")
            #     ending_text = text.split(']')[-1]
            #     sentence = split_text_into_sentences(ending_text)[0]
            #     # print(f"ending text: {sentence}")
            #     best_segment, best_similarity,max_index = find_most_similar_sentence(sentence, whisper_segments[i:])
            #     # print("Best Matching Segment:", best_segment['text'])
            #     # print("Similarity Score:", best_similarity)
            #     # print(whisper_segments[max_index]["text"], whisper_segments[i+max_index]["text"])
            #     i = i+max_index
            #     start_index = i
            #     processed_paragraph = preprocess_text(ending_text)

            # while i < len(whisper_segments):
            #     current_text += " " + whisper_segments[i]['text']
            #     new_processed_text = preprocess_text(current_text)
            #     similarity = calculate_similarity(processed_paragraph, new_processed_text)
            #     print(similarity)
            #     if similarity > max_similarity:
            #         max_similarity = similarity
            #         best_match_text = current_text
            #         i += 1
                    
            #     elif similarity > 0.7 and similarity < max_similarity and abs(len(current_text) - len(processed_paragraph))< 30:
            #         start_index = i
            #         break
            #     else:
            #         i +=1
            # print(f"origin Text: {processed_paragraph}")
            # print(f"Matched Text: {best_match_text}")
            # print(f"Start Time: {whisper_segments[start_index]['start']}s, End Time: {whisper_segments[i]['end']}s")    
            # print("----------------------------------------------------")

            # # Use summarizer to get the summary for the text
            # summary = self.summarizer.summarize(text, "statement")
            # # Create and append the summary tag
            # summary_element = ET.SubElement(text_element, "summary")
            # summary_element.text = summary
        return root
    
    def add_QA_stockprice_to_xml(self, root, time, stock_data, SP500_data, KBW_data,result):
        """
        Add summaries to the XML file based on the section Question and Answer.
        
        Args:
            root: ElementTree of the transcript
        """
        print("processing QA section")
        whisper_segments = result["segments"]
        # Find the <section name="Question and Answer"> section
        qa_section = root.find("./body/section[@name='Question and Answer']")

        # Iterate over the elements within the section 
        text_type = ""
        prev_time = None
        for element in qa_section.iter():
            
            # 
            if element.tag == "transition" or element.tag=="ending":
                text_type = "transition"
                
            elif "question" in element.tag.lower():
                text_type = "question"
                
            elif "answer" in element.tag.lower():
                text_type = "answer"
                
                

            if element.tag == 'text':

                if text_type == "question":

                    text = ""
                    if element.text is None:
                        print("There is None text in Q&A")
                        print("_________________________________________")
                    else:
                        text = element.text.strip()
                    

                    last_sentence = self.get_last_two_sentences(text)

                    best_segment, best_similarity, best_index = self.find_most_similar_sentence(last_sentence, whisper_segments)

                    # Print the best matching segment's text, similarity score, and times
                    # print("Target sentence: ", last_sentence)
                    # print("Best Matching Segment:", best_segment['text'])
                    # print("Similarity Score:", best_similarity)
                    # print(f"Start Time: {best_segment['start']}s, End Time: {best_segment['end']}s")
                    if best_segment == None:
                        timestamp_element = ET.SubElement(element, "timeStamp")
                        timestamp_element.text = "None"
                        stock_element = ET.SubElement(element, "stock_price")
                        stock_element.text = "None"
                        continue
                     
                    end_time_gmt = time + timedelta(seconds=best_segment['end'])
                    rounded_end_time_gmt = self.round_time_to_nearest_minute(end_time_gmt)
                    end_time_et = self.convert_gmt_to_et(rounded_end_time_gmt)
                    stock_time_str = end_time_et.strftime('%Y-%m-%d %H:%M:%S')
                    stock_price = self.get_specific_data(stock_time_str, stock_data)
                    SP500 = self.get_specific_data(stock_time_str, SP500_data)
                    KBW = self.get_specific_data(stock_time_str, KBW_data)
                    
                    timestamp_element = ET.SubElement(element, "timeStamp")
                    timestamp_element.text = end_time_gmt.strftime('%H:%M:%S')
                    stock_element = ET.SubElement(element, "stock_price")
                    stock_element.text = f"{stock_price['Close']:.6f}"
                    S_P500_element = ET.SubElement(element, "S_P500")
                    S_P500_element.text = f"{SP500['Close']:.6f}" 
                    KBW_element = ET.SubElement(element, "KBW")
                    KBW_element.text = f"{KBW['Close']:.6f}"
                    self.global_time.append(end_time_et)
                    self.global_price.append(stock_price)

        return root
    
    def get_stock_data(self, stock_folder, ticker, time):
        if not os.path.exists(stock_folder):
            os.makedirs(stock_folder)
        stock_data = self.load_daily_stock_data(ticker, self.convert_gmt_to_et(time))
        SP500_data = self.load_daily_stock_data("^GSPC",self.convert_gmt_to_et(time))
        BKX_data = self.load_daily_stock_data("^BKX",self.convert_gmt_to_et(time))
        stock_data.to_csv(os.path.join(stock_folder, self.xml_file.replace("xml","csv")))
        SP500_data.to_csv(os.path.join(stock_folder, self.xml_file.replace(".xml","-SP500.csv")))
        BKX_data.to_csv(os.path.join(stock_folder, self.xml_file.replace(".xml","-KBW.csv")))
        print(f"data store under {stock_folder}")
        return stock_data, SP500_data, BKX_data
    
    def load_stock_data(self, stock_folder = "stock"):
        """
        Loads stock data, SP500 data, and BKX data from CSV files.

        Args:
            stock_folder (str): Path to the folder containing the CSV files.
            xml_file (str): The original XML file name (used for naming the CSVs).

        Returns:
            tuple: DataFrames for stock data, SP500 data, and BKX data.
        """
        # Generate the expected file paths for the stock, SP500, and BKX data
        stock_csv = os.path.join(stock_folder, self.xml_file.replace("xml", "csv"))
        sp500_csv = os.path.join(stock_folder, self.xml_file.replace(".xml", "-SP500.csv"))
        bkx_csv = os.path.join(stock_folder, self.xml_file.replace(".xml", "-KBW.csv"))

        try:
            # Load the data from the CSV files into pandas DataFrames
            stock_data = pd.read_csv(stock_csv, index_col='Datetime', parse_dates=True)
            SP500_data = pd.read_csv(sp500_csv, index_col='Datetime', parse_dates=True)
            BKX_data = pd.read_csv(bkx_csv, index_col='Datetime', parse_dates=True)
        except FileNotFoundError:
            # If files are not found, call get_data function to retrieve default data
            print(f"File(s) not found: {self.xml_file}. Loading default data using get_stock_data().")
            stock_data, SP500_data, BKX_data = self.get_stock_data()

        return stock_data, SP500_data, BKX_data


    def plot_stock_data(self, stock_data):
        """
        Plots the stock data for open, close, high, and low prices.

        Args:
            stock_data (DataFrame): DataFrame containing the stock data with datetime index.
        """
        # Check if data is empty
        if stock_data.empty:
            print("No data available to plot.")
            return

        # Ensure the index is a datetime index
        stock_data.index = pd.to_datetime(stock_data.index)

        plt.figure(figsize=(10, 6))
        plt.plot(stock_data.index, stock_data['Open'], label='Open', color='green')
        plt.plot(stock_data.index, stock_data['Close'], label='Close', color='red')
        plt.plot(stock_data.index, stock_data['High'], label='High', color='black')
        plt.plot(stock_data.index, stock_data['Low'], label='Low', color='blue')

        plt.title('Stock Prices')
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)  # Rotate dates for better visibility
        plt.tight_layout()  # Adjust subplots to give some padding

        plt.show()
    
    def create_and_sort_dataframe(self):
        df = pd.DataFrame({
            'Time': self.global_time,
            'Price': [price['Close'] for price in self.global_price]  
        })
        df['Time'] = pd.to_datetime(df['Time']) 
        df.sort_values('Time', inplace=True)  
        return df


    def plot_stock_prices(self,df):
        plt.figure(figsize=(10, 5))
        plt.plot(df['Time'], df['Price'], marker='o', linestyle='-', color='b')
        plt.title('Stock Prices Over Time')
        plt.xlabel('Time')
        plt.ylabel('Price (USD)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    

    def process_file(self, audio_path,audio_file, stock_folder, xml_path, xml_file, has_stock_data):
        self.xml_file = xml_file
        try:
            self.load_audio2text_result()
        except FileNotFoundError:
            self.audio2text(audio_path,audio_file)

        tree = ET.parse(os.path.join(xml_path,xml_file))
        root = tree.getroot()
        time, ticker = self.timeAndTicker(root)
        print(time, ticker)
        if has_stock_data:
            stock_data, SP500_data, BKX_data = self.load_stock_data(stock_folder)

        else:
            stock_data, SP500_data, BKX_data = self.get_stock_data(stock_folder, ticker, time)
        root = self.add_presentation_stockprice_to_xml(root,time,stock_data, SP500_data, BKX_data, self.result)
        root = self.add_QA_stockprice_to_xml(root, time, stock_data, SP500_data, BKX_data, self.result)
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        print(f"Processed {xml_file}")
        self.plot_stock_data(stock_data)
        
        df = self.create_and_sort_dataframe()
        self.plot_stock_prices(df)


if __name__ == "__main__":
    processor = TimeStampStockProcessor()
    processor.process_file("recording", "The Bank of New York Mellon Corporation (NYSE_BK) Jul-12-2024 - Audio.mp3", "stock", "xml", "BK-Q1-2024.xml", True)