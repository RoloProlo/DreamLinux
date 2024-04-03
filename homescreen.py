import tkinter as tk
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime


class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.date_label = tk.Label(self, font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white")
        self.time_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.controller = controller
        self.configure(background='#1D2364')

        self.image_list = []
        self.current_image_index = 0
        self.current_id = 0
        self.fullscreen_overlay = None
        self.overlay_label = None

        self.image_label = None  # Initialize image_label

        # Load images from database and create UI elements
        self.load_images_from_database()
        self.setup_ui()

    def setup_ui(self):
        # Display the current time
        self.time_label.pack()

        # Display the date of the current image
        self.date_label.pack()

        self.update_time_date()
        self.display_current_image()
        self.create_buttons()

    def reset_screen(self):
        self.load_images_from_database()
        self.setup_ui()


    def update_time_date(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M:%S"))
        self.time_label.after(1000, self.update_time_date)

    def load_images_from_database(self):
        conn = sqlite3.connect('DreamImages.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, image FROM DreamImages ORDER BY date DESC")
        self.image_list = cursor.fetchall()
        conn.close()

    def display_current_image(self):

        self.controller.set_shared_data("current_image_index", self.current_image_index)
        # Ensure there are images to display
        self.current_id = len(self.image_list) - self.current_image_index
        if not self.image_list or self.current_image_index >= len(self.image_list):
            # Optionally, display a placeholder or message when there are no images
            if self.image_label is not None:
                self.image_label.destroy()
            self.image_label = tk.Label(self, text="No images available", background='#1D2364', fg='white')
            self.image_label.pack(side="top", fill="both", expand=True)
            return

        # Clear the current image if it exists
        if self.image_label is not None:
            self.image_label.destroy()

        # Get the current image and date
        # Assuming you only need date and image_path, and id is not used directly here.
        _, current_date, image_path = self.image_list[self.current_image_index]
        self.controller.set_shared_data("current_image_index", self.current_image_index)
        self.controller.set_shared_data("current_id", self.current_id)


        # Update the image
        original_image = Image.open(image_path)
        photo = ImageTk.PhotoImage(original_image)

        # Create a label to display the image
        self.image_label = tk.Label(self, image=photo, background='#1D2364')
        self.image_label.image = photo  # Keep a reference!
        self.image_label.pack(side="top", fill="both", expand=True)

        # Update the date label to show the date of the current image
        self.date_label.config(text=current_date)

        enlarge_button = tk.Button(self, text="⇐", command=lambda: self.enlarge_image(image_path))
        enlarge_button.place(relx=0.884, rely=0.19, anchor=tk.CENTER)
        self.create_buttons()


    def previous_image(self):
        if self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.controller.set_shared_data("current_image_index", self.current_image_index)
            self.display_current_image()
            print(self.current_image_index)

    def next_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.controller.set_shared_data("current_image_index", self.current_image_index)
            self.display_current_image()
            print(self.current_image_index)

    def enlarge_image(self, image_path):
        # Clear the window
        for widget in self.winfo_children():
            widget.place_forget()

        # Open the image
        image = Image.open(image_path)
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
        self.overlay_label = tk.Label(self, image=self.fullscreen_overlay, background='#1D2364')
        self.overlay_label.place(x=0, y=(600 - new_height) // 2)  # Adjust positioning
        self.overlay_label.bind("<Button-1>", self.exit_fullscreen)

    def refresh_images(self):
        """Refresh the list of images from the database and display the latest one."""
        self.load_images_from_database()
        # Reset the current image index to show the latest image
        if self.image_list:
            self.current_image_index = 0
        self.display_current_image()

    def exit_fullscreen(self, event=None):
        # Only try to destroy the overlay if it exists
        if self.overlay_label is not None:
            self.overlay_label.destroy()
            self.overlay_label = None
        # Restore the widgets or rebuild the interface as needed
        self.display_current_image()
        self.create_buttons()

    def go_description(self):
        self.controller.show_frame("DescriptionScreen")
        description_screen = self.controller.get_frame("DescriptionScreen")
        description_screen.setup_ui()  # Ensure this method updates the UI based on the current index

    def go_meaning(self):
        self.controller.show_frame("MeaningScreen")
        meaning_screen = self.controller.get_frame("MeaningScreen")
        meaning_screen.setup_ui()  # Ensure this method updates the UI based on the current index
 
    def go_characters(self):
        self.controller.show_frame("CharacterScreen")
        character_screen = self.controller.get_frame("CharacterScreen")
        character_screen.setup_ui()  # Ensure this method updates the UI based on the current index

    def create_buttons(self):

        # Navigation buttons
        next_button = tk.Button(self, text=">>", command=self.next_image)
        prev_button = tk.Button(self, text="<<", command=self.previous_image)

        # Place navigation buttons
        next_button.place(relx=0.95, rely=0.5, anchor=tk.CENTER)
        prev_button.place(relx=0.05, rely=0.5, anchor=tk.CENTER)

        # Calculate button width and the spacing between them
        button_width = 100  # Fixed width for each button
        parent_width = 1024  # Assuming the parent frame's width is the whole window width
        space_between_buttons = (parent_width - (5 * button_width)) / 6  # Equally space out buttons

        # Button 1
        button1 = tk.Button(self, text="Description", pady=10, bg='#8E97FF', fg='white', command=self.go_description)
        button1.place(x=space_between_buttons, y=520, width=button_width, height=30)  # Adjust y for bottom placement
        # Button 2
        button2 = tk.Button(self, text="Meaning", pady=10, bg='#8E97FF', fg='white', command=self.go_meaning)
        button2.place(x=space_between_buttons * 2 + button_width, y=520, width=button_width, height=30)
        # Button 3
        button3 = tk.Button(self, text="Characters", pady=10, bg='#8E97FF', fg='white', command=self.go_characters)
        button3.place(x=space_between_buttons * 3 + button_width * 2, y=520, width=button_width, height=30)
        # Button 4
        button4 = tk.Button(self, text="Story", command=lambda: self.controller.show_frame("StoryScreen"))
        button4.place(x=space_between_buttons * 4 + button_width * 3, y=520, width=button_width, height=30)  # Adjust y for bottom placement
        # # Button 5
        button5 = tk.Button(self, text="Alarm", bg='#414BB2', fg='white', command=lambda: self.controller.show_frame("AlarmScreen"))
        button5.place(x=space_between_buttons * 5 + button_width * 4, y=520, width=button_width,
                      height=30)  # Adjust y for bottom placement


