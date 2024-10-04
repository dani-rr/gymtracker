import tkinter as tk
from tkinter import font
import time
import threading
from evdev import InputDevice, categorize, ecodes
from lib.libhelper.db import *

class TimerForm:
    def __init__(self, user, training):

        self.user = user
        self.training = training
        # Initialize window, define geometry, and hide title bar
        self.window = tk.Tk()
        self.window.geometry("960x320")

        self.principal_font = font.Font(family="Digital-7 Mono", size=100)
        self.small_font = font.Font(family="Digital-7 Mono", size=30)

        self.idle_timer_seconds = 0
        self.idle_timer_id = None
        self.training_time_seconds = 0

        self.setup_ui()

        self.set_idle_timer(0)
        self.update_current_time()
        self.training_time(0)

        self.controller_thread = threading.Thread(target=self.monitor_controller, daemon=True)
        self.controller_thread.start()

        self.window.mainloop()

    def setup_ui(self):
        # Left frame
        left_frame = tk.Frame(self.window, bg="black", width=650)
        left_frame.pack_propagate(False)
        left_frame.pack(fill="y", side="left")

        left_frame_top = tk.Frame(left_frame, bg="black", height=240)
        left_frame_top.pack_propagate(False)
        left_frame_top.pack(fill="x", side="top")

        left_frame_bottom = tk.Frame(left_frame, bg="black", height=80)
        left_frame_bottom.pack_propagate(False)
        left_frame_bottom.pack(fill="x", side="top")

        # Timer label
        self.timer_label = tk.Label(
            left_frame_top,
            font=self.principal_font,
            bg="black",
            fg="red",
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.timer_label.pack(expand=True, fill="both", side="top")

        # Training time label
        self.training_time_label = tk.Label(
            left_frame_bottom,
            font=self.small_font,
            bg="black",
            fg="white",
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.training_time_label.pack(expand=True, fill="both", side="left")

        # Current time label
        self.current_time_label = tk.Label(
            left_frame_bottom,
            font=self.small_font,
            bg="black",
            fg="white",
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.current_time_label.pack(expand=True, fill="both", side="right")

        # Right frame
        right_frame = tk.Frame(self.window, width=310)
        right_frame.pack_propagate(False)
        right_frame.pack(side="right", fill="y")

        training = get_last_training(self.user, self.training)
        exercise = training.loc[training['ExerciseNumber'] == 1, 'Exercise'].values[0]
        weight = training.loc[training['ExerciseNumber'] == 1, 'Weight'].values[0]
        serie = training.loc[training['ExerciseNumber'] == 1, 'Set'].values[0]
        rep = training.loc[training['ExerciseNumber'] == 1, 'Reps'].values[0]


        # Exercise label
        self.exercise_label = tk.Label(
            right_frame,
            text=exercise,
            font=self.small_font,
            bg="black",
            fg="white",
            anchor="center",
            justify="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.exercise_label.pack(expand=True, fill="both", side="top")


        right_middle_frame = tk.Frame(right_frame, bg="black")
        right_middle_frame.pack(expand=True, fill="both", side="top")      

        # Series label
        self.weight_label = tk.Label(
            right_middle_frame,
            text=f"W: {weight}",
            font=self.small_font,
            bg="black",
            fg="white",
            # width=10,
            height=1,
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.weight_label.pack(expand=True, fill="both", side="left")
        
        self.serie_label = tk.Label(
            right_middle_frame,
            text=f"S: {serie}",
            font=self.small_font,
            bg="black",
            fg="white",
            # width=10,
            height=1,
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.serie_label.pack(expand=True, fill="both", side="right")

        border_frame = tk.Frame(right_frame, bg="white", bd=2)
        border_frame.pack(expand=True, fill="both")  # 
        inner_frame = tk.Frame(border_frame, bg="black")
        inner_frame.pack(expand=True, fill="both") 

        # Weight label
        self.last_rep_label = tk.Label(
            inner_frame,
            text=f"Rep:{rep} / ",
            font=self.small_font,
            bg="black",
            fg="white",
            width=11,
            height=1,
            anchor="e",
        )
        self.last_rep_label.pack(expand=True, fill="both", side="left")  

        self.actual_rep_label = tk.Label(
            inner_frame,
            text=f"0",
            font=self.small_font,
            bg="black",
            fg="white",
            width=2,
            height=1,
            anchor="w",
        )
        self.actual_rep_label.pack(expand=True, fill="both", side="right")  

        self.is_visible = True
        self.blink_label()

    def set_idle_timer(self, t):
        # Reset the idle timer
        self.idle_timer_seconds = t

        # Cancel any existing timer
        if self.idle_timer_id is not None:
            self.window.after_cancel(self.idle_timer_id)

        # Update the label immediately
        self.update_idle_timer()

    def update_idle_timer(self):
        # Update the timer count
        hours, remainder = divmod(self.idle_timer_seconds, 3600)
        mins, secs = divmod(remainder, 60)
        timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
        self.timer_label.configure(text=timeformat)

        # Increment the timer
        self.idle_timer_seconds += 1

        # Schedule the next update
        self.idle_timer_id = self.window.after(1000, self.update_idle_timer)

    def update_current_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.current_time_label.config(text=f"{current_time}")
        self.window.after(1000, self.update_current_time)

    def training_time(self, t):
        self.training_time_seconds = t
        hours, remainder = divmod(t, 3600)
        mins, secs = divmod(remainder, 60)
        timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
        self.training_time_label.configure(text=f"{timeformat}")
        self.window.after(1000, lambda: self.training_time(self.training_time_seconds + 1))


    def blink_label(self):
        if self.is_visible:
            self.actual_rep_label.config(fg="white") 
        else:
            self.actual_rep_label.config(fg=self.actual_rep_label["bg"])  
        self.is_visible = not self.is_visible

        self.window.after(500, self.blink_label)

    def monitor_controller(self):
        try:
            gamepad = InputDevice("/dev/input/event4")  # Update event number if needed
            for event in gamepad.read_loop():
                if event.type == ecodes.EV_KEY:  # Button events
                    key_event = categorize(event)
                    if key_event.keystate == 1 and key_event.keycode[0] == "BTN_A":  # Button A on Xbox controller
                        print("Button A pressed, resetting idle timer!")
                        self.set_idle_timer(0)  # Reset idle timer
        except:
            return None