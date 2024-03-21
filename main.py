import tkinter as tk
from homescreen import HomeScreen


class MainApplication(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('1024x600')  # Set window size
        self.frames = {}

        self.attributes('-fullscreen', True)  # Set the application to fullscreen
        self.bind("<Escape>", self.toggle_fullscreen)  # Bind the Escape key to toggle fullscreen

        # Provide frames as a tuple
        for F in (HomeScreen,):
            frame = F(parent=self, controller=self)
            self.frames[F.__name__] = frame
            frame.place(x=0, y=0, width=1024, height=600)

        self.show_frame("HomeScreen")

    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()

    def toggle_fullscreen(self, event=None):
        fullscreen = self.attributes('-fullscreen')
        self.attributes('-fullscreen', not fullscreen)


if __name__ == "__main__":
    try:
        app = MainApplication()
        app.mainloop()
    except Exception as e:
        print(e)
