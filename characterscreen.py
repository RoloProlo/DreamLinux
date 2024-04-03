import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import sqlite3
from tkmacosx import Button
from characterdetailscreen import CharacterDetailScreen
from database import DB

class CharacterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(background='#1D2364')
        #self.character_details = CharacterDetailScreen  # Placeholder for the character details screen
        self.current_image_index = 0
        self.date = ""
        self.character_names = ""

        # date of dream image
        self.date_label = tk.Label(self, text=self.date, font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white", relief="flat", anchor="n")
        self.date_label.place(relx=0.5, rely=0.12, anchor=tk.CENTER)

        self.setup_ui()

    def setup_ui(self):
        # Clock Label
        self.clock_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.clock_label.pack(pady=10, padx=10)
        self.update_clock()

        # date of dream image (Assuming the date is stored in the first column)
        date = tk.Label(self, text=self.date, font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white", relief="flat", anchor="n")

        # Create canvas for characters
        self.canvas = tk.Canvas(self, bg="#1D2364", highlightbackground="#1D2364", borderwidth=1, highlightthickness=0)
        self.canvas.place(x=100, y=100, width=850, height=430)

        self.display_characters()
        
        # self.setup_character_view()

        # Buttons
        self.see_all_button = Button(self, text="See all characters", command=self.see_all, pady=10, bg='#8E97FF', fg='white', borderless=1)
        self.back_button = Button(self, text='Back to image', command=lambda: self.controller.show_frame("HomeScreen"), bg='#414BB2', fg='white', pady=10, borderless=1)
       
       # SHOW ELEMENTS ON SCREEN
        self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        self.see_all_button.place(relx=0.7, rely=0.95, anchor=tk.CENTER)
        self.back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)


    def display_characters(self):
        # self.canvas.delete("all")  # Clear existing characters

        current_image_index = self.controller.get_shared_data("current_image_index")
        current_id = self.controller.get_shared_data("current_id")
        print(current_id)
        conn = sqlite3.connect('DreamImages.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DreamImages WHERE id=?", (current_id,))
        row = cursor.fetchone()

         # Store references to canvas items if needed for interaction or later updates
        self.canvas_items = []

        # Get the character names and date associated with this DreamImage
        self.character_names = row[5].split(', ') if row else []
        self.date = row[1] if row else []
        print("names: ", self.character_names)

        # Update the date label
        self.date_label.config(text=self.date)

        # check if there are any characters associated with current dream
        if not self.character_names[0] == "":
            symbol = self.open_symbol()

            x_offset, y_offset = 30, 10  # initial x and y offset for the first picture
            for name in self.character_names:
                # Load picture onto the canvas
                char_image = self.canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=symbol)
                # Add name text underneath the picture
                char_name = self.canvas.create_text(x_offset + 80, y_offset + 170, text=name, font=("Helvetica", 24, "bold"), fill="white")

                # Example of binding a click event to each character image
                self.canvas.tag_bind(char_image, '<Button-1>', lambda e, name=name: self.on_character_click(name))
                # Associate text item with image item
                self.canvas.addtag_withtag(f'{char_image}_text', char_name)

                # Store references if you need to interact with these items later
                self.canvas_items.append((char_image, char_name))

                # Update x and y_offset for the next picture
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
        current_time = datetime.now().strftime("%H:%M")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)  # Use 'self.after' instead of 'self.clock_label.after'


    # Assuming this method is within CharacterScreen class
    def on_character_click(self, name):
        # Example of fetching character description
        self.conn_characters = sqlite3.connect('Characters.db')
        self.cursor_characters = self.conn_characters.cursor()
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
        for name_tuple in self.character_names:
            self.char_listbox.insert(tk.END, name_tuple[0])

        # Show the characters frame
        self.characters_frame.pack(fill="both", expand=True, side="bottom")

    def go_back(self):
        self.controller.show_frame("HomeScreen")
        self.conn.close()
