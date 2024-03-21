import tkinter as tk
from tkinter import ttk
from tkmacosx import Button
from PIL import ImageTk, Image
import subprocess
from datetime import datetime
 
## CURRENTLY NOT USED

root = tk.Tk()

# Open window having dimension 
root.geometry('1000x500')   

# set background colour of screen
root.configure(background='#1D2364')

#resize image
def resize_image(path):
    image = Image.open(path)
    # Resize the image
    image = image.resize((1000, 500), Image.ANTIALIAS)

    # Convert the Image object into a Tkinter-compatible photo image
    photo = ImageTk.PhotoImage(image)

    return photo

photo = resize_image("images/dream_image_flying.jpeg")

dream_image = tk.Label(image=photo, borderwidth=0)
dream_image.image = photo  # Keep a reference to the image to prevent it from being garbage collected

dream_image.place(x=0, y=0, relwidth=1, relheight=1) 

quit_button = Button(root, text='<->', command=root.quit, bg='#8E97FF', fg='white', pady=5, borderless=1)
quit_button.place(relx=1, rely=0, anchor='ne') 



root.mainloop()