from transcript_parser import TranscriptParser
from sentiment_analysis_processor import SentimentAnalysisProcessor
from emotion_classification_processor import EmotionClassificationProcessor
from summary_processor import SummaryProcessor
from indexInfo_processor import IndexProcessor
import argparse
import os

class FileProcessor:
    def __init__(self, file_dir, save_dir, filename=None):
        self.file_dir = file_dir
        self.save_dir = save_dir
        self.filename = filename
        self.tp = TranscriptParser()
        self.sa_processor = SentimentAnalysisProcessor()
        self.ec_processor = EmotionClassificationProcessor()
        self.su_processor = SummaryProcessor()
        self.index_processor = IndexProcessor()

    def process_single_file(self, save_dir):
        print(f"Processing file: {self.file_dir}")
        file = self.tp.process_file(self.file_dir, self.filename, self.save_dir)
        temp_filename= os.path.join(save_dir, file)
        print(f"Transcript parsing completed. File saved in: {temp_filename}")

        self.sa_processor.process_file(temp_filename, self.save_dir)
        print("Sentiment analysis completed.")

        self.ec_processor.process_file(temp_filename)
        print("Emotion classification completed.")

        self.su_processor.process_file(temp_filename)
        print("Summary generation completed.")

        self.index_processor.process_file(temp_filename)
        print("index header addition completed.")
        return file

    def process_all_files(self):
        print(f"Processing all files in folder: {self.file_dir}")
        self.tp.process_folder(self.file_dir, self.save_dir)
        print("Transcript parsing for all files completed.")

        self.sa_processor.process_folder(self.save_dir)
        print("Sentiment analysis for all files completed.")

        self.ec_processor.process_folder(self.save_dir)
        print("Emotion classification for all files completed.")

        self.su_processor.process_folder(self.save_dir)
        print("Summary generation completed.")

        self.index_processor.process_folder(self.save_dir)
        print("index header addition completed.")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files for sentiment and emotion analysis.")
    parser.add_argument("--file-dir", type=str, required=True, help="Directory containing the files to process.")
    parser.add_argument("--save-dir", type=str, required=True, help="Directory to save processed files.")
    parser.add_argument("--filename", type=str, required=False, help="Name of a specific file to process.")
    args = parser.parse_args()

    if args.filename:
        processor = FileProcessor(file_dir=args.file_dir, save_dir=args.save_dir, filename=args.filename)
        processor.process_single_file()
    else:
        processor = FileProcessor(file_dir=args.file_dir, save_dir=args.save_dir)
        processor.process_all_files()

'''
Example:

python file_processor.py --file-dir "transcripts/NTRS" --save-dir "xml" --filename "Northern Trust Corporation, Q1 2024 Earnings Call, Apr 16, 2024.rtf"
python file_processor.py --file-dir "transcripts" --save-dir "xml"
'''