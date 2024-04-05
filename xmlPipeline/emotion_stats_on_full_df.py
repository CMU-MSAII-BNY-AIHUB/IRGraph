import os
from xml.etree import ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
import emotion_classification_xml as EC
import json

def extract_sentiment_from_folder(xml_folder_path: str, csv_file_path: str) -> None:
    all_files = []
    all_text = []
    all_sentiments = []
    all_positive_scores = []
    all_negative_scores = []
    all_neutral_scores = []

    # Loop through all XML files in the folder
    for filename in os.listdir(xml_folder_path):
        if filename.endswith(".xml"):
            file_path = os.path.join(xml_folder_path, filename)
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Find all text elements and extract sentiment-related information
            for text_elem in root.findall(".//text"):
                all_text.append(text_elem.text)
                all_files.append(filename)  # Add filename to the list
                sentiment_elem = text_elem.find("sentiment")
                if sentiment_elem is not None:
                    all_sentiments.append(sentiment_elem.text)
                else:
                    all_sentiments.append(None)

                positive_elem = text_elem.find("pos")
                if positive_elem is not None:
                    all_positive_scores.append(positive_elem.text)
                else:
                    all_positive_scores.append(None)

                negative_elem = text_elem.find("neg")
                if negative_elem is not None:
                    all_negative_scores.append(negative_elem.text)
                else:
                    all_negative_scores.append(None)

                neutral_elem = text_elem.find("neutr")
                if neutral_elem is not None:
                    all_neutral_scores.append(neutral_elem.text)
                else:
                    all_neutral_scores.append(None)

    df = pd.DataFrame({
        'File Name': all_files,
        'Text': all_text,
        'Sentiment Label': all_sentiments,
        'Positive Score': all_positive_scores,
        'Negative Score': all_negative_scores,
        'Neutral Score': all_neutral_scores
    })
    df.to_csv(csv_file_path, index=False)


def find_score_ranges(csv_file_path):
    """Find the range of scores that correlate to each sentiment label."""
    df = pd.read_csv(csv_file_path)

    grouped = df.groupby('Sentiment Label')
    score_ranges = {}
    for label, group in grouped:
        min_positive = group['Positive Score'].min()
        max_positive = group['Positive Score'].max()
        
        min_negative = group['Negative Score'].min()
        max_negative = group['Negative Score'].max()
        
        min_neutral = group['Neutral Score'].min()
        max_neutral = group['Neutral Score'].max()

        score_ranges[label] = {
            'Positive Score': (min_positive, max_positive),
            'Negative Score': (min_negative, max_negative),
            'Neutral Score': (min_neutral, max_neutral)
        }

    return score_ranges


def visualize_score_ranges(score_ranges):
    """Visualize score ranges for each sentiment label."""
    # Define sentiment labels and score types
    labels = ['negative', 'neutral', 'positive']
    score_types = ['Positive Score', 'Negative Score', 'Neutral Score']
    
    colors = {'positive': 'green', 'negative': 'red', 'neutral': 'blue'}
    fig, axes = plt.subplots(nrows=1, ncols=len(score_types), figsize=(15, 5), sharey=True)
    
    # Plot score ranges for each sentiment label and score type
    for i, score_type in enumerate(score_types):
        ax = axes[i]
        ax.set_title(score_type)
        ax.set_xlabel('Sentiment Label')
        ax.set_ylabel('Score Range')
        ax.set_ylim(0, 1)  # Set y-axis limits to 0 and 1
        
        # Plot score ranges for each sentiment label
        for j, label in enumerate(labels):
            score_range = score_ranges[label][score_type]
            ax.bar(j, score_range[1] - score_range[0], bottom=score_range[0], color=colors[label], alpha=0.5, label=label)
            ax.text(j, score_range[0] + 0.05, f"{score_range[0]:.4f}-{score_range[1]:.4f}", ha='center', va='bottom')

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)

    plt.tight_layout()
    plt.legend(title='Sentiment Label', loc='upper left', bbox_to_anchor=(1, 1))
    plt.savefig("plots/emotion_score_ranges_72files.png")

if __name__ == "__main__":
    output = "stats_files/all_72_sentiment_files.csv"
    extract_sentiment_from_folder("xml_w_sentiment_full", output)
    score_ranges = find_score_ranges(output)
    visualize_score_ranges(score_ranges)
    EC.get_final_emotion_tags(output, plot=True)