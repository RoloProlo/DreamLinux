import tkinter as tk
from gtts import gTTS
from tkmacosx import Button
import pygame
import pyaudio
import sounddevice as sd
import speech_recognition as sr
from io import BytesIO
from datetime import datetime
from speechbubble import SpeechBubble
from scipy.io.wavfile import write
import numpy as np
from database import DB
import sqlite3
import threading
import soundfile as sf  # For saving the recording
import threading
import speech_recognition as sr

class StoryScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.confirm_button = Button(self, text="Confirm", command=self.confirm_recording, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.again_button = Button(self, text="Again", command=self.restart_recording, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.controller = controller
        self.configure(background='#1D2364')
        self.clock_label = tk.Label(self, font=("Helvetica", 44, "bold"), bg="#1D2364", fg="white")
        self.canvas = tk.Canvas(self, bg="#1D2364", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.setup_ui()
        self.description = ""
        self.stop_recording = False
        self.recording_thread = None

    def setup_ui(self):
        bubble, text_widget, triangle = self.create_speech_bubble(40, 50, 250, 160, 50, 20, "")
        self.clock_label = tk.Label(self, font=("Helvetica", 44, "bold"), bg="#1D2364", fg="white")
        self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

        self.start_button = Button(self, text='Start Speech', command=self.start_conversation, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.start_button.place(relx=0.4, rely=0.95, anchor=tk.CENTER)

        self.skip_button = Button(self, text='Skip', command=lambda: self.skip_dev(), bg='#414BB2', fg='white', pady=10, borderless=1)
        self.skip_button.place(relx=0.3, rely=0.95, anchor=tk.CENTER)

        self.back_button = Button(self, text='Go Back', command=self.go_back, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        self.update_clock()

        # back_button = Button(self, text='Go Back', command=lambda: self.go_back(), bg='#414BB2', fg='white', pady=10, borderless=1)
        #
        # start_button = Button(self, text='Start speech', command=lambda: self.start_conversation(), bg='#414BB2', fg='white', pady=10, borderless=1)
        # back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)
        # start_button.place(relx=0.4, rely=0.95, anchor=tk.CENTER)
        #
        # self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        # self.canvas.place(x=100, y=100, width=850, height=430)
    def skip_dev(self):
        generation_screen = self.controller.get_frame("GenerationScreen")
        generation_screen.start_gen("testing this prompt")
        self.controller.show_frame("GenerationScreen")

    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)  # Use 'self.after' instead of 'self.clock_label.after'

    def create_speech_bubble(self, x, y, width, height, radius, pointer_offset, text):
        # Draw the rounded rectangle
        bubble = self.create_rounded_rectangle(x, y, x + width, y + height, radius, fill='white', outline='black')

        # Add the text with wrapping
        text_widget = self.canvas.create_text(x + width / 2, y + height / 2, text=text, fill='black', font=("Helvetica", 26), width=width - 20, anchor='center')

        # Draw the pointer triangle
        triangle = self.canvas.create_polygon(x + width / 2 - pointer_offset, y + height,
                                              x + width / 2 + pointer_offset, y + height,
                                              x + width / 2, y + height + pointer_offset,
                                              fill='white', outline='')

        return bubble, text_widget, triangle
    def create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1 + radius, y1,
                  x2 - radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius,
                  x2, y2 - radius, x2, y2 - radius, x2, y2, x2 - radius, y2,
                  x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius,
                  x1, y1 + radius, x1, y1 + radius, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def speak(self, text, callback=None):
        tts = gTTS(text)
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        pygame.mixer.init()
        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        if callback:
            callback()

    def transcribe_audio(self, file_path):
        # Initialize recognizer and audio file
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
        try:
            # Transcribe the audio file
            text = recognizer.recognize_google(audio_data)
            print("Transcribed text:", text)
            self.description = text
            # Update the right speech bubble with the transcribed text
            self.update_speech_bubble(text, 1)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")


    def start_conversation(self):
        # Say the initial question and update the left speech bubble
        bubble, text_widget, triangle = self.create_speech_bubble(40, 50, 250, 160, 50, 20, "Goodmorning, what did you dream about last night?")

        self.speak("Good morning, what did you dream about? Please tell me", self.show_stop_button)


    def show_stop_button(self):
        # Method to show the "Stop Recording" button and start recording in a separate thread
        self.stop_button = Button(self, text="Stop Recording", command=self.stop_recording_action, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.stop_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Start recording in a separate thread to avoid blocking the UI
        threading.Thread(target=self.record_audio, daemon=True).start()
        print("Recording should start now...")

    def record_audio(self, samplerate=44100, channels=2):
        print("Recording...")
        bubble, text_widget, triangle = self.create_speech_bubble(700, 200, 250, 160, 50, 20, "")
        duration = 30  # Maximum duration in seconds, adjust as needed
        self.stop_recording = False
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='float64')
        while not self.stop_recording:
            sd.sleep(100)  # Check every 100ms if stop_recording is True
        sd.stop()
        # Save the recording
        sf.write('output.wav', recording, samplerate)
        print("Recording stopped and saved to 'output.wav'.")
        # Transcribe the recording
        self.transcribe_audio('output.wav')

    def update_speech_bubble(self, text, side):
        if side == 1:
            bubble, text_widget, triangle = self.create_speech_bubble(700, 200, 250, 160, 50, 20, text)
        else:
            bubble, text_widget, triangle = self.create_speech_bubble(40, 50, 250, 160, 50, 20, "Goodmorning, what did you dream about last night?")

    def stop_recording_action(self):
        self.stop_recording = True
        self.stop_button.place_forget()
        self.show_confirmation_buttons()
        # Hide the stop button
        if self.recording_thread:
            self.recording_thread.join()

    def show_confirmation_buttons(self):
        self.confirm_button = Button(self, text="Confirm", command=self.confirm_recording, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.again_button = Button(self, text="Again", command=self.restart_recording, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.again_button.place(relx=0.4, rely=0.9, anchor=tk.CENTER)

        self.confirm_button.place(relx=0.6, rely=0.9, anchor=tk.CENTER)

    def restart_recording(self):
        self.again_button.place_forget()
        self.confirm_button.place_forget()
        self.start_conversation()

    def give_description(self):
        return self.description

    def confirm_recording(self):
        print("Confirmed transcription.")
        description = self.description
        self.again_button.place_forget()
        self.confirm_button.place_forget()

        generation_screen = self.controller.get_frame("GenerationScreen")
        generation_screen.start_gen(description)
        self.controller.show_frame("GenerationScreen")




    def go_back(self):
        self.controller.show_frame("HomeScreen")
        self.conn.close()  # Close the database connection when leaving this screen
