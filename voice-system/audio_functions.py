import openai
from openai import OpenAI
import sounddevice as sd
import numpy
import wavio
import io
import os
import whisper
from pydub import AudioSegment
from pydub.playback import play
import subprocess

start_audio_path = 'audio/start_listening.m4a'
stop_audio_path = 'audio/stop_listening.m4a'

class AudioManager:

    def __init__(self):
        self.client = OpenAI()
        self.model = whisper.load_model("base") # openAI for transcripting speech-to-text

    def play_audio_without_messages(self, audio_path: str) -> None:
        """The audio file displays a long information message whenever it plays the recording tone.
        This code suppresses the message for a cleaner terminal UI

        Args:
            audio_path: where the recording beep tone is located

        Returns:
            None
        """
        subprocess.run(['ffplay', '-nodisp', '-autoexit', audio_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def record_audio(self, duration=8, fs=44100) -> numpy.ndarray:
        """Record audio from the microphone for a specified duration and sampling rate.
        
        Args:
            duration: time in seconds for user to speak
            fs: sampling rate

        Returns:
            audio: the recorded audio
        """
        self.play_audio_without_messages(start_audio_path)
        print("Listening...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        self.play_audio_without_messages(stop_audio_path)
        print("Recording finished")
        return audio

    def save_audio(self, audio, filename="input.wav", fs=44100) -> str:
        """Save the recorded audio to a WAV file.
        Args:
            audio: the recorded audio
            filename: file name
            fs: sampling rate

        Returns:
            filename
        """
        wavio.write(filename, audio, fs, sampwidth=2)
        return filename

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe the audio at the given path using OpenAI Whisper.
        Args:
            audio_path: where the stored audiofile is

        Returns:
            transcribed speech-to-text
        """
        result = self.model.transcribe(audio_path)
        os.remove(audio_path)
        return result["text"]

    def stream_and_play(self, text: str) -> None:
        """Use OpenAI's text-to-speech API to stream the audio and play the bot's response.
        Args:
            text: the text that BKGraph Voice needs to vocalize

        Returns:
            None
        """
        response = self.client.audio.speech.create(
            model="tts-1-1106",
            voice="alloy",
            input=text
        )

        byte_stream = io.BytesIO(response.content)
        audio_segment = AudioSegment.from_file(byte_stream, format="mp3")
        play(audio_segment)