import nltk
from nltk.stem import PorterStemmer
import json

def stem_keywords(keywords):
    emotion_keywords = None
    with open('emotion_keywords.json', 'r') as file:
        emotion_keywords = json.load(file)

    # Stem keywords
    emotion_keywords_stemmed = {}
    for emotion, info in emotion_keywords.items():
        keywords = info["Keywords"].split(", ")
        stemmer = PorterStemmer()
        emotion_keywords_stemmed[emotion] = [stemmer.stem(word) for word in keywords]

    with open('emotion_keywords_stemmed.json', 'w') as json_file:
        json.dump(emotion_keywords_stemmed, json_file, indent=4)