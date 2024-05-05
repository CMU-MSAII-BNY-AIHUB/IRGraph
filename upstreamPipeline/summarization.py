from openai import OpenAI
import os
from configparser import ConfigParser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# print(BASE_DIR)
CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / "config.ini")
OPENAI_KEY = CONFIG.get("UPSTREAM", "openai_api_key")

class Summarizer:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_KEY)

    def summarize(self, text, tag):
        # tag = "question" if isQuestion else "answer"
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 
                        "You are a financial analyst reading earnings call transcript, skilled in analyzing the call and performing summarization. You are preparing for an upcoming earnings call and looking back to previous earnings calls to get insights. Your task is to summartize the presentation statement, questions and answers concisely."},
                {"role": "user", "content": f"Summarize this {tag} with only one sentence: {text}"}
            ]
        )
        summarization = completion.choices[0].message.content
        # print(len(summarization) / len(text) * 100, '%')

        return summarization
