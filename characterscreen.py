import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import sqlite3
from tkmacosx import Button
from characterdetailscreen import CharacterDetailScreen

class CharacterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(background='#1D2364')
        #self.character_details = CharacterDetailScreen  # Placeholder for the character details screen


        # Clock Label
        self.clock_label = tk.Label(self, font=("Helvetica", 44, "bold"), bg="#1D2364", fg="white")
        self.clock_label.pack(pady=10, padx=10)
        self.update_clock()

        # Database connection
        self.conn = sqlite3.connect('DreamImages.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT * FROM DreamImages LIMIT 1 OFFSET 0")
        self.dream_image_data = self.cursor.fetchone()

        # Date Label
        self.date_label = tk.Label(self, text=self.dream_image_data[1] if self.dream_image_data else "No Date", font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white", relief="flat")
        self.date_label.pack(pady=(0, 20))

        # Canvas for characters
        self.canvas = tk.Canvas(self, bg="#1D2364", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.initialize_characters()

        # Load characters if any
        if self.dream_image_data:
            self.display(self.dream_image_data[5].split(', ') if self.dream_image_data[5] else [])

        self.setup_character_view()


        # Buttons
        self.see_all_button = Button(self, text="See all characters", command=self.see_all, pady=10, bg='#8E97FF', fg='white', borderless=1)
        self.back_button = Button(self, text='Back to image', command=lambda: self.controller.show_frame("HomeScreen"), bg='#414BB2', fg='white', pady=10, borderless=1)
        self.see_all_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.back_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def initialize_characters(self):
        # Assuming you have a table "Characters" with a column "name" for character names
        self.conn_characters = sqlite3.connect('Characters.db')
        self.cursor_characters = self.conn_characters.cursor()
        self.cursor_characters.execute("SELECT name FROM Characters")
        self.characters = self.cursor_characters.fetchall()  # This will be a list of tuples

        # Close the connection if not needed further or keep it open if you'll need it later
        # self.conn_characters.close()

    def display(self, characters):
        self.canvas.delete("all")  # Clear existing characters
        symbol = self.open_symbol()

        # Store references to canvas items if needed for interaction or later updates
        self.canvas_items = []

        x_offset, y_offset = 30, 10
        for name in characters:
            char_image = self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=symbol)
            char_name = self.canvas.create_text(x_offset + 80, y_offset + 170, text=name, font=("Helvetica", 24, "bold"), fill="white")

            # Example of binding a click event to each character image
            self.canvas.tag_bind(char_image, '<Button-1>', lambda e, name=name: self.on_character_click(name))

            # Store references if you need to interact with these items later
            self.canvas_items.append((char_image, char_name))

            x_offset += 200
            if x_offset > 750:
                x_offset = 30
                y_offset += 200

        # Ensure the symbol image is retained by storing it in an attribute
        self.symbol_image = symbol

    def setup_character_view(self):
        # Create a frame for the characters list
        self.characters_frame = tk.Frame(self, bg="#1D2364")
        self.characters_frame.pack(fill="both", expand=True, side="bottom")

        # Scrollbar
        self.char_scrollbar = tk.Scrollbar(self.characters_frame)
        self.char_scrollbar.pack(side="right", fill="y")

        # Listbox for characters
        self.char_listbox = tk.Listbox(self.characters_frame, yscrollcommand=self.char_scrollbar.set, width=50, bg="#1D2364", fg="white")
        self.char_scrollbar.config(command=self.char_listbox.yview)

        self.char_listbox.pack(side="left", fill="both", expand=True)

        # Initially hide the frame
        self.characters_frame.pack_forget()

        close_button = Button(self.characters_frame, text="Close", command=lambda: self.characters_frame.pack_forget(), bg='#414BB2', fg='white')
        close_button.pack()

    def open_symbol(self):
        image = Image.open("images/character_symbol.jpg").resize((160, 160), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)

    def update_clock(self):
        self.clock_label.config(text=datetime.now().strftime("%H:%M"))
        self.clock_label.after(1000, self.update_clock)

    # Assuming this method is within CharacterScreen class
    def on_character_click(self, name):
        # Example of fetching character description
        self.cursor_characters.execute("SELECT description FROM Characters WHERE name=?", (name,))
        row = self.cursor_characters.fetchone()
        if row:
            description = row[0] or "No description available"  # Ensure description is not None
            if not isinstance(description, str):
                description = str(description)  # Convert description to string if necessary

            # Assuming CharacterDetailScreen is properly imported and accessible
            if hasattr(self, 'character_details') and self.character_details:
                self.character_details.hide_screen()  # Hide existing detail screen if it exists

            self.character_details = CharacterDetailScreen(self, self.controller, name, description)
            self.character_details.show_screen()
        else:
            print(f"No description found for character: {name}")

    def see_all(self):
        # Clear existing entries
        self.char_listbox.delete(0, tk.END)

        # Populate the listbox with character names
        for name_tuple in self.characters:
            self.char_listbox.insert(tk.END, name_tuple[0])

        # Show the characters frame
        self.characters_frame.pack(fill="both", expand=True, side="bottom")

    def go_back(self):
        self.controller.show_frame("HomeScreen")
        self.conn.close()
