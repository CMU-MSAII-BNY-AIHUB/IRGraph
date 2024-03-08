from xml.etree import ElementTree as ET
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def extract_qa_text(xml_file_path):
    # Load the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Define empty lists to store speaker IDs and text content
    speaker_id_list = []
    speaker_name_list = []
    speaker_position_list = []
    text_list = []

    # Find the <section name="Question and Answer"> section
    qa_section = root.find("./body/section[@name='Question and Answer']")

    # Iterate over the elements within the section --> type, id, speaker id, speaker pos, text, [sentiment]
    for element in qa_section.iter():
        if element.tag == 'speaker':
            speaker_id_list.append(element.get('id'))
            speaker_position_list.append(element.get('position'))
            speaker_name_list.append(element.text.strip())
        if element.tag == 'text':
            text = element.text.strip()
            text_list.append(text)


    qa_df = pd.DataFrame({'Speaker ID': speaker_id_list,
                    'Speaker Name': speaker_name_list,
                    'Speaker Position': speaker_position_list, 
                    'Text': text_list})
    
    return qa_df

def get_sentiment_scores(text):
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
  
def add_sentiment_tag_to_xml(xml_file_path, qa_df, file_name):
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

if __name__ == "__main__":
    # extract statements from the presentation
    
    file_name = 'BNY-Q3-2020'
    xml_file_path = 'xml_files/'+file_name+'.xml'
    # print(f"\n## Extracting Q&A session from {xml_file_path}...")
    # qa_df = extract_qa_text(xml_file_path)
    # call_info = 'csv/'+file_name+'_'
    # # qa_df.to_csv(call_info+"qa_section.csv", index=False)

    # # conduct sentiment analysis on the Q&A text
    # print("\n## Conducting sentiment analysis on the Q&A text...")
    # qa_df['Positive Score'], qa_df['Negative Score'], qa_df['Neutral Score'], qa_df['Sentiment Label'] = zip(*qa_df['Text'].apply(get_sentiment_scores))
    # qa_df.to_csv(call_info+"qa_section_sentiment.csv", index=False)


    ##### UNCOMMENT IF USING THE LAST SAVED DF WITHOUT RUNING PREVIOUS LINES OF CODE
    qa_df = pd.read_csv(f"csv/{file_name}_qa_section_sentiment.csv", converters={'Positive Score': pd.eval})
    #####

    # add the sentiment label to the xml file
    print("\n## Adding the report as a tag to the XML file...")
    output_file = 'xml_files/'+file_name+'_with_qa_sentiment.xml'
    add_sentiment_tag_to_xml(xml_file_path, qa_df, output_file)
    print(f"Done! Find the XML file here:{output_file} \n")