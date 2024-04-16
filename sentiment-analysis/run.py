import sentiment_analysis_xml as SA
import os
from multiprocessing import Pool

def process_file(filename, folder_path):
    if filename.endswith('.xml'):
        xml_file_path = os.path.join(folder_path, filename)
        SA.complete_sentiment_tagging(xml_file_path)

def multi_processing():
    folder_path = 'data/'
    filenames = [filename for filename in os.listdir(folder_path) if filename.endswith('.xml')]
    total_files = len(filenames)
    
    process_file.total_files = total_files
    
    # Use Pool from multiprocessing to create multiple worker processes
    with Pool() as pool:
        pool.starmap(process_file, [(filename, folder_path) for filename in filenames])

def sequential_processing():
    folder_path = 'data/'

    total_files = len([filename for filename in os.listdir(folder_path) if filename.endswith('.xml')])
    file_number = 0

    for filename in os.listdir(folder_path):
        if filename.endswith('.xml'):
            file_number += 1
            xml_file_path = os.path.join(folder_path, filename)
            SA.complete_sentiment_tagging(xml_file_path)
            print(f'------------- Processed file {file_number}/{total_files}: {filename} -------------')

if __name__ == "__main__":
    multi_processing()
    data_total_files = len([filename for filename in os.listdir('data') if filename.endswith('.xml')])
    processed_total_files = len([filename for filename in os.listdir('xml_w_sentiment') if filename.endswith('.xml')])
    print(f"Total original data files: {data_total_files}, Total processed files: {processed_total_files}")