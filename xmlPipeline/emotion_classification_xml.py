import sys
sys.path.append('../')
import os
from xml.etree import ElementTree as ET
import pandas as pd
import warnings
from typing import List, Tuple
import json
import matplotlib.pyplot as plt
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.util import ngrams
warnings.filterwarnings("ignore")

# Download NLTK resources
# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('stopwords')

def extract_qa_text(xml_file_path: str) -> pd.DataFrame:
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Empty lists to store speaker IDs and text content
    speaker_id_list = []
    speaker_name_list = []
    speaker_company_list = []
    text_list = []
    sentiment_label_list = []
    positive_scores_list = []
    negative_scores_list = []
    neutral_scores_list = []

    # Find the <section name="Question and Answer"> section
    qa_section = root.find("./body/section[@name='Question and Answer']")

    # Iterate over the elements within the section 
    for element in qa_section.iter():
        if element.tag == 'speaker':
            speaker_id_list.append(element.get('id'))
            speaker_company_list.append(element.get('company'))
            speaker_name_list.append(element.text.strip())
        if element.tag == 'text':
            text = ''
            if element.text is None:
                text = "Neutral."
            else:
                text = element.text.strip()
            text_list.append(text)
        # get sentiment
        if element.tag == 'sentiment':
            sentiment_label_list.append(element.text.strip())
        if element.tag == 'pos':
            positive_scores_list.append(element.text.strip())
        if element.tag == 'neg':
            negative_scores_list.append(element.text.strip())
        if element.tag == 'neutr':
            neutral_scores_list.append(element.text.strip())

    qa_df = pd.DataFrame({'Speaker ID': speaker_id_list,
                    'Speaker Name': speaker_name_list,
                    'Speaker Company': speaker_company_list, 
                    'Text': text_list,
                    'Sentiment Label': sentiment_label_list,
                    'Positive Score': positive_scores_list,
                    'Negative Score': negative_scores_list,
                    'Neutral Score': neutral_scores_list
                    })
    return qa_df

# Function to tokenize, remove stop words, and stem the text
def process_text(text):
    tokens = word_tokenize(text)
    additional_stop_words = [',', '.', '--', "'s", "'d", "'ll", "'re", "'ve", '``', "''"]
    stop_words = set(stopwords.words('english') + additional_stop_words)
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(word) for word in filtered_tokens]
    return stemmed_tokens


# Function to classify emotions based on sentiment score ranges
def classify_emotion_score_ranges(row):
    emotion_data = None
    with open('glossary/emotion_score_range.json', 'r') as file:
        emotion_data = json.load(file)

    pos_score = row['Positive Score']
    neg_score = row['Negative Score']
    neutr_score = row['Neutral Score']
    
    # Handle missing scores by returning "Unclassified"
    if pd.isna(pos_score) or pd.isna(neg_score) or pd.isna(neutr_score):
        return "Unclassified"
    
    applicable_emotions = []
    for emotion, scores in emotion_data.items():
        if (scores['PositiveScoreRange'][0] <= pos_score <= scores['PositiveScoreRange'][1] and
            scores['NegativeScoreRange'][0] <= neg_score <= scores['NegativeScoreRange'][1] and
            scores['NeutralScoreRange'][0] <= neutr_score <= scores['NeutralScoreRange'][1]):
            applicable_emotions.append(emotion)
    
    # Join multiple emotions with a semicolon or return "Unclassified"
    return ", ".join(applicable_emotions) if applicable_emotions else "Unclassified"


# Function to classify emotions based on stemmed keywords
def classification_by_stem(tokens, stemmed_keywords):
    emotions = []
    ack_words = set(["ye", "right", "okay", "got", "thank", "sure", "none"])

    # Check if tokens have less than 5 words and contain one of the acknowledgment words
    if len(tokens) < 5 and any(word in tokens for word in ack_words):
        return "Acknowledgement"

    for emotion, keywords in stemmed_keywords.items():
        for keyword in keywords:
            bigrams = list(ngrams(tokens, 2))
            # Check if unigram or bigram is in the text
            if keyword in tokens or any(keyword in bigram for bigram in bigrams):
                emotions.append(emotion)
                break  # No need to check other keywords for this emotion
    return ', '.join(emotions) if emotions else "Unclassified"


# Function to combine emotions from score ranges and stemmed keywords
def combine_emotions(df):
    def classify_res(row):
        if row['Emotion By Score Ranges'] == 'Unclassified' and row['Emotion By Keyword Stem'] == 'Unclassified':
            return 'Neutral'
        elif row['Emotion By Keyword Stem'] == 'Acknowledgement':
            return 'Acknowledgement'
        elif row['Emotion By Score Ranges'] != 'Unclassified':
            return row['Emotion By Score Ranges']
        else:
            return row['Emotion By Keyword Stem']

    df['Emotion Category'] = df.apply(classify_res, axis=1)
    return df

