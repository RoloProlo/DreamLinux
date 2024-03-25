import tkinter as tk
from tkinter import ttk
from tkmacosx import Button
from datetime import datetime
import sqlite3


class DescriptionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.clock_label = tk.Label(self, font=("Helvetica", 44, "bold"), bg="#1D2364", fg="white")
        self.text_widget_height = 350  # Adjust this value as needed
        self.controller = controller
        self.configure(background='#1D2364')
        self.current_image_index = 0

        # Connect to the SQLite database for dream images
        self.conn = sqlite3.connect('DreamImages.db')
        self.cursor = self.conn.cursor()
        self.text_widget = tk.Text

        # Retrieve index of dream image displayed on the homescreen
        current_index = 0
        # Access the data of the current dream image in the DreamImages database
        self.cursor.execute("SELECT * FROM DreamImages LIMIT 1 OFFSET ?", (current_index,))
        self.dream_image_data = self.cursor.fetchone()

        # Assuming the description is stored in the third column (index 2)
        self.description = self.dream_image_data[3]

        self.setup_ui()

    def setup_ui(self):
        self.clock_label.pack(pady=10, padx=10)
        self.update_clock()

        canvas = tk.Canvas(self, width=850, height=450, borderwidth=0, highlightthickness=0, bg="#1D2364")
        x1, y1, x2, y2, r = 50, 30, 800, 450, 150
        points = (x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2, x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1)
        canvas.create_polygon(points, fill="#8E97FF", smooth=True)

        # Add a text widget inside the canvas
        self.text_widget = tk.Text(canvas, font=("Helvetica", 18), bg="#8E97FF", fg="white", bd=1, wrap="word")
        self.text_widget.insert(tk.END, self.description)
        self.text_widget.config(state=tk.DISABLED)

        # Create a scrollbar
        scrollbar = ttk.Scrollbar(canvas, orient="vertical", command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Place the scrollbar and text widget inside the canvas
        self.text_widget.config(height=self.text_widget_height, highlightbackground="#8E97FF", highlightthickness=0)
        canvas.create_window(80, 60, window=self.text_widget, anchor="nw", width=650, height=self.text_widget_height)
        canvas.create_window(750, 60, window=scrollbar, anchor="nw", width=20, height=350)

        # date of dream image (Assuming the date is stored in the first column)
        date = self.dream_image_data[1]
        date = tk.Label(self, text=date, font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white", relief="flat", anchor="n")

        # add button to go back
        back_button = tk.Button(self, text="Go Back", command=lambda: self.controller.show_frame("HomeScreen"))

        # Create buttons for adjusting text size
        text_size = tk.Label(self, text="Text size", font=("Helvetica", 24, "bold"), bg='#1D2364', fg='white')
        increase_button = Button(self, text="+", font=("Helvetica", 34, "bold"), command=lambda: self.increase_text_size(), bg='#1D2364', fg='white', borderless=1, highlightthickness=1, highlightbackground='#1D2364')
        increase_button.config(width=50, height=50)

        decrease_button = Button(self, text="-", font=("Helvetica", 34, "bold"), command=lambda: self.decrease_text_size(), bg='#1D2364', fg='white', borderless=1, highlightthickness=0, highlightbackground='#1D2364')
        decrease_button.config(width=50, height=50)

        # SHOW ELEMENTS ON SCREEN
        date.place(relx=0.5, rely=0.12, anchor=tk.CENTER)
        canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

        text_size.place(relx=0.93, rely=0.3, anchor=tk.CENTER)
        increase_button.place(relx=0.93, rely=0.4, anchor=tk.CENTER)
        decrease_button.place(relx=0.93, rely=0.5, anchor=tk.CENTER)

        back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)  # Use 'self.after' instead of 'self.clock_label.after'

    def increase_text_size(self):
        current_size = int(self.text_widget['font'].split()[1])
        self.text_widget.config(font=("Helvetica", current_size + 1))

    def decrease_text_size(self):
        current_size = int(self.text_widget['font'].split()[1])
        if current_size > 1:
            self.text_widget.config(font=("Helvetica", current_size - 1))

    def go_back(self):
        self.controller.show_frame("HomeScreen")
        self.conn.close()  # Close the database connection when leaving this screen
