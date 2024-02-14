from TTS.api import TTS
import time
from IPython.display import Audio
import subprocess
import os
import argparse

def convert_text_to_speech(text: str) -> None:
    """Use Coqui TTS to convert text to .wav audio file

    Args:
        text: the text to be spoken

    Returns:
        None
    """
    # Initialize TTS model
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC_ph", progress_bar=False, gpu=False)
    
    # Synthesize speech from text
    tts.tts_to_file(text=text, file_path="audio/output.wav")
    Audio('audio/output.wav')


def play_audio_without_messages(audio_path="audio/output.wav") -> None:
    """The audio file displays a long information message whenever it plays the recording tone.
    This code suppresses the message for a cleaner terminal UI

    Args:
        audio_path: where the recording beep tone is located

    Returns:
        None
    """
    subprocess.run(['ffplay', '-nodisp', '-autoexit', audio_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    os.remove(audio_path)

def stream_and_play(text):
    """Use Coqui TTS  to stream the audio and play the bot's response.
    Args:
        text: the text that BKGraph Voice needs to vocalize

    Returns:
        None
    """
    convert_text_to_speech(text)
    play_audio_without_messages()

if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser(description='Process response for streaming and playing.')

    # Add argument for response (-r or --response)
    parser.add_argument('-r', '--response', type=str, help='Response text for streaming and playing')

    # Parse the arguments
    args = parser.parse_args()

    # Check if response argument is provided
    if args.response:
        stream_and_play(args.response)
    else:
        print("Please provide a response using -r or --response argument.")

# tts_models/en/blizzard2013/capacitron-t2-c150_v2: too fast
# SAM IS : very slow
# tts_models/en/ljspeech/tacotron2-DDC: a bit slow
# "tts_models/multilingual/multi-dataset/xtts_v2: multilingual option

# Initialize the TTS model using the multilingual dataset
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
# tts = TTS(model_name="tts_models/en/blizzard2013/capacitron-t2-c150_v2", progress_bar=False, gpu=False)

# Set the text you want to convert to speech
# text_to_speak = "Hello, this is an example of using Coqui TTS for text-to-speech."


# Play the generated audio
# tts.play(audio_data)
# Audio('output.wav')
# subprocess.run(['ffplay', '-nodisp', '-autoexit', 'output.wav'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


