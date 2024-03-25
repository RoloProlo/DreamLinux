import tkinter as tk
from tkinter import ttk
from tkmacosx import Button
from PIL import ImageTk, Image
import subprocess
from datetime import datetime, date
import sqlite3

# Create the SQLite database for dream images
conn = sqlite3.connect('DreamImages.db')
cursor = conn.cursor()

# Create the DreamImages table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS DreamImages (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    image TEXT,  -- Store path or URL of the image
                    description TEXT,
                    meaning TEXT,
                    characters TEXT
                  )''')
conn.commit()


# Create the SQLite database for characters
conn_characters = sqlite3.connect('Characters.db')
cursor_characters = conn_characters.cursor()

# Create the Characters table if it doesn't exist
cursor_characters.execute('''CREATE TABLE IF NOT EXISTS Characters (
                            id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE,
                            age INTEGER,
                            description TEXT
                          )''')
conn_characters.commit()


# Create the SQLite database for characters in dream
conn_dreamcast = sqlite3.connect('DreamCast.db')
cursor_dreamcast = conn_dreamcast.cursor()

# Create the DreamCast table if it doesn't exist
cursor_dreamcast.execute('''CREATE TABLE IF NOT EXISTS DreamCast (
                            id INTEGER PRIMARY KEY,
                            dream_image_id INTEGER,  -- Foreign key to link with DreamImages table
                            character TEXT,
                            FOREIGN KEY (dream_image_id) REFERENCES DreamImages(id),
                            FOREIGN KEY (character) REFERENCES Characters(name)
                          )''')
conn_dreamcast.commit()


# Create the SQLite database for alarms
conn_alarms = sqlite3.connect('Alarms.db')
cursor_alarms = conn_alarms.cursor()

# Create the Alarms table if it doesn't exist
cursor_alarms.execute('''CREATE TABLE IF NOT EXISTS Alarms (
                    id INTEGER PRIMARY KEY,
                    alarm_time TEXT,
                    state TEXT
                  )''')
conn_alarms.commit()


# Close the connection to the databases when done
conn.close()
conn_characters.close()
conn_dreamcast.close()
conn_alarms.close()
