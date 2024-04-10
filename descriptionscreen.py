import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from tkmacosx import Button
from datetime import datetime
import sqlite3


class DescriptionScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.clock_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.text_widget_height = 350  # Adjust this value as needed
        self.controller = controller
        self.configure(background='#1D2364')
        self.current_image_index = 0
        self.description = "" # Initialize description as an empty string
        self.date = ""

        self.text_widget = tk.Text

        self.setup_ui()


    def setup_ui(self):
        self.display_current_description()
        print("Description that is now stored: \n", self.description)
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
        date = tk.Label(self, text=self.date, font=("Helvetica", 24, "bold"), bg="#1D2364", fg="white", relief="flat", anchor="n")

        # add button to go back
        self.back_button = self.create_icon_only_button(self, "Icons/home.png", "Icons/home_press.png", self.go_back)

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

        self.back_button.place(relx=0.5, y=560, anchor=tk.CENTER)
        # self.after(100, self.display_current_description)  # Delay added to ensure current index is fetched after the screen is fully initialized

    def create_icon_only_button(self, parent, icon_path, pressed_icon_path, command):
        # Load the normal icon
        new_icon_size = (60, 60)  # Adjust the size as needed

        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image.resize(new_icon_size, Image.Resampling.LANCZOS))

        # Load the pressed icon
        pressed_icon_image = Image.open(pressed_icon_path)
        pressed_icon_photo = ImageTk.PhotoImage(pressed_icon_image.resize(new_icon_size, Image.Resampling.LANCZOS))

        # Use parent's background color for a seamless look
        parent_bg = parent.cget('bg')

        # Create the button frame
        button_frame_outer = tk.Frame(parent, bg=parent_bg, bd=0, highlightthickness=0)
        button_frame = tk.Frame(button_frame_outer, bg=parent_bg, bd=0, highlightthickness=0, width=70, height=70)
        button_frame.pack_propagate(False)
        button_frame.pack()

        # Create the icon label centered in the frame
        icon_label = tk.Label(button_frame, image=icon_photo, bg=parent_bg)
        icon_label.image = icon_photo  # Keep a reference to avoid garbage collection
        icon_label.pack(expand=True)

        # Function to swap to the pressed icon
        def on_press(event):
            icon_label.config(image=pressed_icon_photo)
            icon_label.image = pressed_icon_photo

        # Function to swap back to the normal icon and execute the command when released
        def on_release(event):
            icon_label.config(image=icon_photo)
            icon_label.image = icon_photo
            command()

        # Bind the press and release events
        button_frame_outer.bind("<ButtonPress-1>", on_press)
        button_frame_outer.bind("<ButtonRelease-1>", on_release)
        icon_label.bind("<ButtonPress-1>", on_press)
        icon_label.bind("<ButtonRelease-1>", on_release)


        return button_frame_outer
    def display_current_description(self):
        current_image_index = self.controller.get_shared_data("current_image_index")
        current_id = self.controller.get_shared_data("current_id")
        print(current_id)
        conn = sqlite3.connect('DreamImages.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DreamImages WHERE id=?", (current_id,))
        row = cursor.fetchone()

        if row:
            self.date = row[1] # Assuming the date is in the 2nd column
            self.description = row[3]  # Assuming the description is in the 4th column
        else:
            self.description = "Description not available"
        conn.close()

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
        # self.conn.close()  # Close the database connection when leaving this screen
