import tkinter as tk
from PIL import Image, ImageTk
import random
from tkinter import messagebox, filedialog
import requests
from io import BytesIO
import os
from datetime import datetime

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
                self.update_image_fullscreen()  # Call updated method to display the image fullscreen
                # self.save_image()
            except KeyError as e:
                messagebox.showerror("Error", f"Failed to parse image data. {e}")
        else:
            messagebox.showerror("Error", "Failed to generate image. Please check your API key and internet connection.")

    def update_image_fullscreen(self):
        image = self.global_img
        width, height = image.size

        # Set the new width to the window width and scale height to maintain aspect ratio
        window_width = 1024
        new_height = int(height * (window_width / width))
        resized_image = image.resize((window_width, new_height), Image.Resampling.LANCZOS)

        # If the resized height is greater than the window height, we need to crop the top and bottom
        if new_height > 600:
            # Calculate the amount to crop from the top and bottom
            crop_amount = (new_height - 600) // 2
            # Crop the image to the new dimensions to fit the window size exactly
            resized_image = resized_image.crop((0, crop_amount, window_width, new_height - crop_amount))
            new_height = 600  # After cropping, the height is the window height

        self.fullscreen_overlay = ImageTk.PhotoImage(resized_image)

        # Place the image Label to fill the window and align it centered vertically
        overlay_label = tk.Label(self, image=self.fullscreen_overlay, background='#1D2364')
        overlay_label.place(x=0, y=(600 - new_height) // 2)  # Center vertically
        overlay_label.bind("<Button-1>", self.exit_fullscreen)


        # if self.global_img:
        #     img_resized = self.global_img.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.Resampling.LANCZOS)
        #     photo = ImageTk.PhotoImage(img_resized)
        #     self.image_label.configure(image=photo)
        #     self.image_label.image = photo  # Keep a reference to avoid garbage collection
        # else:
        #     messagebox.showinfo("No Image", "There is no image to display.")

    def exit_fullscreen(self, event=None):
        # Hide the overlay
        if self.overlay_label:
            self.overlay_label.destroy()
            self.overlay_label = None

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
            print(f"Image saved as {file_path}")  # Optional: print the path for confirmation
        else:
            messagebox.showinfo("No Image", "There is no image to save. Please generate an image first.")
    #
    # def update_image(self, image_path):
    #     # Load and display the image specified by image_path
    #     img = Image.open(image_path)
    #     img = img.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.Resampling.LANCZOS)
    #     photo = ImageTk.PhotoImage(img)
    #     self.image_label.config(image=photo)
    #     self.image_label.image = photo  # Keep a reference!
    #     self.image_label.pack(fill="both", expand=True)
