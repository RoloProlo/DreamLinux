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
import re


class GenerationScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(background='#1D2364')
        self.canvas = tk.Canvas(self, bg="#1D2364", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.description = "I had to help my friend from the past with the washing machine. but the washing machine was flying around and breaking down. I was stressed because I had a lot of appointments during the day and I needed to go. But it was raining and stormy, and I needed to pee so I went to a coffeeplace, but there kept being a woman in front of me."
        self.meaning = ""
        self.characters = ""
        self.image_label = tk.Label(self)  # Placeholder for the image
        self.text_label = tk.Label(self, font=("Helvetica", 20), bg="#1D2364", fg="white", wraplength=parent.winfo_screenwidth())  # To display the transcribed text
        self.text_label.pack(side="top", pady=20)  # Adjust positioning as needed
        self.API_KEY = 'secret'
        self.global_img = None
        self.image_label = tk.Label(self)
        self.image_label.pack(fill="both", expand=True)  # Pre-pack the label to ensure it's ready
        self.conn = sqlite3.connect('DreamImages.db')
        self.cursor = self.conn.cursor()

        self.prompted_generation = ""

        self.back_button = Button(self, text='Go Back', command=self.go_back, bg='#414BB2', fg='white', pady=10, borderless=1)
        self.back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        self.start_gen(self.description)


    def start_gen(self, description):
        self.description = description
        self.generate_meaning(self.description)
        self.generate_characters(self.description)

        character_screen = self.controller.get_frame("CharacterScreen")
        character_screen.generation_characters(self.characters)
        character_screen.set_buttons()
        self.controller.show_frame("CharacterScreen")


        # self.generate_and_display_image(self.description)

    def start_img(self):
        self.replace_names_with_descriptions()
        print(self.prompted_generation)
        self.generate_and_display_image(self.prompted_generation)
        return


    def replace_names_with_descriptions(self):
        # Connect to the database
        conn = sqlite3.connect('Characters.db')
        cursor = conn.cursor()
        dream_description = self.description

        # Fetch all character names and descriptions
        cursor.execute("SELECT name, description FROM Characters")
        characters = cursor.fetchall()

        def replace_function(match):
            # This function will be used to replace each match with the appropriate text
            name = match.group(0)  # The original text matched (preserving case)
            # Find the character tuple by case-insensitive name match
            character = next((c for c in characters if c[0].lower() == name.lower()), None)
            if character:
                _, description = character
                if description and description.strip() != "No description available":
                    return f"{name} ({description})"
            return name  # Return the name as is if no description is available or if not found

        # Compile a regular expression pattern that matches any of the character names
        # Use re.IGNORECASE for case-insensitive matching
        names_pattern = re.compile('|'.join(re.escape(name) for name, _ in characters), re.IGNORECASE)

        # Use the sub method to replace all occurrences found by the pattern
        # The replace_function determines the replacement text for each match
        self.prompted_generation = names_pattern.sub(replace_function, dream_description)

        conn.close()

    # def replace_names_with_descriptions(self):
    #     # Connect to the database
    #     conn = sqlite3.connect('Characters.db')
    #     cursor = conn.cursor()
    #     dream_description = self.description
    #
    #     # Fetch all character names and descriptions
    #     cursor.execute("SELECT name, description FROM Characters")
    #     characters = cursor.fetchall()
    #
    #     # Replace each name in the dream description with its description
    #     for name, description in characters:
    #         if name in dream_description:
    #             if description and description.strip() != "No description available":
    #                 replacement_text = f"{name} ({description})"
    #             else:
    #                 replacement_text = name  # If no valid description, just use the name without appending anything.
    #             dream_description = dream_description.replace(name, replacement_text)
    #
    #     conn.close()
    #     self.prompted_generation = dream_description

    def generate_and_display_image(self, prompt):
        if not prompt:
            messagebox.showinfo("I was walking when the old wise owl stopped me and said this is not Amsterdam You Fool, Run!")
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
            "size": "1792x1024",  # Image size
            "quality": "standard"
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
                self.go_back()

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
            "model": "gpt-3.5-turbo-instruct",
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
                self.meaning = meaning
                print(meaning)
   
            except KeyError as e:
                messagebox.showerror("Error", f"Failed to parse meaning data. {e}")
        else:
            messagebox.showerror("Error", "Failed to generate meaning. Please check your API key and internet connection.")


    def generate_characters(self, prompt):
        if not prompt:
            messagebox.showinfo("Input Required", "Please enter a dream description.")
            return
        enhanced_prompt = f"consider this story: {prompt}. Give me a list of all the characters, with no subdivision.\
                Every single character should be mentioned separately on its own line. Only include characters that are explicitely mentioned, and only include humans (so no objects).\
                The narrator, or the 'I' in the story should be listed as Me"
        headers = {
            "Authorization": f"Bearer {self.API_KEY}"
        }
        data = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": enhanced_prompt,
            "max_tokens": 100,  # Adjust as needed
            "temperature": 0.2,  # Adjust as needed <= could be helpful to adjust (lower = less creativity)
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
                characters_list = []
                for line in characters.split("\n"):
                    if line.strip():
                        # Check if line contains ". " and split accordingly, else just use the line as is
                        split_line = line.split(". ") if ". " in line else [line]
                        characters_list.append(split_line[-1])  # Append the last element which should be the character's name
                # Join characters with comma and save as a string
                characters_string = ', '.join(characters_list)
                print("test" + characters_string)
                self.characters = characters_string  # Store the characters list fo
                # Split the text into lines and extract characters
                # characters_list = [line.split(". ")[1] for line in characters.split("\n") if line.strip()]
                # print("list: ", characters_list)
                # # Join characters with comma and save as a string
                # characters_string = ', '.join(characters_list)
                # self.characters = characters_string  # Store the characters list for future use
                # print(characters_string)
            except KeyError as e:
                messagebox.showerror("Error", f"Failed to parse character data. {e}")
        else:
            messagebox.showerror("Error", "Failed to prompt for characters. Please check your API key and internet connection.")


    def insert_image_into_database(self, image_path, description, meaning, characters):
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
        query = '''INSERT INTO DreamImages (date, image, description, meaning, characters)
                   VALUES (?, ?, ?, ?, ?)'''
        cursor.execute(query, (date_str, image_path, description, meaning, characters))

        conn.commit()
        print("New dream image added to the DreamImages database.")

        # Retrieve the dream image id
        cursor.execute("SELECT id FROM DreamImages WHERE date=?", (date_str,))
        dream_image_id = cursor.fetchone()[0]

        # change characters to a list
        characters_list = characters.split(", ")

        # Insert characters into DreamCast table
        for character in characters_list:
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
            self.insert_image_into_database(file_path, self.description, self.meaning, self.characters)
            print(f"Image saved as {file_path}")  # Optional: print the path for confirmation
        else:
            messagebox.showinfo("No Image", "There is no image to save. Please generate an image first.")


    def go_back(self):
        home_screen = self.controller.get_frame("HomeScreen")
        if home_screen:
            home_screen.refresh_images()
            home_screen.enlarge_image()
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