import os
from xml.etree import ElementTree as ET
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

def extract_presentation_statements(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Extract data into a list of dictionaries
    data = []
    for statement in root.findall(".//statement"):
        speaker = statement.find("speaker")
        speaker_id = speaker.get("id")
        position = speaker.get("position")
        speaker_name = speaker.text.split('<')[0].strip()
        statement_text = speaker.find("text").text
        data.append({
            "Speaker ID": speaker_id,
            "Speaker Company": position,
            "Speaker Name": speaker_name,
            "Statement": statement_text
        })
    
    statement_df = pd.DataFrame(data)
    # statement_df = statement_df.drop(0) # remove the operator
    return statement_df

def get_presentation_sentiment_scores(text):
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    # Split the text into sentences
    sentences = text.split(".")

    sentiment_labels = []
    sentiment_scores = []
    
    # Loop through each sentence and get sentiment prediction (max score)
    for sentence in sentences:
        inputs = tokenizer(sentence, padding = True, truncation = True,  return_tensors='pt')
        outputs = model(**inputs)
        # Get the predicted sentiment score
        scores = torch.nn.functional.softmax(outputs.logits, dim=-1)#outputs.logits.item()
        scores_list = scores[:, 0].tolist(), scores[:, 1].tolist(), scores[:, 2].tolist() # pos, neg, neutr 
        sentiment_scores.append(scores_list)
        # Get the prediction (max score)   
        max_index = scores_list.index(max(scores_list))
        if max_index == 0:
            sentiment_labels.append("positive")
        elif max_index == 1:
            sentiment_labels.append("negative")
        else:
            sentiment_labels.append("neutral")

    most_common_label = max(sentiment_labels, key=sentiment_labels.count)

    return sentiment_scores, sentiment_labels, most_common_label
    
def find_presentation_negative_sentences(text, sentiment_labels):
    # Split the text into sentences
    sentences = text.split(".")

    # Extract sentences based on labels
    negative_sentences = []
    for sentence, label in zip(sentences, sentiment_labels):
        if label=="negative":
            negative_sentences.append(sentence)
    
    output = ''
    if negative_sentences:
        output += "The classified negative sentences are: "
        for i, sentence in enumerate(negative_sentences, start=1):
            output += f"({i}) {sentence.strip()}. "
    
    return output
    
def create_presentation_analysis_summary(text, sentiment_labels):
    # Calculate counts and percentages
    positive_count = sentiment_labels.count("positive")
    negative_count = sentiment_labels.count("negative")
    neutral_count = sentiment_labels.count("neutral")
    total_sentences = len(sentiment_labels)

    positive_percentage = (positive_count / total_sentences) * 100
    negative_percentage = (negative_count / total_sentences) * 100
    neutral_percentage = (neutral_count / total_sentences) * 100

    # Find negative sentences
    negative_sentences = find_presentation_negative_sentences(text, sentiment_labels)

    # Generate overall sentiment analysis summary as a string
    most_common_label = max(sentiment_labels, key=sentiment_labels.count)
    analysis_summary = f"Overall sentiment is {most_common_label}. "
    analysis_summary += f"{positive_count} sentences are positive ({positive_percentage:.2f}%). "
    analysis_summary += f"{negative_count} sentences are negative ({negative_percentage:.2f}%). "
    analysis_summary += f"{neutral_count} sentences are neutral ({neutral_percentage:.2f}%). "
    analysis_summary += f"{negative_sentences}"

    return analysis_summary

def add_presentation_sentiment_tag_to_xml(xml_file_path, statement_df, file_name):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Iterate over the statement elements and add sentiment tags
    for statement_element, sentiment_label in zip(root.findall(".//statement"), statement_df['Top Sentiment Label']):
        speaker_element = statement_element.find("speaker")
        text_element = speaker_element.find("text")
        sentiment_element = ET.SubElement(text_element, "sentiment")
        sentiment_element.text = sentiment_label

    # Add the sentiment report to the xml file
    for statement_element, sentiment_analysis in zip(root.findall(".//statement"), statement_df['Analysis Summary']):
        speaker_element = statement_element.find("speaker")
        text_element = speaker_element.find("text")
        analysis_element = ET.SubElement(text_element, "analysis")
        analysis_element.text = sentiment_analysis
        
    # Save the modified XML file
    tree.write(file_name, encoding='utf-8', xml_declaration=True)

def extract_qa_text(xml_file_path):
    # Load the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Define empty lists to store speaker IDs and text content
    speaker_id_list = []
    speaker_name_list = []
    speaker_company_list = []
    text_list = []

    # Find the <section name="Question and Answer"> section
    qa_section = root.find("./body/section[@name='Question and Answer']")

    # Iterate over the elements within the section --> type, id, speaker id, speaker pos, text, [sentiment]
    for element in qa_section.iter():
        if element.tag == 'speaker':
            speaker_id_list.append(element.get('id'))
            speaker_company_list.append(element.get('company'))
            speaker_name_list.append(element.text.strip())
        if element.tag == 'text':
            text = element.text.strip()
            text_list.append(text)


    qa_df = pd.DataFrame({'Speaker ID': speaker_id_list,
                    'Speaker Name': speaker_name_list,
                    'Speaker Company': speaker_company_list, 
                    'Text': text_list})
    
    return qa_df

def get_qa_sentiment_scores(text):
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    
    # Get sentiment prediction (max score)
    inputs = tokenizer(text, padding = True, truncation = True,  return_tensors='pt')
    outputs = model(**inputs)
    # Get the predicted sentiment score
    scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_scores = scores[:, 0].tolist(), scores[:, 1].tolist(), scores[:, 2].tolist() # (pos, neg, neutr) tuple
    pos_score, neg_score, neut_score = round(sentiment_scores[0][0], 4), round(sentiment_scores[1][0], 4), round(sentiment_scores[2][0], 4)
    # Get the prediction (max score) 
    max_index = sentiment_scores.index(max(sentiment_scores))
    sentiment_label = ''
    if max_index == 0:
        sentiment_label = "positive"
    elif max_index == 1:
        sentiment_label = "negative"
    else:
        sentiment_label = "neutral"

    return pos_score, neg_score, neut_score, sentiment_label
  
def add_qa_sentiment_tag_to_xml(xml_file_path, qa_df, file_name):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    qa_section = root.find("./body/section[@name='Question and Answer']")

    # Add sentiment label, positive score, negative score, neutral score
    idx = 0
    for element in qa_section.iter():
        if element.tag == 'text':
            # sentiment label
            sentiment_element = ET.SubElement(element, "sentiment")
            sentiment_element.text = qa_df.loc[idx, 'Sentiment Label']
            # pos
            pos_element = ET.SubElement(element, "pos")
            pos_element.text = str(qa_df.loc[idx, 'Positive Score'])
            # neg
            neg_element = ET.SubElement(element, "neg")
            neg_element.text = str(qa_df.loc[idx, 'Negative Score'])
            # neutr
            neutr_element = ET.SubElement(element, "neutr")
            neutr_element.text = str(qa_df.loc[idx, 'Neutral Score'])
            idx += 1
        
    # Save the modified XML file
    tree.write(file_name, encoding='utf-8', xml_declaration=True)

def complete_sentiment_tagging(xml_file_path):
    # extract file name
    path_components = xml_file_path.split('/')
    file_name_with_extension = path_components[-1]
    file_name = os.path.splitext(file_name_with_extension)[0]

    # PRESENTATION SECTION
    print("\n### Adding sentiment tags to the XML for the presentation section... ")
    print("> Extracting statements from the presentation...")
    statement_df = extract_presentation_statements(xml_file_path)

    print("> Conducting sentiment analysis on the statements...")
    statement_df['Sentiment Scores'], statement_df['Sentiment Labels'], statement_df['Top Sentiment Label'] = zip(*statement_df['Statement'].apply(get_presentation_sentiment_scores))
    statement_df['Analysis Summary'] = statement_df.apply(lambda x: create_presentation_analysis_summary(x['Statement'], x['Sentiment Labels']), axis=1)
    statement_df.to_csv(f'csv/Presentation_Sentiment_{file_name}.csv', index=False) # SAVE THE DATA

    ##### UNCOMMENT IF USING THE SAVED DATA WITHOUT RUNING PREVIOUS LINES OF CODE
    # statement_df = pd.read_csv("csv/new_xml_"+"presentation_sentiment_summary.csv")
    #####

    # add the sentiment label to the xml file
    pres_sentim_xml_file = 'xml_files/With_Presentation_Sentiment_'+file_name+'.xml'
    add_presentation_sentiment_tag_to_xml(xml_file_path, statement_df, pres_sentim_xml_file)
    print(f"Done! Find the XML file with sentiment tags for the presentation section here: {pres_sentim_xml_file} \n")

    # Q&A SECTION
    print("\n### Adding sentiment tags to the XML (with presentation sentiment) for the Q&A section... ")
    print(f"> Extracting Q&A section from {pres_sentim_xml_file}...")
    qa_df = extract_qa_text(pres_sentim_xml_file)

    print("> Conducting sentiment analysis on the Q&A text...")
    qa_df['Positive Score'], qa_df['Negative Score'], qa_df['Neutral Score'], qa_df['Sentiment Label'] = zip(*qa_df['Text'].apply(get_qa_sentiment_scores))
    qa_df.to_csv(f'csv/Q&A_Sentiment_{file_name}.csv', index=False) # SAVE THE DATA

    ##### UNCOMMENT IF USING THE LAST SAVED DF WITHOUT RUNING PREVIOUS LINES OF CODE
    # qa_df = pd.read_csv(f"csv/{file_name}_qa_section_sentiment.csv", converters={'Positive Score': pd.eval})
    #####

    # add the sentiment label to the xml file
    sentiment_file = 'xml_files/With_Sentiment_'+file_name+'.xml'
    add_qa_sentiment_tag_to_xml(pres_sentim_xml_file, qa_df, sentiment_file)
    print(f"Done! Find the XML file with all sentiment tags (both presentation and Q&A sections) here: {sentiment_file} \n")

    # CLEANUP
    os.remove(pres_sentim_xml_file) # remove presentation sentiment xml file
    

if __name__ == "__main__":
    xml_file_path = '../data/sample_xml/The Bank of New York Mellon Corporation, Q3 2020 Earnings Call, Oct 16, 2020.xml'
    complete_sentiment_tagging(xml_file_path)
    