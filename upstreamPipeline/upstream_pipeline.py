from neo4j_processor import Neo4jProcessor
from file_processor import FileProcessor
from timeStamp_stock_processor import TimeStampStockProcessor
import argparse
import os
from configparser import ConfigParser
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
# print(BASE_DIR)
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")
OPENAI_KEY = CONFIG.get("UPSTREAM", "openai_api_key")
URI = CONFIG.get("NEO4J", "uri")
PASSWORD = CONFIG.get("NEO4J", "password")
AUTH = ("neo4j", PASSWORD)


def neo4j_import_single_file(file_path):
    neo4j_processor = Neo4jProcessor(URI, AUTH)
    neo4j_processor.process_single_file(file_path)
    print(f"Completed importing {file_path} to Neo4j.")
    neo4j_processor.close()

def neo4j_import_folder(folder_path):
    neo4j_processor = Neo4jProcessor(URI, AUTH)
    neo4j_processor.process_folder(folder_path)
    print(f"Completed importing all files in {folder_path} to Neo4j {URI}.")
    neo4j_processor.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process files for sentiment and emotion analysis and import to Neo4j.")
    parser.add_argument("--file-dir", type=str, required=False, help="Directory containing the files to process.")
    parser.add_argument("--save-dir", type=str, required=False, help="Directory to save processed files.")
    parser.add_argument("--filename", type=str, required=False, help="Name of a specific file to process.")
    parser.add_argument("--generate-from-rar", action="store_true", help="Flag to indicate if generate directly based on the xml.rar we provide")
    parser.add_argument("--add-stock",action="store_true", help="Flag to indicate if user want to use ASR to add timeStamp and minute level stock price. If so, please add audio folder and audio name")
    parser.add_argument("--audio-dir", type=str, required=False, help="Directory containing the audio file.")
    parser.add_argument("--audio-file", type=str, required=False, help="Name of a specific audio file to process.")
    parser.add_argument("--stock-dir", type=str, required=False, help="Directory to save or read stock information.")
    parser.add_argument("--has-stock-data", action="store_true", help="Flag to indicate if we already have minute level stock data")
    parser.add_argument("--clean_db", action="store_true", help="add the flag to clean the current database")
    args = parser.parse_args()

    #process_file(self, audio_path,audio_file, stock_folder, xml_path, xml_file, has_stock_data):
    #"recording", "The Bank of New York Mellon Corporation (NYSE_BK) Jul-12-2024 - Audio.mp3", "stock", "xml", "BK-Q1-2024.xml", False
    processor = FileProcessor(file_dir=args.file_dir, save_dir=args.save_dir, filename=args.filename)
    if args.generate_from_rar:
        print(args.generate_from_rar)
        neo4j_import_folder(args.save_dir)
    else:
        if args.filename:
            print(f"processing single file: {args.filename}")
            file_name = args.filename
            file_name = processor.process_single_file(args.save_dir)

            if args.add_stock:
                print(f"Generate time stamp for file: {file_name}")
                stock_processor = TimeStampStockProcessor()
                stock_processor.process_file(args.audio_dir, args.audio_file,  args.stock_dir, args.save_dir, file_name, args.has_stock_data)
            print(f"neo 4j processing {file_name} on {AUTH}")
            neo4j_import_single_file( file_name)

        else:
            processor.process_all_files()
            neo4j_import_folder(args.save_dir)

'''

Example:
python upstream_pipeline.py --file-dir "transcripts/BK" ^
    --save-dir "xml" ^
        --filename "The Bank of New York Mellon Corporation, Q3 2024 Earnings Call, Oct 11, 2024.rtf" ^
        --add-stock ^
        --audio-dir "recording" ^
        --audio-file "The Bank of New York Mellon Corporation (NYSE_BK) Oct-11-2024 - Audio.mp3" ^
        --stock-dir "stock"
        

processor.process_file("recording", "The Bank of New York Mellon Corporation (NYSE_BK) Jul-12-2024 - Audio.mp3", "stock", "xml", "BK-Q1-2024.xml", True)
python upstream_pipeline.py --file-dir "xml" --generate-from-rar

python upstream_pipeline.py --file-dir "transcripts/BK" --save-dir "xml" --filename "The Bank of New York Mellon Corporation, Q2 2024 Earnings Call, Jul 12, 2024.rtf"
python upstream_pipeline.py --file-dir "transcripts" --save-dir "xml"
python upstream_pipeline.py --file-dir "xml" --save-dir "xml" --filename "xml\STT-Q1-2024_timestamp.xml"


clean the data base:
MATCH (n)
DETACH DELETE n
'''