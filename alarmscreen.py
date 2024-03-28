import tkinter as tk
from tkinter import simpledialog
from tkmacosx import Button
from datetime import datetime
import sqlite3
import tkmacosx
import subprocess
from storyscreen import StoryScreen


class AlarmScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(background='#1D2364')  # Set a background color

        # Database setup
        self.conn = sqlite3.connect('Alarms.db')
        self.cursor = self.conn.cursor()

        # Fetch existing alarms from the database
        self.cursor.execute("SELECT alarm_time, state FROM Alarms")
        self.existing_alarms = self.cursor.fetchall()


        self.alarm_y = [0.3]
        self.alarm_toggles = {}


        # UI Elements
        self.setup_ui()

        for alarm in self.existing_alarms:
            self.create_alarm_widgets(alarm[0], alarm[1])

        # Start the check for alarms

        # self.display_alarms()

    def check_alarms(self):
        current_time = datetime.now().strftime("%H:%M")
        self.cursor.execute("SELECT alarm_time FROM Alarms WHERE state=?", ('ON',))
        active_alarms = self.cursor.fetchall()
        for alarm_time in active_alarms:
            if alarm_time[0] == current_time:
                print(f"Alarm triggered at {current_time}")
                self.controller.show_frame("StoryScreen")
        self.after(30000, self.check_alarms)  # Check alarms every 30 seconds

    def setup_ui(self):
        self.clock_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.clock_label.pack(pady=10)
        self.update_clock()

        back_button = tkmacosx.Button(self, text="Go Back", command=lambda: self.controller.show_frame("HomeScreen"), bg='#414BB2',
                                      fg='white', pady=5, borderless=1)

        add_alarm_button = tkmacosx.Button(self, text='Add Alarm', command=self.add_alarm, bg='#8E97FF', fg='white',
                                           pady=5, borderless=1)
        add_alarm_button.pack()

        self.back_button = Button(self, text='Go Back', command=self.controller.show_frame("HomeScreen"), bg='#414BB2', fg='white', pady=10, borderless=1)

        # SHOW ELEMENTS ON SCREEN
        self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        add_alarm_button.place(relx=0.8, rely=0.9, anchor=tk.CENTER)
        back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # self.display_alarms()

    def create_alarm_widgets(self, alarm_time, state):
        global alarm_toggle
        # Create a new label for the alarm
        alarm_label = tk.Label(self, text=alarm_time, font=("Helvetica", 44, "bold"), bg="#1D2364", fg="white")
        alarm_label.place(relx=0.2, rely=self.alarm_y[-1], anchor=tk.CENTER)
        alarm_label.bind("<Button-1>", self.on_alarm_click)

        # Create a new toggle button for the alarm
        if state == "ON":
            alarm_toggle = Button(self, text=state, bg='#8E97FF', fg='white', pady=5, borderless=1, command=lambda: self.toggle_alarm(alarm_label))
        else:
            alarm_toggle = Button(self, text=state, bg='#C6C7CC', fg='white', pady=5, borderless=1, command=lambda: self.toggle_alarm(alarm_label))

        alarm_toggle.place(relx=0.8, rely=self.alarm_y[-1], anchor=tk.CENTER)
        self.alarm_toggles[alarm_label] = alarm_toggle  # Store alarm toggle button associated with the alarm

        # Increment the alarm_y for the next alarm
        self.alarm_y.append(self.alarm_y[-1] + 0.1)

    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M")
        self.clock_label.config(text=current_time)
        self.after(1000, self.update_clock)  # Update every 1000 milliseconds (1 second)

    def add_alarm(self):
        global hour_label, minute_label, hour_var, minute_var
        # Check if alarm_y is empty and initialize with a starting y-coordinate if necessary
        if not self.alarm_y:
            self.alarm_y = [0.2]

        def set_alarm():
            global alarm_toggle
            alarm_time = f"{hour_var.get():02d}:{minute_var.get():02d}"
            alarm_label = tk.Label(self, text=alarm_time, font=("Helvetica", 44, "bold"), bg="#1D2364", fg="white")
            alarm_label.place(relx=0.2, rely=self.alarm_y[-1], anchor=tk.CENTER)
            alarm_label.bind("<Button-1>", self.on_alarm_click)

            alarm_toggle = tkmacosx.Button(self, text='ON', bg='#8E97FF', fg='white', pady=5, borderless=1,
                                           command=lambda: self.toggle_alarm(self, alarm_label))
            alarm_toggle.place(relx=0.8, rely=self.alarm_y[-1], anchor=tk.CENTER)
            self.alarm_toggles[alarm_label] = alarm_toggle  # Store alarm toggle button associated with the alarm

            self.alarm_y.append(self.alarm_y[-1] + 0.1)  # Increment the alarm_y for the next alarm
            alarm_window.destroy()

            # Insert the alarm into the database
            self.cursor.execute("INSERT INTO Alarms (alarm_time, state) VALUES (?, ?)", (alarm_time, 'ON'))
            self.conn.commit()

        # Open new toplevel window to set alarm
        alarm_window = tk.Toplevel(self)
        alarm_window.title("Set Alarm")
        alarm_window.geometry("500x500")
        alarm_window.configure(background='#1D2364')

        # Define and show time sliders
        hour_var = tk.IntVar(value=datetime.now().hour)
        minute_var = tk.IntVar(value=datetime.now().minute)

        hour_label = tk.Label(alarm_window, textvariable=hour_var, fg="white", bg="#1D2364",
                              font=("Helvetica", 44, "bold"))
        hour_label.place(relx=0.4, rely=0.4, anchor=tk.CENTER)
        hour_label.bind("<MouseWheel>", self.scroll)

        minute_label = tk.Label(alarm_window, textvariable=minute_var, fg="white", bg="#1D2364",
                                font=("Helvetica", 44, "bold"))
        minute_label.place(relx=0.61, rely=0.4, anchor=tk.CENTER)
        minute_label.bind("<MouseWheel>", self.scroll)

        colon_label = tk.Label(alarm_window, text=":", bg="#1D2364", fg="white", font=("Helvetica", 44, "bold"))
        colon_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        set_button = tkmacosx.Button(alarm_window, text='Set', command=set_alarm, bg='#414BB2', fg='white', pady=5,
                                     borderless=1)
        set_button.place(relx=0.6, rely=0.9, anchor=tk.CENTER)

        delete_button = tkmacosx.Button(alarm_window, text='Delete', command=alarm_window.destroy, bg='#414BB2',
                                        fg='white', pady=5, borderless=1)
        delete_button.place(relx=0.3, rely=0.9, anchor=tk.CENTER)


    def scroll(self, event):
        global hour_label, minute_label, hour_var, minute_var
        if event.delta > 0:  # Scroll up
            if event.widget == hour_label:
                hour_var.set((hour_var.get() + 1) % 24)
            elif event.widget == minute_label:
                minute_var.set((minute_var.get() + 1) % 60)

        else:  # Scroll down
            if event.widget == hour_label:
                hour_var.set((hour_var.get() - 1) % 24)
            elif event.widget == minute_label:
                minute_var.set((minute_var.get() - 1) % 60)


    def on_alarm_click(self, event):
        global alarm_label, alarm_window, hour_var, minute_var, hour_label, minute_label
        alarm_label = event.widget
        alarm_window = tk.Toplevel(self)
        alarm_window.title("Set Alarm")
        alarm_window.geometry("400x400")
        alarm_window.configure(background='#1D2364')

        # Define and show time sliders
        hour_var = tk.IntVar(value=int(alarm_label.cget("text").split(":")[0]))
        minute_var = tk.IntVar(value=int(alarm_label.cget("text").split(":")[1]))

        hour_label = tk.Label(alarm_window, textvariable=hour_var, fg="white", bg="#1D2364",
                              font=("Helvetica", 44, "bold"))
        hour_label.place(relx=0.4, rely=0.4, anchor=tk.CENTER)
        hour_label.bind("<MouseWheel>", self.scroll)

        minute_label = tk.Label(alarm_window, textvariable=minute_var, fg="white", bg="#1D2364",
                                font=("Helvetica", 44, "bold"))
        minute_label.place(relx=0.61, rely=0.4, anchor=tk.CENTER)
        minute_label.bind("<MouseWheel>", self.scroll)

        colon_label = tk.Label(alarm_window, text=":", bg="#1D2364", fg="white", font=("Helvetica", 44, "bold"))
        colon_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        set_button = tkmacosx.Button(alarm_window, text='Set', command=self.set_alarm, bg='#414BB2', fg='white', pady=5,
                                     borderless=1)
        set_button.place(relx=0.6, rely=0.9, anchor=tk.CENTER)

        delete_button = tkmacosx.Button(alarm_window, text='Delete', command=lambda: self.delete_alarm(alarm_label),
                                        bg='#414BB2', fg='white', pady=5, borderless=1)
        delete_button.place(relx=0.3, rely=0.9, anchor=tk.CENTER)

    def set_alarm(self):
        # retrieve the current alarm time
        old_alarm = alarm_label.cget('text')

        alarm_time = f"{hour_var.get():02d}:{minute_var.get():02d}"
        alarm_label.config(text=alarm_time)
        self.alarm_toggles[alarm_label] = alarm_toggle  # Store alarm toggle button associated with the alarm
        alarm_window.destroy()
        alarm_label.bind("<Button-1>", self.on_alarm_click)

        # update the alarm with the new set time
        self.cursor.execute("UPDATE Alarms SET alarm_time=? WHERE alarm_time=?", (alarm_time, old_alarm))
        self.conn.commit()


    def delete_alarm(self, alarm_label):
        global alarm_toggles, alarm_y
        # Get the current y-coordinate of the alarm label being deleted
        deleted_y = alarm_label.place_info().get('rely')

        # Remove the alarm from the database
        alarm_time = alarm_label.cget('text')
        self.cursor.execute("DELETE FROM Alarms WHERE alarm_time=?", (alarm_time,))
        self.conn.commit()

        # Destroy the alarm label and its associated toggle button
        self.alarm_toggles[alarm_label].destroy()  # Delete corresponding alarm toggle button
        alarm_label.destroy()
        del self.alarm_toggles[alarm_label]
        alarm_window.destroy()

        # Shift up the remaining alarms below the deleted one
        for label, toggle in list(self.alarm_toggles.items()):
            rely = label.place_info().get('rely')
            if rely and float(rely) > float(deleted_y):
                new_y = float(rely) - 0.1
                label.place_configure(rely=new_y)
                toggle.place_configure(rely=new_y)

        # Remove the last entry from alarm_y list
        self.alarm_y.pop()

    def toggle_alarm(self, alarm_label):
        global alarm_toggles
        if self.alarm_toggles[alarm_label].cget("text") == "ON":
            self.alarm_toggles[alarm_label].config(text="OFF",
                                                   bg="#FF5733")  # Change text and color to indicate OFF state
            state = 'OFF'
        else:
            self.alarm_toggles[alarm_label].config(text="ON",
                                                   bg='#414BB2')  # Change text and color to indicate ON state
            state = 'ON'

        # Update the state in the database
        alarm_time = alarm_label.cget('text')
        self.cursor.execute("UPDATE Alarms SET state=? WHERE alarm_time=?", (state, alarm_time))
        self.conn.commit()

    def go_back(self):
        self.controller.show_frame("HomeScreen")
        self.conn.close()  # Close the database connection when leaving this screen

    def __del__(self):
        self.conn.close()
