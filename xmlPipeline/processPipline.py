from transcript_parser import TranscriptParser
from sentiment_analysis_processor import SentimentAnalysisProcessor
from emotion_classification_processor import EmotionClassificationProcessor
import argparse
import os

def process_single_file(file_dir, filename, save_dir):
    # Assuming process_file method for each processor does not require directory arguments but only file path
    print(f"Processing file: {file_dir}")
    tp = TranscriptParser()
    temp_filename = tp.process_file(file_dir, filename, save_dir)
    print(f"Transcript parsing completed. file in: {temp_filename}")

    sa_processor = SentimentAnalysisProcessor()
    sa_processor.process_file(temp_filename, save_dir)
    print("Sentiment analysis completed.")

    ec_processor = EmotionClassificationProcessor()
    ec_processor.process_file(temp_filename)
    print("Emotion classification completed.")

def process_all_files(file_dir, save_dir):
    # Assuming process_folder method for each processor does not require save directory argument but only folder path
    print(f"Processing all files in folder: {file_dir}")
    tp = TranscriptParser()
    tp.process_folder(file_dir, save_dir)
    print("Transcript parsing for all files completed.")

    sa_processor = SentimentAnalysisProcessor()
    sa_processor.process_folder(save_dir)
    print("Sentiment analysis for all files completed.")

    ec_processor = EmotionClassificationProcessor()
    ec_processor.process_folder(save_dir)
    print("Emotion classification for all files completed.")

# def process_single_file(file_dir, filename, save_dir):
#     processor = TranscriptParser()
#     processor.process_file(file_dir, filename, save_dir)
#     print(f"Processed {filename} and saved to {save_dir}")

# def process_all_files(file_dir, save_dir):
#     processor = TranscriptParser()
#     processor.process_folder(file_dir, save_dir)
#     print(f"Processed all files in {file_dir} and saved to {save_dir}")

# def sentiment_analysis_on_single_file(file_path):
#     sa_processor = SentimentAnalysisProcessor()
#     sa_processor.process_file(file_path)
#     print(f"Completed sentiment analysis for {file_path}")

# def sentiment_analysis_on_folder(folder_path):
#     sa_processor = SentimentAnalysisProcessor()
#     sa_processor.process_folder(folder_path)
#     print(f"Completed sentiment analysis for all files in {folder_path}")


if __name__ == "__main__":
    file_dir = "sample_data"
    filename = "The Bank of New York Mellon Corporation, Q2 2023 Earnings Call, Jul 18, 2023 (1).rtf"
    save_dir = "sample_output"


    # process_single_file(file_dir, filename, save_dir)

    process_single_file(file_dir, filename, save_dir)
    # process_all_files(file_dir, save_dir)
    # sentiment_analysis_on_folder(save_dir)