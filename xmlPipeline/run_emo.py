import emotion_classification_xml as EC
import os
from multiprocessing import Pool

import nltk
nltk.download('punkt')
nltk.download('stopwords')

def process_file(filename, folder_path):
    if filename.endswith('.xml'):
        xml_file_path = os.path.join(folder_path, filename)
        EC.complete_emotion_tagging(xml_file_path)

def multi_processing():
    folder_path = 'xml_w_sentiment_topic'
    filenames = [filename for filename in os.listdir(folder_path) if filename.endswith('.xml')]
    total_files = len(filenames)
    
    process_file.total_files = total_files
    
    # Use Pool from multiprocessing to create multiple worker processes
    with Pool() as pool:
        pool.starmap(process_file, [(filename, folder_path) for filename in filenames])

if __name__ == "__main__":
    multi_processing()
    data_total_files = len([filename for filename in os.listdir('xml_w_sentiment_topic') if filename.endswith('.xml')])
    processed_total_files = len([filename for filename in os.listdir('xml_w_emotion') if filename.endswith('.xml')])
    print(f"Total original data files: {data_total_files}, Total processed files: {processed_total_files}")