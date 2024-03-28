import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime, date
import sqlite3
import sys
from PIL import ImageTk, Image
import subprocess
from tkmacosx import Button


class CharacterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Set the controller attribute
        tk.Frame.__init__(self, parent)
        self.configure(background='#1D2364')

        self.clock_label = tk.Label(self, font=("Helvetica", 44, "bold"), bg="#1D2364", fg="white")

        # Connect to the SQLite database for dream images
        conn = sqlite3.connect('DreamImages.db')
        cursor = conn.cursor()
        # Connect to the SQLite database for character information
        conn_characters = sqlite3.connect('Characters.db')
        cursor_characters = conn_characters.cursor()

        current_index = 0
        # Access the data of the current dream image in the DreamImages database
        cursor.execute("SELECT * FROM DreamImages LIMIT 1 OFFSET ?", (current_index,))
        self.dream_image_data = cursor.fetchone()

        self.date = self.dream_image_data[1]

        cursor_characters.execute("SELECT name FROM Characters")
        self.characters = cursor_characters.fetchall()

        # Get the character names associated with this DreamImage
        character_names = self.dream_image_data[5].split(', ') if self.dream_image_data else []

        self.setup_ui()

    def setup_ui(self):
        self.clock_label.pack(pady=10, padx=10)
        self.update_clock()

        self.date = tk.Label(self, text=self.date, font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white", relief="flat", anchor="n")

        # Define buttons
        seeAll_button = Button(self, text="See all characters", command=self.see_all, pady=10, bg='#8E97FF', fg='white', borderless=1)
        back_button = Button(self, text='Back to image', command=self.controller.show_frame("HomeScreen"), bg='#414BB2', fg='white', pady=10, borderless=1)

        self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        self.date.place(relx=0.5, rely=0.12, anchor=tk.CENTER)
        seeAll_button.place(relx=0.65, rely=0.95, anchor=tk.CENTER)
        back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def display(self, characters):
        symbol = self.open_symbol()
        x_offset, y_offset = 30, 10  # Starting positions

        for name in characters:
            print(name)
            char_label = tk.Label(self, image=symbol)
            char_label.image = symbol  # Keep a reference.
            char_label.place(x=x_offset, y=y_offset)

            name_label = tk.Label(self, text=name, font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white")
            name_label.place(x=x_offset, y=y_offset + 170)

            x_offset += 200
            if x_offset > 750:
                x_offset = 30
                y_offset += 200

        back_button = Button(self, text='Back to characters', command=self.controller.show_frame("CharacterScreen"), bg='#414BB2', fg='white', pady=10, borderless=1)
        back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)


    def open_symbol(self):
        image = Image.open("images/character_symbol.jpg")
        # Resize the image
        image = image.resize((160, 160), Image.Resampling.LANCZOS)

        # Convert the Image object into a Tkinter-compatible photo image
        photo = ImageTk.PhotoImage(image)

        return photo

    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M")
        self.clock_label.config(text=current_time)
        self.clock_label.after(1000, self.update_clock)  # Update every 1000 milliseconds (1 second)

    def on_symbol_click(self, event):
        # Get the item ID of the clicked object
        current_tags = event.widget.find_withtag(tk.CURRENT)
        if current_tags:
            item_id = current_tags[0]
            ...
        else:
            print("debug")
            return

        # Get the text associated with the clicked object
        character_name = event.widget.find_withtag(f'{item_id}_text')[0]
        text = event.widget.itemcget(character_name, 'text')

    def see_all(self):
        self.names = []
        for name_tuple in self.characters:
            self.names.append(name_tuple[0])

        self.display(self.names)

    def go_back(self):
        self.controller.show_frame("HomeScreen")
        self.conn.close()  # Close the database connection when leaving this screen
