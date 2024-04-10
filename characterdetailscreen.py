import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import sqlite3
from tkmacosx import Button
import textwrap
import speech_recognition as sr
from threading import Thread





class CharacterDetailScreen(tk.Frame):
    def __init__(self, parent, controller, character_name, character_description):
        super().__init__(parent, background='#1D2364')
        self.controller = controller
        self.character_name = character_name
        self.character_description = character_description  # Make sure to include this in the arguments
        self.text_entry= ""
        self.recording = False  # Flag to control recording

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

        # Check if character name needs wrapping
        if len(self.character_name) > 18:
            wrapped_name = textwrap.fill(self.character_name, width=18)
        else:
            wrapped_name = self.character_name

        # add text character information
        self.name_label = tk.Label(self, text=wrapped_name, font=("Helvetica", 24, "bold"), fg="white", bg="#8E97FF")
        self.description_title_label = tk.Label(self, text="Description", font=("Helvetica", 24, "bold"), fg="white", bg="#8E97FF")
        # Add text inside the inner rectangle
        self.description_text = self.canvas_inner.create_text(80, 50, text=self.character_description,
                                font=("Helvetica", 18), fill="white", width=400, anchor="nw")

        self.canvas_inner.tag_bind(self.description_text, '<Button-1>', self.enable_editing)


        # Create buttons for adjusting text size
        text_size = tk.Label(self, text="Text size", font=("Helvetica", 24, "bold"), bg='#1D2364', fg='white')
        self.increase_button = Button(self, text="+", font=("Helvetica", 34, "bold"), command=self.increase_text_size,bg='#1D2364', fg='white', borderless=1, highlightthickness=1, highlightbackground='#1D2364')
        self.increase_button.config(width=50, height=50)
        self.decrease_button = Button(self, text="-", font=("Helvetica", 34, "bold"), command=self.decrease_text_size, bg='#1D2364', fg='white', borderless=1, highlightthickness=0, highlightbackground='#1D2364')
        self.decrease_button.config(width=50, height=50)

        # Positioning the "Start Recording" button
        self.start_recording_button = Button(self, text="Start Recording to Edit", command=self.start_recording, font=("Helvetica", 14, "bold"), bg='#2C3488', fg='white', highlightbackground="#414BB2", borderless=0)
        self.start_recording_button.place(relx=0.5, rely=0.5, anchor="center", width=250, height=50)

        # Positioning the "Stop Recording" button, hidden initially
        self.stop_recording_button = Button(self, text="Stop Recording and Save", command=self.stop_recording, font=("Helvetica", 14, "bold"), bg='#2C3488', fg='white', highlightbackground="#414BB2", borderless=0, state='disabled')
        self.stop_recording_button.place(relx=0.5, rely=0.6, anchor="center", width=250, height=50)


        # add edit and back buttons
        # self.edit_button = Button(self, text='Edit', command=self.edit, bg='#414BB2', fg='white', highlightbackground="#8E97FF", pady=10, borderless=0)
        self.delete_button = Button(self, text='Delete', command=self.delete_character, bg='#414BB2', fg='white', highlightbackground="#8E97FF", pady=10, borderless=0)
        self.back_button = Button(self, text='Back', command=self.hide_screen, bg='#414BB2', fg='white', pady=10, borderless=1)
        # self.save_button = Button(self, text='Stop recording and save', command=self.save_edit, bg='#414BB2', fg='white', pady=10, borderless=1)

        # Add a button in your UI setup to call this method
        # self.record_button = Button(self, text="Record Description", command=self.record_and_transcribe, bg="#414BB2", fg="white", pady=10, borderless=1)
        # self.record_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        # SHOW ELEMENTS ON SCREEN
        self.canvas_outer.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.canvas_inner.place(relx=0.57, rely=0.55, anchor=tk.CENTER)
        char_symbol.place(relx=0.25, rely=0.4, anchor=tk.CENTER)
        self.name_label.place(relx=0.25, rely=0.6, anchor=tk.CENTER)
        self.description_title_label.place(relx=0.45, rely=0.25, anchor=tk.CENTER)

        text_size.place(relx=0.93, rely=0.3, anchor=tk.CENTER)
        self.increase_button.place(relx=0.93, rely=0.4, anchor=tk.CENTER)  
        self.decrease_button.place(relx=0.93, rely=0.5, anchor=tk.CENTER)

        # self.edit_button.place(relx=0.3, rely=0.8, anchor=tk.CENTER)
        self.delete_button.place(relx=0.25, rely=0.8, anchor=tk.CENTER)
        self.back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)
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

    def show_screen(self, character_name=None, character_description=None):
        # Optional: Update content if new character details are provided
        if character_name and character_description:
            self.name_label.config(text=character_name)
            self.description_text.config(state='normal')
            self.description_text.delete('1.0', tk.END)
            self.description_text.insert('end', character_description)
            self.description_text.config(state='disabled')

        self.pack(fill="both", expand=True)

    def enable_editing(self, event=None):
        # Get the current description text
        # self.save_button.place(relx=0.5, rely=0.6, anchor=tk.CENTER, width = 300, height = 100)
        # print("check 1")

        # self.record_and_transcribe()

        # current_text = self.canvas_inner.itemcget(self.description_text, 'text')

        # Create an Entry widget at the same place as the text
        # self.text_entry = tk.Entry(self, font=("Helvetica", 18), bg='white', fg='black', width=50)
        # self.text_entry.insert(0, current_text)  # Prefill with current text
        # self.text_entry.bind('<Return>', self.save_edit)  # Bind the Enter key to save the edit
        #
        # # Place the Entry widget on the canvas
        self.text_entry_window = self.canvas_inner.create_window(80, 50, anchor="nw", window=self.text_entry)
        self.text_entry.focus_set()  # Set focus to the entry widget
        self.edit_button.place_forget()

    # Assume CharacterDetailScreen class definition above this code

    def start_recording(self):
        self.recording = True
        self.stop_recording_button['state'] = 'normal'  # Show the stop button
        self.start_recording_button['state'] = 'disabled'  # Disable the start button to prevent re-entry
        # Start recording in a separate thread to prevent UI freezing
        self.recording_thread = Thread(target=self.record_audio)
        self.recording_thread.start()

    def stop_recording(self):
        self.recording = False
        self.stop_recording_button['state'] = 'disabled'  # Hide the stop button
        self.start_recording_button['state'] = 'normal'  # Re-enable the start button

    def record_audio(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio_data = None
            while self.recording:
                try:
                    print("Recording... Speak now")
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    audio_data = audio if not audio_data else recognizer.concatenate(audio_data, audio)
                except sr.WaitTimeoutError:
                    pass  # Continue listening without forcing stop

            if audio_data:
                # Perform transcription after stopping
                try:
                    text = recognizer.recognize_google(audio_data)
                    print(f"Transcribed text: {text}")
                    self.character_description = text
                    self.after(0, self.update_description_text, text)  # Schedule update_description_text to run on the main thread
                    self.edit()
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand the audio")
                    self.after(0, self.update_description_text, "Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
                    self.after(0, self.update_description_text, "Error in transcription")
            else:
                print("No audio recorded")
                self.after(0, self.update_description_text, "No audio recorded")

    def update_description_text(self, text):
        """Updates the description text with the provided text."""
        # Assuming self.canvas_inner and self.description_text are defined in your setup_ui method
        # Update the text item with the new transcription
        self.canvas_inner.itemconfigure(self.description_text, text=text)
        # If you're using a Text widget instead of canvas text, use the following:
        # self.description_text.delete('1.0', tk.END)
        # self.description_text.insert('1.0', text)

    def save_edit(self, event=None):
        return
        # Get the edited text from the Entry widget
        # edited_text = self.text_entry.get()
        # self.character_description = edited_text  # Update the character description

        # # Remove the Entry widget and show the updated text
        # self.canvas_inner.delete(self.text_entry_window)  # Remove the Entry widget from the canvas
        # self.canvas_inner.itemconfigure(self.description_text, text=self.character_description)  # Update the text element with new description

        # Optionally, update the database with the new description here
        # Similar to the existing code in the edit method

        # self.save_button.place_forget()
        # self.edit_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # self.edit()  # Call the existing method to update the database (or modify as needed)

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
        print("saving")
        # edit the description: speech-to-text
        # INSERT CODE HERE
 #       self.character_description = "INSERT SPEECH-TO-TEXT PROMPT HERE"

        # update the database with new description
        conn_characters = sqlite3.connect('Characters.db')
        cursor_characters = conn_characters.cursor()
        cursor_characters.execute("UPDATE Characters SET description=? WHERE name=?", (self.character_description, self.character_name))
        conn_characters.commit()

    # def record_and_transcribe(self):
    #     # Initialize the recognizer
    #     r = sr.Recognizer()
    #     # Start recording
    #     with sr.Microphone() as source:
    #         self.canvas_inner.itemconfigure(self.description_text, text="Listening... Speak now.")
    #         audio = r.listen(source)
    #     # Try to recognize the audio
    #     try:
    #         self.character_description = r.recognize_google(audio)
    #         self.canvas_inner.itemconfigure(self.description_text, text=self.character_description)
    #     except sr.UnknownValueError:
    #         self.canvas_inner.itemconfigure(self.description_text, text="Google Speech Recognition could not understand audio")
    #     except sr.RequestError as e:
    #         self.canvas_inner.itemconfigure(self.description_text, text=f"Could not request results; {e}")

    def delete_character(self):
        # update the database
        conn_characters = sqlite3.connect('Characters.db')
        cursor_characters = conn_characters.cursor()
        cursor_characters.execute("DELETE FROM Characters WHERE name=?", (self.character_name,))
        conn_characters.commit()

        self.hide_screen()
  

