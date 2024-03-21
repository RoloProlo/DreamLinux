import tkinter as tk
from gtts import gTTS
import pygame
import sounddevice as sd
import speech_recognition as sr
from io import BytesIO
from speechbubble import SpeechBubble



class StoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(background='#1D2364')

        # Initialize the recognizer and microphone
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=2)

        self.left_bubble = SpeechBubble(self, bg='#1D2364', bd=0, highlightthickness=0)
        self.left_bubble.place(relx=0.1, rely=0.1, anchor='w')

        self.right_bubble = SpeechBubble(self, bg='#1D2364', bd=0, highlightthickness=0)
        self.right_bubble.place(relx=0.9, rely=0.2, anchor='e')

        self.conversation_button = tk.Button(self, text="Start Conversation",
                                             command=self.start_conversation)
        self.conversation_button.pack()

        self.user_input = tk.Entry(self)
        self.user_input.pack()

        self.submit_button = tk.Button(self, text="Submit",
                                       command=self.save_input)
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

    def record_audio(self):
        # Start a new thread to record the audio without freezing the GUI
        self.after(100, self._record_audio_thread)

    def _record_audio_thread(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        # Save the audio in a WAV file in the current directory
        with open("user_recording.wav", "wb") as f:
            f.write(audio.get_wav_data())

    def save_input(self):
        # Load the recorded audio and try to recognize the speech
        with sr.AudioFile("user_recording.wav") as source:
            audio = self.recognizer.record(source)
        try:
            # Transcribe the recorded audio to text
            text = self.recognizer.recognize_google(audio)
            # Update the right speech bubble with the transcribed text
            self.right_bubble.update_text(text)
            # Print the recognized text to the console
            print("Recognized text:", text)
        except sr.UnknownValueError:
            # Handle the exception if the audio could not be understood
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            # Handle the exception if there was a problem with the Google API
            print(f"Could not request results from Google Speech Recognition service; {e}")

