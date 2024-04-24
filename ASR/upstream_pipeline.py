from neo4j_processor import Neo4jProcessor
from file_processor import FileProcessor
import argparse
import os
## main db
# URI = "neo4j+s://28d0251c.databases.neo4j.io"
# AUTH = ("neo4j", "t4yYAA-Toa9N4cQNb1r2nQQAXWrabbMM3MclZ7rq2Tc")
## backup db
URI = "neo4j+s://e32a4bb4.databases.neo4j.io"
AUTH = ("neo4j", "EerfwXY8kw-DFeEB8WaO4vjWJKzNTbVhLIMlx_uWwSI")


def neo4j_import_single_file(file_path):
    neo4j_processor = Neo4jProcessor(URI, AUTH)
    neo4j_processor.process_single_file(file_path)
    print(f"Completed importing {file_path} to Neo4j.")
    neo4j_processor.close()

def neo4j_import_folder(folder_path):
    neo4j_processor = Neo4jProcessor(URI, AUTH)
    neo4j_processor.process_folder(folder_path)
    print(f"Completed importing all files in {folder_path} to Neo4j.")
    neo4j_processor.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process files for sentiment and emotion analysis and import to Neo4j.")
    parser.add_argument("--file-dir", type=str, required=True, help="Directory containing the files to process.")
    parser.add_argument("--save-dir", type=str, required=True, help="Directory to save processed files.")
    parser.add_argument("--filename", type=str, required=False, help="Name of a specific file to process.")
    args = parser.parse_args()

    processor = FileProcessor(file_dir=args.file_dir, save_dir=args.save_dir, filename=args.filename)
    if args.filename:
        file_name = args.filename
        # file_name = processor.process_single_file()
        print(f"neo 4j processing {file_name} on {AUTH}")
        neo4j_import_single_file(file_name)
        print("here")
    else:
        # processor.process_all_files()
        neo4j_import_folder(args.save_dir)

'''
Example:

python upstream_pipeline.py --file-dir "" --save-dir "" --filename "STT-Q1-2024_timestamp.xml"
python upstream_pipeline.py --file-dir "transcripts" --save-dir "xml"

clean the data base:
MATCH (n)
DETACH DELETE n
'''