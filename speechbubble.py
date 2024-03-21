import tkinter as tk
from gtts import gTTS
import pygame
from io import BytesIO

class SpeechBubble(tk.Canvas):
    def __init__(self, parent, text="", **kwargs):
        super().__init__(parent, **kwargs)
        self.text = text
        self.create_bubble()

    def create_bubble(self):
        bubble_width = 200
        bubble_height = 100
        pad_x = 10
        pad_y = 10
        self.configure(width=bubble_width + pad_x, height=bubble_height + pad_y)
        self.create_oval(pad_x, pad_y, bubble_width, bubble_height, fill='white')
        self.create_text(bubble_width // 2 + pad_x // 2, bubble_height // 2 + pad_y // 2, text=self.text, width=bubble_width - pad_x)

    def update_text(self, text):
        self.text = text
        self.delete("all")
        self.create_bubble()