# Function to add emotion tags to the XML file for the Q&A section
def plot_emotion_distribution(column, plot_title, file_name):
    all_emotions = []
    for emotions in column:
        all_emotions.extend(emotions.split(', '))

    # Count the frequency of each emotion
    emotion_counts = Counter(all_emotions)
    labels = list(emotion_counts.keys())
    counts = list(emotion_counts.values())

    # Define color mapping and plot
    color_map = {'Confidence': 'green', 'Excitement': 'green', 'Optimism': 'green','Positive Surprise': 'green',
                 'Frustration': 'red','Concern': 'red', 'Doubtful': 'red', 'Negative Surprise': 'red',
                 'Confusion': 'blue', 'Curiosity': 'blue', 'Skepticism': 'blue',
                 'Unclassified': 'grey'
                }
    colors = [color_map.get(emotion, 'grey') for emotion in labels]
    plt.figure(figsize=(10, 8))
    plt.barh(labels, counts, color=colors)
    plt.xlabel('Frequency')
    plt.ylabel('Emotion')
    plt.title(f'Distribution of Emotions by Frequency {plot_title}')
    plt.tight_layout()
    plt.savefig(f'plots/{file_name}.png')

def get_final_emotion_tags(file_path, plot=False):
    # load data
    df = pd.read_csv(file_path)

    # get emotion categories from score ranges
    df['Emotion By Score Ranges'] = df.apply(classify_emotion_score_ranges, axis=1)
    if plot:
        plot_emotion_distribution(df['Emotion By Score Ranges'], 'Based On Sentiment Score Ranges', 'scorerange_emotion_distribution')

    # get emotion categories from stemming
    emotion_keywords_stemmed = None
    with open('glossary/emotion_keywords_stemmed.json', 'r') as file:
        emotion_keywords_stemmed = json.load(file)
    df['Text'] = df['Text'].fillna('')  # Handle missing values
    df['Processed_Text'] = df['Text'].apply(process_text)
    df['Emotion By Keyword Stem'] = df['Processed_Text'].apply(lambda x: classification_by_stem(x, emotion_keywords_stemmed))
    df_final = df[['Text', 'Processed_Text', 'Emotion By Score Ranges', 'Emotion By Keyword Stem', 'Sentiment Label', 'Positive Score', 'Negative Score', 'Neutral Score']]
    if plot:
        plot_emotion_distribution(df['Emotion By Keyword Stem'], 'Based On Keyword Stem', 'keywordstem_emotion_distribution')
    
    # combine both
    df_combined = combine_emotions(df_final)
    if plot:
        plot_emotion_distribution(df_combined['Emotion Category'], 'Emotion By Score and Keyword', 'combined_emotion_distribution')
    return df_combined


def add_qa_emotion_tag_to_xml(xml_file_path: str, qa_df: pd.DataFrame, file_name: str) -> None: 
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    qa_section = root.find("./body/section[@name='Question and Answer']")

    idx = 0
    for speaker_element in qa_section.iter('speaker'):
        if speaker_element.attrib.get('id') != '-1':
            text_element = speaker_element.find('text')
            emotion_element = ET.SubElement(text_element, "emotion")
            emotion_element.text = qa_df.loc[idx, 'Emotion Category'].lower()
        idx += 1
        
    # Save the modified XML file
    tree.write(file_name, encoding='utf-8', xml_declaration=True)


def complete_emotion_tagging(xml_file_path: str) -> None:
    # Extract file name
    path_components = xml_file_path.split('\\')
    file_name_with_extension = path_components[-1]
    file_name = os.path.splitext(file_name_with_extension)[0]

    # Q&A SECTION
    print(f"[{file_name}] Adding emotion tags to the XML for the Q&A section... ")
    df = extract_qa_text(xml_file_path)
    output = f'csv/qa_{file_name}.csv'
    df.to_csv(output, index=False) # MUST SAVE THE DATA

    # ADD EMOTION TAGS TO DF
    df = get_final_emotion_tags(output, plot=False)
    # output = f'csv/emotions_qa_{file_name}.csv'
    # df.to_csv(output, index=False) # SAVE THE DATA  (OPTIONAL)

    # ADD TAGS TO XML
    file_output = 'xml_w_emotion/'+file_name+'.xml'
    add_qa_emotion_tag_to_xml(xml_file_path, df, file_output)

    # CLEANUP
    os.remove(f'csv/qa_{file_name}.csv')

if __name__ == '__main__':
    complete_emotion_tagging('sent_xml_BK-Q1-2018.xml')