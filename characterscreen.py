import tkinter as tk
from PIL import Image, ImageTk

class CharacterScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # Set the controller attribute
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="This is the Character Screen")
        label.pack(pady=10, padx=10)

        back_button = tk.Button(self, text="Go Back", command=lambda: controller.show_frame("HomeScreen"))
        back_button.pack()
