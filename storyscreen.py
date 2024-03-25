import tkinter as tk
from gtts import gTTS
import pygame
import pyaudio
import sounddevice as sd
import speech_recognition as sr
from io import BytesIO
from speechbubble import SpeechBubble
from scipy.io.wavfile import write
import numpy as np


class StoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller
        self.configure(background='#1D2364')

        # Initialize the recognizer
        self.recognizer = sr.Recognizer()

        self.left_bubble = SpeechBubble(self, bg='#1D2364', bd=0, highlightthickness=0)
        self.left_bubble.place(relx=0.1, rely=0.1, anchor='w')

        self.right_bubble = SpeechBubble(self, bg='#1D2364', bd=0, highlightthickness=0)
        self.right_bubble.place(relx=0.9, rely=0.2, anchor='e')

        self.conversation_button = tk.Button(self, text="Start Conversation",
                                             command=self.start_conversation)
        self.conversation_button.pack()

        self.user_input = tk.Entry(self)
        self.user_input.pack()

        self.submit_button = tk.Button(self, text="Submit", command=self.start_conversation)

        self.submit_button.pack()

    def speak(self, text):
        # Update the left speech bubble with the text
        self.left_bubble.update_text(text)
        # Use gTTS to say the text
        tts = gTTS(text)
        # Save the speech to a BytesIO stream
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        # Initialize pygame mixer
        pygame.mixer.init()
        # Load the sound from the BytesIO stream
        pygame.mixer.music.load(fp)
        # Play the sound
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def start_conversation(self):
        # Say the initial question and update the left speech bubble
        self.speak("Good morning, what did you dream about? Please tell me")
        self.record_audio()

    def record_audio(self, duration=5, samplerate=44100, channels=2):
        print("Recording...")
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='float64')
        sd.wait()  # Wait until recording is finished
        print("Recording stopped.")

        # Optional: Save the recording to a WAV file
        write('output.wav', samplerate, np.int16(recording * 32767))
        print("Recording saved to 'output.wav'.")
