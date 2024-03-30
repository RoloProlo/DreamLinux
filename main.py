import tkinter as tk
from homescreen import HomeScreen
# Import additional screens
from descriptionscreen import DescriptionScreen
from alarmscreen import AlarmScreen
from meaningscreen import MeaningScreen
from characterscreen import CharacterScreen
from storyscreen import StoryScreen
from generationscreen import GenerationScreen

#from characterdetailscreen import CharacterDetailScreen

class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('1024x600')  # Set window size
        self.frames = {}
        self.current_image_index = 0  # Initialize the attribute here
        self.attributes('-fullscreen', True)  # Set the application to fullscreen
        self.bind("<Escape>", self.toggle_fullscreen)  # Bind the Escape key to toggle fullscreen

        # Provide frames as a tuple
        for F in (HomeScreen, DescriptionScreen, AlarmScreen, MeaningScreen, CharacterScreen, StoryScreen, GenerationScreen):
            frame = F(parent=self, controller=self)  # Note the 'controller=self' part
            self.frames[F.__name__] = frame
            frame.place(x=0, y=0, width=1024, height=600)

        self.show_frame("HomeScreen")

    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()

    def get_frame(self, frame_name):
        print("Available frames:", self.frames.keys())
        frame = self.frames.get(frame_name)
        if frame is None:
            print(f"Frame not found: {frame_name}")
        return frame

    def toggle_fullscreen(self, event=None):
        fullscreen = self.attributes('-fullscreen')
        self.attributes('-fullscreen', not fullscreen)


if __name__ == "__main__":
    try:
        app = MainApplication()
        app.mainloop()
    except Exception as e:
        print(e)
