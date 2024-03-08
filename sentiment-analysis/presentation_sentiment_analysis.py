from xml.etree import ElementTree as ET
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import matplotlib.pyplot as plt

def extract_statements(xml_file_path):
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

def get_sentiment_scores(text):
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
    
def find_negative_sentences(text, sentiment_labels):
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
    
def create_analysis_summary(text, sentiment_labels):
    # Calculate counts and percentages
    positive_count = sentiment_labels.count("positive")
    negative_count = sentiment_labels.count("negative")
    neutral_count = sentiment_labels.count("neutral")
    total_sentences = len(sentiment_labels)

    positive_percentage = (positive_count / total_sentences) * 100
    negative_percentage = (negative_count / total_sentences) * 100
    neutral_percentage = (neutral_count / total_sentences) * 100

    # Find negative sentences
    negative_sentences = find_negative_sentences(text, sentiment_labels)

    # Generate overall sentiment analysis summary as a string
    most_common_label = max(sentiment_labels, key=sentiment_labels.count)
    analysis_summary = f"Overall sentiment is {most_common_label}. "
    analysis_summary += f"{positive_count} sentences are positive ({positive_percentage:.2f}%). "
    analysis_summary += f"{negative_count} sentences are negative ({negative_percentage:.2f}%). "
    analysis_summary += f"{neutral_count} sentences are neutral ({neutral_percentage:.2f}%). "
    analysis_summary += f"{negative_sentences}"

    return analysis_summary

def add_sentiment_tag_to_xml(xml_file_path, statement_df, file_name):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Iterate over the statement elements and add sentiment tags
    for statement_element, sentiment_label in zip(root.findall(".//statement"), statement_df['Top Sentiment Label']):
        speaker_element = statement_element.find('speaker')
        sentiment_element = ET.SubElement(speaker_element, "sentiment")
        sentiment_element.text = sentiment_label

    # Add the sentiment report to the xml file
    for statement_element, sentiment_analysis in zip(root.findall(".//statement"), statement_df['Analysis Summary']):
        speaker_element = statement_element.find('speaker')
        sentiment_element = speaker_element.find('sentiment')
        analysis_element = ET.SubElement(sentiment_element, "analysis")
        analysis_element.text = sentiment_analysis
        
    # Save the modified XML file
    tree.write(file_name, encoding='utf-8', xml_declaration=True)
    

if __name__ == "__main__":

    # extract statements from the presentation
    print("\n## Extracting statements from XML file...")
    file_name = 'BNY-Q2-2023'
    xml_file_path = 'xml_files/'+file_name+'.xml'
    statement_df = extract_statements(xml_file_path)
    call_info = 'csv/'+file_name+'_'
    # statement_df.to_csv(call_info+"presentation_section.csv", index=False)

    # conduct sentiment analysis on the statements
    print("\n## Conducting sentiment analysis on the statements...")
    statement_df['Sentiment Scores'], statement_df['Sentiment Labels'], statement_df['Top Sentiment Label'] = zip(*statement_df['Statement'].apply(get_sentiment_scores))
    # statement_df.to_csv(call_info+"presentation_section_sentiment.csv", index=False)

    # create a summary of the sentiment analysis insights
    print("\n## Creating a summary of analysis...")
    statement_df['Analysis Summary'] = statement_df.apply(lambda x: create_analysis_summary(x['Statement'], x['Sentiment Labels']), axis=1)
    statement_df.to_csv(call_info+"presentation_sentiment_summary.csv", index=False) # LASTED SAVED DF


    ##### UNCOMMENT IF USING THE LAST SAVED DF WITHOUT RUNING PREVIOUS LINES OF CODE
    # statement_df = pd.read_csv("csv/bny_q2_2023_"+"presentation_sentiment_summary.csv")
    #####

    # add the sentiment label to the xml file
    print("\n## Adding the report as a tag to the XML file...")
    output_file = 'xml_files/'+file_name+'_with_presentation_sentiment.xml'
    add_sentiment_tag_to_xml(xml_file_path, statement_df, output_file)
    print(f"Done! Find the XML file here:{output_file} \n")