import tkinter as tk
from tkinter import font
import time
import threading
from evdev import InputDevice, categorize, ecodes

class TimerForm:
    def __init__(self):
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

        # Exercise label
        self.exercise_label = tk.Label(
            right_frame,
            text="Ejercicio\nde prueba",
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

        # Series label
        self.serie_label = tk.Label(
            right_frame,
            text=f"{'S:' : <1}{'22' : >5}",
            font=self.small_font,
            bg="black",
            fg="white",
            width=10,
            height=1,
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.serie_label.pack(expand=True, fill="both", side="top")

        # Weight label
        self.weight_label = tk.Label(
            right_frame,
            text=f"{'W:' : <1}{'22' : >5}",
            font=self.small_font,
            bg="black",
            fg="white",
            width=10,
            height=1,
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2
        )
        self.weight_label.pack(expand=True, fill="both", side="bottom")  # Pack this label at the bottom

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