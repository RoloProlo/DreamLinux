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
        self.description = "I dreamt about an elephant that lived in a rainbow castle"
        self.meaning = ""
        self.characters = ""
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

        # self.start_gen(self.description)

    def start_gen(self, description):
        self.description = description
        self.generate_and_display_image(self.description)
        self.generate_meaning(self.description)
        self.generate_characters(self.description)

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

        # Make the API call to DALL-E for image generation
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


    def generate_meaning(self, prompt):
        if not prompt:
            messagebox.showinfo("Input Required", "Please enter a dream description.")
            return

        enhanced_prompt = f"consider this story: {prompt}. What could be the meaning behind this dream?"

        headers = {
            "Authorization": f"Bearer {self.API_KEY}"
        }

        data = {
            "model": "text-davinci-003",
            "prompt": enhanced_prompt,
            "max_tokens": 200,  # Adjust as needed
            "temperature": 0.7,  # Adjust as needed
            "top_p": 1,  # Adjust as needed
            "frequency_penalty": 0,  # Adjust as needed
            "presence_penalty": 0,  # Adjust as needed
            "best_of": 1  # Adjust as needed
        }

        # Make the API call to GPT-4 for meaning generation
        response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data)

        if response.status_code == 200:
            # Assuming the response['data'] contains text
            try:
                meaning = response.json()['choices'][0]['text'].strip()
                messagebox.showinfo("Meaning", meaning)

                # self.save_image()
                print(meaning)
   
            except KeyError as e:
                messagebox.showerror("Error", f"Failed to parse meaning data. {e}")
        else:
            messagebox.showerror("Error", "Failed to generate meaning. Please check your API key and internet connection.")

    def generate_characters(self, prompt):
        if not prompt:
            messagebox.showinfo("Input Required", "Please enter a dream description.")
            return

        enhanced_prompt = f"consider this story: {prompt}. Give me a list of all the characters, with no subdivision. every single character should be mentioned separately on its own line"

        headers = {
            "Authorization": f"Bearer {self.API_KEY}"
        }

        data = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": enhanced_prompt,
            "max_tokens": 100,  # Adjust as needed
            "temperature": 0.7,  # Adjust as needed
            "top_p": 1,  # Adjust as needed
            "frequency_penalty": 0,  # Adjust as needed
            "presence_penalty": 0,  # Adjust as needed
            "best_of": 1  # Adjust as needed
        }

        # Make the API call to GPT-4 for character prompt
        response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data)

        if response.status_code == 200:
            # Assuming the response['data'] contains text
            try:
                characters = response.json()['choices'][0]['text'].strip()
                messagebox.showinfo("Characters", characters)
                self.characters = characters  # Store the characters for future use
                print(characters)
            except KeyError as e:
                messagebox.showerror("Error", f"Failed to parse character data. {e}")
        else:
            messagebox.showerror("Error", "Failed to prompt for characters. Please check your API key and internet connection.")


    def insert_image_into_database(self, image_path, description):
        conn = sqlite3.connect('DreamImages.db')  # Adjust with your actual database path
        cursor = conn.cursor()

        # Prepare data
        date_str = datetime.now().strftime('%d/%m/%Y')
        # Assuming the description variable contains the image description
        # Leave 'meaning' and 'characters' as empty strings or NULL if not applicable
        query = '''INSERT INTO DreamImages (date, image, description, meaning, characters)
                   VALUES (?, ?, ?, ?, ?)'''
        cursor.execute(query, (date_str, image_path, description, '', ''))

        conn.commit()
        conn.close()


    def save_image(self):
        if self.global_img is not None:
            # Ensure the 'dreams' directory exists
            save_directory = 'dreams'
            os.makedirs(save_directory, exist_ok=True)

            # Construct the base file name with the current date
            date_str = datetime.now().strftime('%Y-%m-%d')
            base_file_path = os.path.join(save_directory, date_str)

            # TRY
            base_file_path = os.path.join(save_directory, date_str).replace("\\", "/")


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


# # Create a Tkinter application instance
# app = tk.Tk()

# # Set the window title
# app.title("Generation Screen")

# # Set the window size
# app.geometry("800x600")

# # Create an instance of the GenerationScreen class
# generation_screen = GenerationScreen(app, None)  # Pass None as controller for now

# # Run the Tkinter event loop
# app.mainloop()