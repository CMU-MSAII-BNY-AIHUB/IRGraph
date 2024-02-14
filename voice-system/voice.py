import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import networkx as nx
from audio_functions import AudioManager
from sample_knowledge_graph import traverse_graph
import warnings
import time
import pickle

# Ignore specific user warnings about FP16 not being supported
warnings.filterwarnings(
    'ignore', message='FP16 is not supported on CPU; using FP32 instead')

# Initialize OpenAI
load_dotenv()
client = OpenAI()

# The AudioManager class holds functions for ASR
am = AudioManager()

def load_knowledge_graph(graph_path: str) -> nx.Graph:
    """Loads the NetworkX sample knowledge graph

    Args:
        graph_path: Where the .pickle is stored

    Returns:
        NetworkX graph
    """
    with open(graph_path, "rb") as f:
        G = pickle.load(f)
    return G

def print_user_query(text: str) -> None:
    """Changes color of printed output to yellow

    Args:
        text: the user query

    Returns:
        None
    """
    green_start = "\033[38;5;220mUser 💬: "
    reset = "\033[0m"
    print(green_start + text.strip() + reset)

def print_bkgraph_response(text) -> None:
    """Changes color of printed output to green

    Args:
        text: the BKGraph response

    Returns:
        None
    """
    green_start = "\033[92mBKGraph 🏦: "
    reset = "\033[0m"
    print(green_start + text.strip() + reset)

def get_user_query() -> str:
    """Listens to user's speech and transcribes it

    Args:
        None

    Returns:
        user_query: transcribed speech
    """
    # Record and save the user's speech
    audio = am.record_audio()
    audio_path = am.save_audio(audio)

    # Transcribe the user's speech
    user_query = am.transcribe_audio(audio_path)
    print("")
    print_user_query(user_query)

    return user_query

def identify_query_topic(user_query: str) -> str:
    """Given a user query, find the topic out of these that is the most relevant: 
    [Financial Metrics, Participants, Sentiment, Hiring Needs]. This is because we have a 
    predefined set of questions you can ask.

    Args:
        user_query: the question the user asks

    Returns:
        the topic
    """
    # List of alternative kinds of keywords based on other questions to ask
    valid_node_keywords = {
        "Financial Metrics": ["financial metrics", "revenue", "margin", "income", "cash flow"],
        "Participants": ["participants", "companies", "representatives", "asking questions"],
        "Sentiment": ["sentiment", "investors", "perception"],
        "Hiring Needs": ["hiring needs", "hire", "skills", "talents", "seeking to hire"]
    }

    # Check if any valid node keyword appears in the sentence
    related_nodes = []
    for node, keywords in valid_node_keywords.items():
        for keyword in keywords:
            if keyword in user_query.lower():
                related_nodes.append(node)
                break  # Stop checking keywords for this node if any keyword is found

    time.sleep(5)
    response = None
    topic = [""]
    if related_nodes:
        response = f"I see that you are asking a question about {related_nodes[0].lower()}. What kind of response do you want? (simple/descriptive)"
        print_bkgraph_response(response)
        topic = related_nodes[0]
    else:
        response = "The sentence is not related to any valid node."
        print_bkgraph_response(response)

    # am.stream_and_play(response) # text-to-speech (needs $$, uncomment if you have sufficient quota)
    return topic

def read_descriptive_text(file_path: str) -> str:
    """The user has the option to receive a simple or descriptive text. 
    The descriptive text was gotten from ChatGPT's response to the question,
    simulating an LLM response.

    Args:
        file_path: where the text is located

    Returns:
        sentence: the descriptive text
    """
    with open(file_path, 'r') as file:
        content = file.read()
        words = content.split()
        sentence = ' '.join(words)
        return(sentence)

def retrieve_answer(topic: str, mode: str) -> str:
    """Traverse knowledge graph and get the answer for the user

    Args:
        topic: the topic of the user query
        mode: simple or descriptive, based on user's choice

    Returns:
        response: the answer to the query
    """
    relevant_answers = traverse_graph(G, topic)
    response = ', '.join(relevant_answers)

    if topic == "Financial Metrics":
        if mode == "descriptive":
            response = read_descriptive_text('descriptive_text/financial_metric.txt')
            print_bkgraph_response(response)
        else:
            print_bkgraph_response(f"The key financial metrics are {response}.")
    if topic == "Participants":
        if mode == "descriptive":
            response = read_descriptive_text('descriptive_text/participants.txt')
            print_bkgraph_response(response)
        else:
            print_bkgraph_response(f"The companies that participated were {response}.")
    if topic == "Sentiment":
        if mode == "descriptive":
            response = read_descriptive_text('descriptive_text/sentiment.txt')
            print_bkgraph_response(response)
        else:
            print_bkgraph_response(f"The overall sentiment was {response}.")
    if topic == "Hiring Needs":
        if mode == "descriptive":
            response = read_descriptive_text('descriptive_text/hiring_needs.txt')
            print_bkgraph_response(response)
        else:
            print_bkgraph_response(f"The specific skills being sought after in hiring are {response}.")
    
    # am.stream_and_play(response) # text-to-speech (needs $$, uncomment if you have sufficient quota)
    return response

def display_instructions() -> None:
    """Instructions for the user to interact with the system

    Args:
        None

    Returns:
        None
    """
    print("\nWelcome to BKGraph Voice 🏦. Ask one of these questions when 'Listening...' appears. You'll hear a start audio note.")
    print("1. What are the key financial metrics discussed during the earnings call?")
    print("2. What companies were represented in the participants who asked questions?")
    print("3. What is the overall sentiment of investors towards BNY Mellon?")
    print("4. What specific skills and talents is BNY Mellon actively seeking to hire?")

if __name__ == "__main__":
    # Launch voice chat interaction to get user input and return a response
    G = load_knowledge_graph("sample_knowledge_graph.pickle")
    display_instructions()
    ready = input("\nAre you ready to begin? (yes/no): ")
    if ready.lower() == 'yes':
        user_query = get_user_query()
        topic = identify_query_topic(user_query)
        mode = input("Enter your choice: ")
        print("")
        response = retrieve_answer(topic, mode)
        print("")
    else:
        print("\nBKGraph Voice Ended.")