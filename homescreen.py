import tkinter as tk
from tkmacosx import Button
from PIL import Image, ImageTk
import subprocess
from datetime import datetime, date
import sqlite3
import sys

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Set the controller attribute
        tk.Frame.__init__(self, parent)

        self.configure(background='#1D2364')  # Set a background color

        # Connect to the SQLite database for dream images
        conn = sqlite3.connect('DreamImages.db')
        cursor = conn.cursor()

        # Connect to the SQLite database for characters
        conn_characters = sqlite3.connect('Characters.db')
        cursor_characters = conn_characters.cursor()

        # Connect to the SQLite database for characters in dream
        conn_dreamcast = sqlite3.connect('DreamCast.db')
        cursor_dreamcast = conn_dreamcast.cursor()

        # Display the current time
        self.time_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.time_label.pack()

        # Display the current date
        self.date_label = tk.Label(self, font=("Helvetica", 14), bg="#1D2364", fg="white")
        self.date_label.pack()  # Space between date and the image

        #Functions

        self.update_time_date()
        self.display_image()
        self.create_buttons()

    def update_time_date(self):
        # Get the current time and date
        now = datetime.now()
        time_string = now.strftime("%H:%M:%S")
        date_string = now.strftime("%d-%m-%Y")

        self.time_label.config(text=time_string)
        self.date_label.config(text=date_string)

        # Update the labels every 1000ms (1 second)
        self.time_label.after(1000, self.update_time_date)

    def display_image(self):
        # Load Image
        #image_path = '/home/roland/Mystical/Images/image1.png'
        image_path = 'images/image1.png'
        original_image = Image.open(image_path)

        # Resize the image to make it smaller, adjust (width, height) as needed
        photo = ImageTk.PhotoImage(original_image)

        # Create a label to display the image with padding to show the background
        image_label = tk.Label(self, image=photo, background='#1D2364')
        image_label.image = photo  # Keep a reference!
        image_label.pack(padx=20, pady=20)  # Adjust padding as needed

    def create_buttons(self):
        # Calculate button width and the spacing between them
        button_width = 100  # Fixed width for each button
        parent_width = 1024  # Assuming the parent frame's width is the whole window width
        space_between_buttons = (parent_width - (5 * button_width)) / 6  # Equally space out buttons

        # Button 1
        button1 = tk.Button(self, text="Descriptions", command=lambda: self.controller.show_frame("DescriptionScreen"))
        button1.place(x=space_between_buttons, y=520, width=button_width, height=30)  # Adjust y for bottom placement


        # Button 2
        button2 = tk.Button(self, text="Meaning", command=lambda: self.controller.show_frame("MeaningScreen"))
        button2.place(x=space_between_buttons * 2 + button_width, y=520, width=button_width, height=30)

        # Button 3
        button3 = tk.Button(self, text="Characters", command=lambda: self.controller.show_frame("CharacterScreen"))
        button3.place(x=space_between_buttons * 3 + button_width * 2, y=520, width=button_width, height=30)

        # Button 4
        button4 = tk.Button(self, text="Story", command=lambda: self.controller.show_frame("StoryScreen"))
        button4.place(x=space_between_buttons * 4 + button_width * 3, y=520, width=button_width, height=30)  # Adjust y for bottom placement

        # Button 5
        button5 = tk.Button(self, text="Alarm", command=lambda: self.controller.show_frame("AlarmScreen"))
        button5.place(x=space_between_buttons * 5 + button_width * 4, y=520, width=button_width, height=30)  # Adjust y for bottom placement
