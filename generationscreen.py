import tkinter as tk
from PIL import Image, ImageTk
import random
from tkinter import messagebox, filedialog
import requests
from io import BytesIO
import os
from datetime import datetime
from tkmacosx import Button
import sqlite3
from openai import OpenAI


class GenerationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(background='#1D2364')
        self.canvas = tk.Canvas(self, bg="#1D2364", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.description = ""
        self.image_label = tk.Label(self)  # Placeholder for the image
        self.text_label = tk.Label(self, font=("Helvetica", 20), bg="#1D2364", fg="white", wraplength=parent.winfo_screenwidth())  # To display the transcribed text
        self.text_label.pack(side="top", pady=20)  # Adjust positioning as needed
        self.API_KEY = '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'
        self.global_img = None
        self.image_label = tk.Label(self)
        self.image_label.pack(fill="both", expand=True)  # Pre-pack the label to ensure it's ready
        self.conn = sqlite3.connect('DreamImages.db')
        self.cursor = self.conn.cursor()

        self.back_button = Button(self, text='Go Back', command=self.go_back, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def start_gen(self, description):
        self.description = description
        self.generate_and_display_image(self.description)

    def generate_and_display_image(self, prompt):
        if not prompt:
            messagebox.showinfo("Input Required", "Please enter a dream description.")
            return

        fantasy_descriptors = ["enchanted", "mystical", "dreamy", "magical"]
        enhanced_prompt = f"Animated {prompt} in a {random.choice(fantasy_descriptors)} setting"

        headers = {
            "Authorization": f"Bearer {self.API_KEY}"
        }

        data = {
            "model": "dall-e-3",
            "prompt": enhanced_prompt,
            "n": 1,  # Number of images to generate
            "size": "1024x1024",  # Image size
            "quality": "hd"
        }

        # Make the API call to DALL-E
        response = requests.post("https://api.openai.com/v1/images/generations", headers=headers, json=data)

        if response.status_code == 200:
            # Assuming the response['data'] contains a list of generated images
            try:
                image_data = response.json()['data'][0]['url']
                # Use requests to get the image from the URL
                response = requests.get(image_data)
                image_bytes = BytesIO(response.content)

                # Update the global image object and display the image
                self.global_img = Image.open(image_bytes)

                self.save_image()
                # self.update_image_fullscreen()  # Call updated method to display the image fullscreen
                # self.save_image()
            except KeyError as e:
                messagebox.showerror("Error", f"Failed to parse image data. {e}")
        else:
            messagebox.showerror("Error", "Failed to generate image. Please check your API key and internet connection.")

    def insert_image_into_database(self, image_path, description):
        # Connect to the SQLite database for dream images
        conn = sqlite3.connect('DreamImages.db')  
        cursor = conn.cursor()

        # Connect to the SQLite database for characters
        conn_characters = sqlite3.connect('Characters.db')
        cursor_characters = conn_characters.cursor()

        # Connect to the SQLite database for characters in dream
        conn_dreamcast = sqlite3.connect('DreamCast.db')
        cursor_dreamcast = conn_dreamcast.cursor()


        # Prepare data
        date_str = datetime.now().strftime('%d/%m/%Y')
        # Assuming the description variable contains the image description
        # Leave 'meaning' and 'characters' as empty strings or NULL if not applicable
        query = '''INSERT INTO DreamImages (date, image, description, meaning, characters)
                   VALUES (?, ?, ?, ?, ?)'''
        cursor.execute(query, (date_str, image_path, description, '', ''))

        conn.commit()
        print("New dream image added to the DreamImages database.")

        # Retrieve the dream image id
        cursor.execute("SELECT id FROM DreamImages WHERE date=?", (date_str,))
        dream_image_id = cursor.fetchone()[0]

        # Insert characters into DreamCast table
        for character in cursor_characters:
            # Check if the character exists in the Characters database
            cursor_characters.execute("SELECT * FROM Characters WHERE name=?", (character,))
            existing_character = cursor_characters.fetchone()

            if not existing_character:
                # Insert new character into the Characters database
                cursor_characters.execute('''INSERT INTO Characters (name, description) VALUES (?, ?)''', (character, "No description available"))
                conn_characters.commit()
                print(f"New character '{character}' added to the Characters database.")
            else:
                print(f"Character '{character}' already present in the Characters database.")

            cursor_dreamcast.execute('''INSERT INTO DreamCast (dream_image_id, character) 
                                        VALUES (?, ?)''', (dream_image_id, character))
            conn_dreamcast.commit()
            print(f"Character '{character}' added to the DreamCast database for the dream image.")

        conn.close()
        conn_characters.close()
        conn_dreamcast.close()


    def save_image(self):
        if self.global_img is not None:
            # Ensure the 'dreams' directory exists
            save_directory = 'dreams'
            os.makedirs(save_directory, exist_ok=True)

            # Construct the base file name with the current date
            date_str = datetime.now().strftime('%Y-%m-%d')
            base_file_path = os.path.join(save_directory, date_str)

            # Check if a file with the same name exists and adjust the name accordingly
            counter = 1
            file_path = f"{base_file_path}.png"
            while os.path.exists(file_path):
                file_path = f"{base_file_path} v.{counter}.png"
                counter += 1

            # Save the image
            self.global_img.save(file_path)
            self.insert_image_into_database(file_path, self.description)
            print(f"Image saved as {file_path}")  # Optional: print the path for confirmation
        else:
            messagebox.showinfo("No Image", "There is no image to save. Please generate an image first.")


    def go_back(self):
        home_screen = self.controller.get_frame("HomeScreen")
        if home_screen:
            home_screen.refresh_images()
        self.controller.show_frame("HomeScreen")
        self.conn.close()  # Close the database connection when leaving this screen