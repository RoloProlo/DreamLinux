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

        self.setup_ui()

    def setup_ui(self):
        # Clock Label
        self.clock_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.clock_label.pack(pady=10, padx=10)
        self.update_clock()

        print("current character: ", self.character_name)
        print("description: ", self.character_description)

        # Create outer rounded rectangle as background
        self.canvas_outer = tk.Canvas(self, width=850, height=450, borderwidth=0, highlightthickness=0, bg="#1D2364")
        x1, y1, x2, y2, r = 50, 5, 800, 450, 50
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        self.canvas_outer.create_polygon(points, fill="#8E97FF", smooth=True)

        # Create inner rounded rectangle as background
        self.canvas_inner = tk.Canvas(self, width=500, height=300, borderwidth=0, highlightthickness=0, bg="#8E97FF")
        x1, y1, x2, y2, r = 50, 5, 500, 300, 50
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        self.canvas_inner.create_polygon(points, fill="#414BB2", smooth=True)

        # add character symbol
        symbol = self.open_symbol()
        char_symbol = tk.Label(image=symbol, borderwidth=0)
        char_symbol.image = symbol  # Keep a reference to the image to prevent it from being garbage collected

        # add text character information
        self.name_label = tk.Label(self, text=self.character_name, font=("Helvetica", 24, "bold"), fg="white", bg="#8E97FF")
        self.description_title_label = tk.Label(self, text="Description", font=("Helvetica", 24, "bold"), fg="white", bg="#8E97FF")
        # Add text inside the inner rectangle
        self.description_text = self.canvas_inner.create_text(80, 50, text=self.character_description,
                                font=("Helvetica", 18), fill="white", width=400, anchor="nw")

        # Create buttons for adjusting text size
        text_size = tk.Label(self, text="Text size", font=("Helvetica", 24, "bold"), bg='#1D2364', fg='white')
        self.increase_button = Button(self, text="+", font=("Helvetica", 34, "bold"), command=self.increase_text_size,bg='#1D2364', fg='white', borderless=1, highlightthickness=1, highlightbackground='#1D2364')
        self.increase_button.config(width=50, height=50)
        self.decrease_button = Button(self, text="-", font=("Helvetica", 34, "bold"), command=self.decrease_text_size, bg='#1D2364', fg='white', borderless=1, highlightthickness=0, highlightbackground='#1D2364')
        self.decrease_button.config(width=50, height=50)

        # add edit and back buttons
        self.edit_button = Button(self, text='Edit', command=self.edit, bg='#414BB2', fg='white', highlightbackground="#8E97FF", pady=10, borderless=0)
        self.back_button = Button(self, text='Back', command=self.hide_screen, bg='#414BB2', fg='white', pady=10, borderless=1)

        # SHOW ELEMENTS ON SCREEN
        self.canvas_outer.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.canvas_inner.place(relx=0.57, rely=0.55, anchor=tk.CENTER)
        char_symbol.place(relx=0.25, rely=0.4, anchor=tk.CENTER)
        self.name_label.place(relx=0.25, rely=0.6, anchor=tk.CENTER)
        self.description_title_label.place(relx=0.45, rely=0.25, anchor=tk.CENTER)

        text_size.place(relx=0.93, rely=0.3, anchor=tk.CENTER)
        self.increase_button.place(relx=0.93, rely=0.4, anchor=tk.CENTER)  
        self.decrease_button.place(relx=0.93, rely=0.5, anchor=tk.CENTER)

        self.edit_button.place(relx=0.25, rely=0.8, anchor=tk.CENTER)
        self.back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def show_screen(self, character_name=None, character_description=None):
        # Optional: Update content if new character details are provided
        if character_name and character_description:
            self.name_label.config(text=character_name)
            self.description_text.config(state='normal')
            self.description_text.delete('1.0', tk.END)
            self.description_text.insert('end', character_description)
            self.description_text.config(state='disabled')

        self.pack(fill="both", expand=True)


    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)  # Use 'self.after' instead of 'self.clock_label.after'


    def open_symbol(self):
        image = Image.open("images/character_symbol2.jpg").resize((160, 160), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    
    def hide_screen(self):
        self.controller.show_frame("CharacterScreen")
        self.pack_forget()
        # Optionally, call a method to show the main character list screen


    def increase_text_size(self):
        current_size = self.canvas_inner.itemcget(self.description_text, 'font').split()[1]
        new_size = int(current_size) + 1
        self.canvas_inner.itemconfigure(self.description_text, font=("Helvetica", new_size))

    def decrease_text_size(self):
        current_size = self.canvas_inner.itemcget(self.description_text, 'font').split()[1]
        new_size = int(current_size) - 1 if int(current_size) > 1 else 1
        self.canvas_inner.itemconfigure(self.description_text, font=("Helvetica", new_size))

    def edit(self):
        # edit the description: speech-to-text
        # INSERT CODE HERE
 #       self.character_description = "INSERT SPEECH-TO-TEXT PROMPT HERE"

        # update the database with new description
        conn_characters = sqlite3.connect('Characters.db')
        cursor_characters = conn_characters.cursor()
        cursor_characters.execute("UPDATE Characters SET description=? WHERE name=?", (self.character_description, self.character_name))
        conn_characters.commit()


