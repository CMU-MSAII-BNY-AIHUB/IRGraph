import docx
import os
import xml.etree.ElementTree as ET
import re
import argparse
import aspose.words as aw

def rtfToDocx(rtf_path, filename):
    doc = aw.Document(os.path.join(rtf_path, filename))
    doc.save(filename.replace(".rtf", ".docx"))
    doc = docx.Document(filename.replace(".rtf", ".docx"))
    return doc


def main():
    parser = argparse.ArgumentParser(description='Parse rtf file and convert to XML.')
    parser.add_argument('--file-dir', type=str, required=False, default="transcripts",
                        help='Path to the transcript file to be parsed.')
    parser.add_argument('--save-dir', type=str, required=False, default="transcripts",
                        help='Path to save the xml')
    args = parser.parse_args()
    file_path = args.file_dir
    save_path = args.save_dir

    print("Listing contents of:", file_path)

    for root, dirs, files in os.walk(os.path.abspath(file_path)):
        for dir_name in dirs:
            print(f"Directory: {dir_name}")
            dir_path = os.path.join(root, dir_name)
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                if os.path.isfile(file_path):
                    print(f"  File: {filename}")
                    doc = rtfToDocx(dir_path,filename)
                    os.remove(filename.replace(".rtf", ".docx"))
                    break
if __name__ == "__main__":
    main()