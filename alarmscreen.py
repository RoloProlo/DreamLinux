import tkinter as tk
from tkinter import simpledialog
from tkmacosx import Button
from datetime import datetime, timedelta
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

        self.ready = False

        # check for alarms
        self.check_alarms()

        # UI Elements
        self.setup_ui()


    def check_alarms(self):
        current_time = datetime.now().strftime("%H:%M")

        # Database setup
        self.conn = sqlite3.connect('Alarms.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT alarm_time FROM Alarms WHERE state=?", ('ON',))
        active_alarms = self.cursor.fetchall()
        for self.alarm_time in active_alarms:
            if self.alarm_time[0] == current_time and not self.ready:
                self.alarm_ring()
                print(f"Alarm triggered at {current_time}")
                break

        self.after(10000, self.check_alarms)  # Check alarms every 10 seconds

    def alarm_ring(self):
        # if self.ready:
        #     return
        # INSERT CODE FOR ALARM SOUND
        self.controller.show_frame("AlarmScreen")
        # Clear the window
        for widget in self.winfo_children():
            widget.place_forget()

        # Clock Label
        self.clock_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        self.update_clock()

        # Define buttons 
        self.snooze_button = Button(self, text="Snooze", font=("Helvetica", 28, "bold"), command=self.snooze_click, bg='#414BB2', fg='white', borderless=1)
        self.snooze_button.config(width=220, height=220)
        self.story_button = Button(self, text='Story time', font=("Helvetica", 28, "bold"), command=self.story_time, bg='#414BB2', fg='white', borderless=1)
        self.story_button.config(width=220, height=220)
        
        self.snooze_button.place(relx=0.3, rely=0.5, anchor=tk.CENTER)
        self.story_button.place(relx=0.7, rely=0.5, anchor=tk.CENTER)


    def snooze_click(self):
        # Snooze the alarm for 10 minutes
        snooze_time = (datetime.now() + timedelta(minutes=10)).strftime("%H:%M")
        print("Snooze until: ", snooze_time)
        self.cursor.execute("UPDATE Alarms SET alarm_time=? WHERE alarm_time=?", (snooze_time, self.alarm_time[0]))
        self.conn.commit()
        self.setup_ui()
        self.controller.show_frame("HomeScreen")

    def story_time(self):
        self.controller.show_frame("StoryScreen")
        story_screen = self.controller.get_frame("StoryScreen")
        story_screen.reset_screen()
        self.ready = True

        self.setup_ui()
        # self.controller.show_frame("StoryScreen")

    def setup_ui(self):
        # Clear the window
        for widget in self.winfo_children():
            widget.place_forget()
        # Fetch existing alarms from the database
        self.conn = sqlite3.connect('Alarms.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT alarm_time, state FROM Alarms")
        self.existing_alarms = self.cursor.fetchall()

        # clock label
        self.clock_label = tk.Label(self, font=("Helvetica", 40, "bold"), bg="#1D2364", fg="white")
        self.clock_label.pack(pady=10)
        self.update_clock()

        self.alarm_y = [0.3]
        self.alarm_toggles = {}

        for alarm in self.existing_alarms:
            self.create_alarm_widgets(alarm[0], alarm[1])

        back_button = tkmacosx.Button(self, text="Back to image", command=lambda: self.go_back(), bg='#414BB2',
                                      fg='white', pady=10, borderless=1)

        add_alarm_button = tkmacosx.Button(self, text='Add Alarm', command=self.add_alarm, bg='#8E97FF', fg='white',
                                           pady=10, borderless=1)
        add_alarm_button.pack()

        # SHOW ELEMENTS ON SCREEN
        self.clock_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        add_alarm_button.place(relx=0.8, rely=0.9, anchor=tk.CENTER)
        back_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)


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

            # Insert the alarm into the database
            self.cursor.execute("INSERT INTO Alarms (alarm_time, state) VALUES (?, ?)", (alarm_time, 'ON'))
            self.conn.commit()

            self.exit_alarm()

        # Clear the window
        for widget in self.winfo_children():
            widget.place_forget()

        # Define and show time sliders
        hour_var = tk.IntVar(value=datetime.now().hour)
        minute_var = tk.IntVar(value=datetime.now().minute)

        self.hour_label = tk.Label(self, textvariable=hour_var, fg="white", bg="#1D2364",
                              font=("Helvetica", 64, "bold"))
        self.hour_label.place(relx=0.4, rely=0.4, anchor=tk.CENTER)
        # hour_label.bind("<MouseWheel>", self.scroll)

        self.minute_label = tk.Label(self, textvariable=minute_var, fg="white", bg="#1D2364",
                                font=("Helvetica", 64, "bold"))
        self.minute_label.place(relx=0.61, rely=0.4, anchor=tk.CENTER)
        # minute_label.bind("<MouseWheel>", self.scroll)

        self.colon_label = tk.Label(self, text=":", bg="#1D2364", fg="white", font=("Helvetica", 64, "bold"))
        self.colon_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Create buttons 

        # Create buttons for incrementing and decrementing hour
        self.hour_increment_button = tkmacosx.Button(self, text='+', command=self.increment_hour, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        self.hour_increment_button.config(width=50, height=50)
        self.hour_increment_button.place(relx=0.4, rely=0.55, anchor=tk.CENTER)

        self.hour_decrement_button = tkmacosx.Button(self, text='-', command=self.decrement_hour, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        
        self.hour_decrement_button.config(width=50, height=50)
        self.hour_decrement_button.place(relx=0.4, rely=0.26, anchor=tk.CENTER)

        # Create buttons for incrementing and decrementing minute
        self.minute_increment_button = tkmacosx.Button(self, text='+', command=self.increment_minute, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        self.minute_increment_button.config(width=50, height=50)
        self.minute_increment_button.place(relx=0.61, rely=0.55, anchor=tk.CENTER)

        self.minute_decrement_button = tkmacosx.Button(self, text='-', command=self.decrement_minute, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        self.minute_decrement_button.config(width=50, height=50)
        self.minute_decrement_button.place(relx=0.61, rely=0.26, anchor=tk.CENTER)

        self.set_button = tkmacosx.Button(self, text='Set', command=set_alarm, bg='#414BB2', fg='white', pady=10,
                                     borderless=1)
        self.set_button.place(relx=0.6, rely=0.9, anchor=tk.CENTER)

        self.delete_button = tkmacosx.Button(self, text='Delete', command=self.exit_alarm, bg='#414BB2',
                                        fg='white', pady=10, borderless=1)
        self.delete_button.place(relx=0.4, rely=0.9, anchor=tk.CENTER)


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

    def increment_hour(self):
        hour_var.set((hour_var.get() + 1) % 24)

    def decrement_hour(self):
        hour_var.set((hour_var.get() - 1) % 24)

    def increment_minute(self):
        minute_var.set((minute_var.get() + 1) % 60)

    def decrement_minute(self):
        minute_var.set((minute_var.get() - 1) % 60)


    def on_alarm_click(self, event):
        global alarm_label, alarm_window, hour_var, minute_var, hour_label, minute_label
        alarm_label = event.widget

        # Clear the window
        for widget in self.winfo_children():
            widget.place_forget()

        # Define and show time sliders
        hour_var = tk.IntVar(value=int(alarm_label.cget("text").split(":")[0]))
        minute_var = tk.IntVar(value=int(alarm_label.cget("text").split(":")[1]))

        self.hour_label = tk.Label(self, textvariable=hour_var, fg="white", bg="#1D2364",
                              font=("Helvetica", 44, "bold"))
        self.hour_label.place(relx=0.4, rely=0.4, anchor=tk.CENTER)
        # hour_label.bind("<MouseWheel>", self.scroll)

        self.minute_label = tk.Label(self, textvariable=minute_var, fg="white", bg="#1D2364",
                                font=("Helvetica", 44, "bold"))
        self.minute_label.place(relx=0.61, rely=0.4, anchor=tk.CENTER)
        # minute_label.bind("<MouseWheel>", self.scroll)

        self.colon_label = tk.Label(self, text=":", bg="#1D2364", fg="white", font=("Helvetica", 44, "bold"))
        self.colon_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # Create buttons

        # Create buttons for incrementing and decrementing hour
        self.hour_increment_button = tkmacosx.Button(self, text='+', command=self.increment_hour, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        self.hour_increment_button.config(width=50, height=50)
        self.hour_increment_button.place(relx=0.4, rely=0.55, anchor=tk.CENTER)

        self.hour_decrement_button = tkmacosx.Button(self, text='-', command=self.decrement_hour, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        
        self.hour_decrement_button.config(width=50, height=50)
        self.hour_decrement_button.place(relx=0.4, rely=0.26, anchor=tk.CENTER)

        # Create buttons for incrementing and decrementing minute
        self.minute_increment_button = tkmacosx.Button(self, text='+', command=self.increment_minute, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        self.minute_increment_button.config(width=50, height=50)
        self.minute_increment_button.place(relx=0.61, rely=0.55, anchor=tk.CENTER)

        self.minute_decrement_button = tkmacosx.Button(self, text='-', command=self.decrement_minute, bg='#1D2364', fg='white', highlightthickness=1, highlightbackground='#1D2364',
                                                borderless=1, font=("Helvetica", 34, "bold"))
        self.minute_decrement_button.config(width=50, height=50)
        self.minute_decrement_button.place(relx=0.61, rely=0.26, anchor=tk.CENTER)

        self.set_button = tkmacosx.Button(self, text='Set', command=self.set_alarm, bg='#414BB2', fg='white', pady=10,
                                     borderless=1)
        self.set_button.place(relx=0.6, rely=0.9, anchor=tk.CENTER)

        self.delete_button = tkmacosx.Button(self, text='Delete', command=lambda: self.delete_alarm(alarm_label),
                                        bg='#414BB2', fg='white', pady=10, borderless=1)
        self.delete_button.place(relx=0.4, rely=0.9, anchor=tk.CENTER)

    def set_alarm(self):
        # retrieve the current alarm time
        old_alarm = alarm_label.cget('text')

        alarm_time = f"{hour_var.get():02d}:{minute_var.get():02d}"
        alarm_label.config(text=alarm_time)
        self.alarm_toggles[alarm_label] = alarm_toggle  # Store alarm toggle button associated with the alarm
        alarm_label.bind("<Button-1>", self.on_alarm_click)

        # update the alarm with the new set time
        self.conn = sqlite3.connect('Alarms.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("UPDATE Alarms SET alarm_time=? WHERE alarm_time=?", (alarm_time, old_alarm))
        self.conn.commit()

        self.exit_alarm()


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

        # Shift up the remaining alarms below the deleted one
        for label, toggle in list(self.alarm_toggles.items()):
            rely = label.place_info().get('rely')
            if rely and float(rely) > float(deleted_y):
                new_y = float(rely) - 0.1
                label.place_configure(rely=new_y)
                toggle.place_configure(rely=new_y)

        # Remove the last entry from alarm_y list
        self.alarm_y.pop()

        self.exit_alarm()

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

    def exit_alarm(self):
        self.hour_label.destroy()
        self.minute_label.destroy()
        self.colon_label.destroy()
        self.hour_increment_button.destroy()
        self.hour_decrement_button.destroy()
        self.minute_increment_button.destroy()
        self.minute_decrement_button.destroy()
        self.set_button.destroy()
        self.delete_button.destroy()
        # Rebuild the interface as needed
        # self.controller.show_frame("AlarmScreen")
        self.setup_ui()

    def go_back(self):
        self.controller.show_frame("HomeScreen")
        self.conn.close()  # Close the database connection when leaving this screen

    def __del__(self):
        self.conn.close()
