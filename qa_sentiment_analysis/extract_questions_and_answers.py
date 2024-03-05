from xml.etree import ElementTree as ET
import pandas as pd

def extract_questions(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Extract data into a list of dictionaries
    data = []
    for question in root.findall(".//question"):
        question_id = question.get("id")
        speaker = question.find("speaker")
        speaker_id = speaker.get("id")
        position = speaker.get("position")
        speaker_name = speaker.text.split('<')[0].strip()
        question_text = speaker.find("text").text
        data.append({
            "Question ID": question_id,
            "Speaker ID": speaker_id,
            "Speaker Company": position,
            "Speaker Name": speaker_name,
            "Question": question_text
        })
    
    question_df = pd.DataFrame(data)
    return question_df

def extract_answers(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Extract data into a list of dictionaries
    data = []
    for answer in root.findall(".//answer"):
        answer_id = answer.get("id")
        speaker = answer.find("speaker")
        speaker_id = speaker.get("id")
        position = speaker.get("position")
        speaker_name = speaker.text.split('<')[0].strip()
        answer_text = speaker.find("text").text
        data.append({
            "Answer ID": answer_id,
            "Speaker ID": speaker_id,
            "Speaker Company": position,
            "Speaker Name": speaker_name,
            "Answer": answer_text
        })
    
    answer_df = pd.DataFrame(data)
    return answer_df

if __name__ == "__main__":
    xml_file_path = '../data/sample_xml/Northern Trust Corporation, Q1 2020 Earnings Call, Apr 21, 2020.xml'
    question_df = extract_questions(xml_file_path)
    answer_df = extract_answers(xml_file_path)

    call_info = "csv/ntrs_q1_2020_"
    question_df.to_csv(call_info+"questions.csv", index=False)
    answer_df.to_csv(call_info+"answers.csv", index=False)