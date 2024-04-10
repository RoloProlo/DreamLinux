import tkinter as tk
from PIL import Image, ImageTk, ImageOps, ImageDraw
import sqlite3
from datetime import datetime
from PIL import Image
import numpy as np
from tkmacosx import Button


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
        self.image_path = ""

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



    def reset_screen(self):
        self.load_images_from_database()
        self.setup_ui()


    def update_time_date(self):
        now = datetime.now()
        self.time_label.config(text=now.strftime("%H:%M"))
        self.time_label.after(1000, self.update_time_date)

    def load_images_from_database(self):
        conn = sqlite3.connect('DreamImages.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, image FROM DreamImages ORDER BY id DESC")
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
        _, self.current_date, self.image_path = self.image_list[self.current_image_index]
        self.controller.set_shared_data("current_image_index", self.current_image_index)
        self.controller.set_shared_data("current_id", self.current_id)


        # Update the image
        original_image = Image.open(self.image_path)
        target_size = (1024, 600)
        resized_image = ImageOps.contain(original_image, target_size)
        photo = ImageTk.PhotoImage(resized_image)


        # Create a label to display the image
        self.image_label = tk.Label(self, image=photo, background='#1D2364')
        self.image_label.image = photo  # Keep a reference!
        self.image_label.pack(side="top", fill="both", expand=True)

        # Update the date label to show the date of the current image
        self.date_label.config(text=self.current_date)

        # display enlarge button
        # enlarge_button = Button(self, text="⇐", bg="#414BB2", fg="white", command=lambda: self.enlarge_image(), highlightbackground="#414BB2", borderless=0)
        # enlarge_button.config(width=50, height=50)
        # enlarge_button.place(relx=0.976, rely=0.184, anchor=tk.CENTER)

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

    def enlarge_image(self):
        # Clear the window
        for widget in self.winfo_children():
            widget.place_forget()

        # Open the image
        image = Image.open(self.image_path)
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
        character_screen.is_generation = False
        character_screen.forget_buttons()
        character_screen.setup_ui()  # Ensure this method updates the UI based on the current index


    def go_alarm(self):
        self.controller.show_frame("AlarmScreen")
        alarm_screen = self.controller.get_frame("AlarmScreen")
        alarm_screen.ready = False



    def create_buttons(self):

        enlarge_button = self.create_icon_only_button(self, "Icons/enlarge.png", self.enlarge_image)
        enlarge_button.config(width=50, height=50)
        enlarge_button.place(relx=0.956, rely=0.184, anchor=tk.CENTER)

        # Navigation buttons
        next_button = self.create_icon_only_button(self, "Icons/next.png", self.next_image)
        next_button.config(width=50, height=50)
        prev_button = self.create_icon_only_button(self, "Icons/back.png", self.previous_image)
        prev_button.config(width=50, height=50)

        # Place navigation buttons
        next_button.place(relx=0.95, rely=0.55, anchor=tk.CENTER)
        prev_button.place(relx=0.05, rely=0.55, anchor=tk.CENTER)

        # Calculate button width and the spacing between them
        button_width = 180  # Fixed width for each button
        parent_width = 1024  # Assuming the parent frame's width is the whole window width
        space_between_buttons = (parent_width - (5 * button_width)) / 6  # Equally space out buttons


        button1 = self.create_icon_button(self, "Icons/description.png", "Description", self.go_description)
        button1.place(x=space_between_buttons, y=520, width=button_width)  # Adjust x and y as needed

        button2 = self.create_icon_button(self, "Icons/meaning.png", "Meaning", self.go_meaning)
        button2.place(x=space_between_buttons * 2 + button_width, y=520, width=button_width)

        button3 = self.create_icon_button(self, "Icons/characters.png", "Characters", self.go_characters)
        button3.place(x=space_between_buttons * 3 + button_width * 2, y=520, width=button_width)

        button4 = self.create_icon_button(self, "Icons/story.png", "Story", lambda: self.controller.show_frame("StoryScreen"))
        button4.place(x=space_between_buttons * 4 + button_width * 3, y=520, width=button_width)  # Adjust y for bottom placement

        button5 = self.create_icon_button(self, "Icons/alarm.png", "Alarm", self.go_alarm)
        button5.place(x=space_between_buttons * 5 + button_width * 4, y=520, width=button_width)  # Adjust y for bottom placement


    def create_icon_only_button(self, parent, icon_path, command):
        # Load the icon
        icon_image = Image.open(icon_path)

        # Assuming a square shape for the button, set both dimensions equal for the icon size
        icon_size = 40  # Adjust the size as needed
        icon_image = icon_image.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon_image)

        # Define colors for normal and pressed states
        normal_bg = '#66ABC0'
        pressed_bg = '#5599AF'  # Darker shade for pressed state

        # Create an outer frame to simulate the darker edges with a slightly darker background.
        button_frame_outer = tk.Frame(parent, bg='#38aec7', bd=0, highlightthickness=0, padx=2, pady=2)

        # The inner frame holds the icon and has the original background color, making the button square.
        button_size = 50  # The total size of the button, slightly larger than the icon
        button_frame = tk.Frame(button_frame_outer, bg=normal_bg, bd=0, highlightthickness=0, width=button_size, height=button_size)
        button_frame.pack_propagate(False)  # Prevents the frame from shrinking to fit the icon
        button_frame.pack()

        # Create the icon label centered in the frame
        icon_label = tk.Label(button_frame, image=icon_photo, bg=normal_bg)
        icon_label.image = icon_photo  # Keep a reference!
        icon_label.pack(expand=True)

        # Function to change the background color when pressed
        def on_press(event):
            button_frame.config(bg=pressed_bg)
            icon_label.config(bg=pressed_bg)

        # Function to change the background color back when released and execute the command
        def on_release(event):
            button_frame.config(bg=normal_bg)
            icon_label.config(bg=normal_bg)
            command()

        # Bind the press and release events to provide visual feedback
        button_frame_outer.bind("<ButtonPress-1>", on_press)
        button_frame_outer.bind("<ButtonRelease-1>", on_release)
        icon_label.bind("<ButtonPress-1>", on_press)
        icon_label.bind("<ButtonRelease-1>", on_release)

        return button_frame_outer

    def create_icon_button(self, parent, icon_path, text, command):
        # Load the icon
        icon_image = Image.open(icon_path)

        # Resize the icon to a smaller size, e.g., 30x30 pixels
        icon_image = icon_image.resize((40, 40), Image.Resampling.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon_image)

        # Define colors for normal and pressed states
        normal_bg = '#66ABC0'
        pressed_bg = '#5599AF'  # Darker shade for pressed state

        # Create an outer frame to simulate the darker edges with a slightly darker background.
        button_frame_outer = tk.Frame(parent, bg='#38aec7', bd=0, highlightthickness=0, padx=2, pady=2)

        # The inner frame holds the content and has the original background color.
        button_frame = tk.Frame(button_frame_outer, bg=normal_bg, bd=0, highlightthickness=0)
        button_frame.pack(fill='both', expand=True)

        # Create the icon label with invisible padding
        icon_label = tk.Label(button_frame, image=icon_photo, bg=normal_bg)
        icon_label.image = icon_photo  # Keep a reference!

        # Create the text label with a larger font
        text_label = tk.Label(button_frame, text=text, bg=normal_bg, fg='white', font=("Helvetica", 20))

        # Use grid layout for precise control over placement
        button_frame.grid_columnconfigure(1, weight=1)
        icon_label.grid(row=0, column=0, sticky="w")
        text_label.grid(row=0, column=1, sticky="ew")

        # Function to change the background color when pressed
        def on_press(event):
            button_frame.config(bg=pressed_bg)
            icon_label.config(bg=pressed_bg)
            text_label.config(bg=pressed_bg)

        # Function to change the background color back when released and execute the command
        def on_release(event):
            button_frame.config(bg=normal_bg)
            icon_label.config(bg=normal_bg)
            text_label.config(bg=normal_bg)
            command()

        # Bind the press and release events
        button_frame_outer.bind("<ButtonPress-1>", on_press)
        button_frame_outer.bind("<ButtonRelease-1>", on_release)
        icon_label.bind("<ButtonPress-1>", on_press)
        icon_label.bind("<ButtonRelease-1>", on_release)
        text_label.bind("<ButtonPress-1>", on_press)
        text_label.bind("<ButtonRelease-1>", on_release)

        return button_frame_outer


