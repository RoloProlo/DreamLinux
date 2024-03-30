import tkinter as tk
from PIL import Image, ImageTk
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import sqlite3
from tkmacosx import Button


class CharacterDetailScreen(tk.Frame):
    def __init__(self, parent, controller, character_name, character_description):
        super().__init__(parent, background='#1D2364')
        self.controller = controller
        self.character_name = character_name
        self.character_description = character_description  # Make sure to include this in the arguments


        # Define all your widgets here
        self.name_label = tk.Label(self, text=self.character_name, font=("Helvetica", 24, "bold"), fg="white", bg="#8E97FF")
        self.description_title_label = tk.Label(self, text="Description", font=("Helvetica", 24, "bold"), fg="white", bg="#8E97FF")
        self.description_text = tk.Text(self, font=("Helvetica", 18), fg="white", bg="#414BB2", wrap="word", height=10, width=50)
        self.increase_button = Button(self, text="+", command=self.increase_text_size, bg='#1D2364', fg='white')
        self.decrease_button = Button(self, text="-", command=self.decrease_text_size, bg='#1D2364', fg='white')
        self.edit_button = Button(self, text='Edit', command=self.edit, bg='#414BB2', fg='white')
        self.back_button = Button(self, text='Back', command=self.hide_screen, bg='#414BB2', fg='white')

        # Now that all widgets are defined, configure them or lay them out
        self.layout_widgets()

        # row = self.cursor_characters.fetchone()
        #
        # if row:
        #     description = row[0]
        #     print(character_name, description)


        # Character Image
        # self.symbol = open_symbol()  # Assuming open_symbol() is accessible
        # self.char_symbol = tk.Label(self, image=self.symbol, borderwidth=0)
        # self.char_symbol.image = self.symbol  # Keep a reference


    def show_screen(self, character_name=None, character_description=None):
        # Optional: Update content if new character details are provided
        if character_name and character_description:
            self.name_label.config(text=character_name)
            self.description_text.config(state='normal')
            self.description_text.delete('1.0', tk.END)
            self.description_text.insert('end', character_description)
            self.description_text.config(state='disabled')

        self.pack(fill="both", expand=True)

    def layout_widgets(self):
        self.name_label.config(text=self.character_name)
        self.name_label.pack(pady=(10, 0))

        self.description_title_label.pack(pady=(10, 0))

        self.description_text.insert('end', self.character_description)
        self.description_text.pack(pady=(5, 20))
        self.description_text.config(state='disabled')  # Make the text read-only initially

        self.increase_button.pack(side='left', padx=(10, 5), pady=10)
        self.decrease_button.pack(side='left', padx=(5, 10), pady=10)
        self.edit_button.pack(side='left', padx=10, pady=10)
        self.back_button.pack(side='right', padx=10, pady=10)

        self.description_text.delete('1.0', tk.END)  # Clear existing text
        self.description_text.insert('end', self.character_description or "No description available")  # Insert description text

    def hide_screen(self):
        self.pack_forget()
        # Optionally, call a method to show the main character list screen

    def increase_text_size(self):
        font = self.description_text.cget("font").split()
        size = int(font[-1]) + 1
        self.description_text.config(font=(font[0], size))

    def decrease_text_size(self):
        font = self.description_text.cget("font").split()
        size = max(int(font[-1]) - 1, 8)  # Prevent size from getting too small
        self.description_text.config(font=(font[0], size))

    def edit(self):
        if self.description_text.cget('state') == 'normal':
            self.description_text.config(state='disabled')
            # Save changes to database here
        else:
            self.description_text.config(state='normal')

