import tkinter as tk
import sqlite3

class DB:
    def __del__(self):
        self.conn.close()

    def __init__(self):
        self.conn = sqlite3.connect('DreamImages.db')
        self.conn_characters = sqlite3.connect('Characters.db')

    def open_dream_data(self, index):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM DreamImages ORDER BY date DESC LIMIT 1 OFFSET ?", (index,))
        dream_data = cursor.fetchone()
        # print(dream_data)
        cursor.close()

        return dream_data

    def open_character_data(self):
        cursor_characters = self.conn_characters.cursor()
        cursor_characters.execute("SELECT * FROM Characters")
        character_data = cursor_characters.fetchall()
        # print(character_data)
        cursor_characters.close()

        return character_data