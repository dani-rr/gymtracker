import tkinter as tk
from tkinter import font
import time
from datetime import datetime
from lib.libhelper.db import *
from lib.libclass.controller import *

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
        self.exercise_number = 1

        self.setup_ui()

        self.set_idle_timer(0)
        self.update_current_time()
        self.training_time(0)

        # Initialize Controller
        self.controller = Controller()
        self.controller.register_listener(self.handle_controller_input)

        self.window.mainloop()



    def setup_ui(self):
        # Left frame
        self.left_frame = tk.Frame(self.window, bg="black", width=650)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(fill="y", side="left")

        self.left_frame_top = tk.Frame(self.left_frame, bg="black", height=240)
        self.left_frame_top.pack_propagate(False)
        self.left_frame_top.pack(fill="x", side="top")

        self.left_frame_bottom = tk.Frame(self.left_frame, bg="black", height=80)
        self.left_frame_bottom.pack_propagate(False)
        self.left_frame_bottom.pack(fill="x", side="top")

        # Timer label
        self.timer_label = tk.Label(
            self.left_frame_top,
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
            self.left_frame_bottom,
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
            self.left_frame_bottom,
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
        self.right_frame = tk.Frame(self.window, width=310)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side="right", fill="y")

        self.set_df()

        # Exercise label
        self.exercise_label = tk.Label(
            self.right_frame,
            text=self.exercise,
            font=self.small_font,
            bg="black",
            fg="white",
            anchor="center",
            justify="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2,
            wraplength=280
        )
        self.exercise_label.pack(expand=True, fill="both", side="top")


        self.right_middle_frame = tk.Frame(self.right_frame, bg="black")
        self.right_middle_frame.pack(expand=True, fill="both", side="top")      

        # Series label
        self.weight_label = tk.Label(
            self.right_middle_frame,
            text=f"W: {self.weight}",
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
        
        self.set_label = tk.Label(
            self.right_middle_frame,
            text=f"S: {self.set}",
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
        self.set_label.pack(expand=True, fill="both", side="right")

        self.border_frame = tk.Frame(self.right_frame, bg="white", bd=2)
        self.border_frame.pack(expand=True, fill="both")  # 
        self.inner_frame = tk.Frame(self.border_frame, bg="black")
        self.inner_frame.pack(expand=True, fill="both") 

        # Weight label
        self.last_rep_label = tk.Label(
            self.inner_frame,
            text=f"Rep:{self.rep} / ",
            font=self.small_font,
            bg="black",
            fg="white",
            width=11,
            height=1,
            anchor="e",
        )
        self.last_rep_label.pack(expand=True, fill="both", side="left")  

        self.actual_rep_label = tk.Label(
            self.inner_frame,
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
        self.blink_label("white")

    def set_df(self):
        self.weight_steps = [4, 7, 9, 11, 14, 16, 18, 20, 23, 25, 27, 30, 32, 34, 36, 39, 41]
        self.training_df = get_last_training(self.user, self.training)
        self.new_training_df = self.training_df.copy()
        self.new_training_df = self.new_training_df.assign(Reps=0)
        self.new_training_df = self.new_training_df.assign(Date=datetime.today().strftime('%Y-%m-%d'))
        self.list_exercise_numbers = sorted(self.new_training_df['ExerciseNumber'].unique())
        self.exercise = self.training_df.loc[self.training_df['ExerciseNumber'] == self.exercise_number, 'Exercise'].values[0]
        self.set = self.training_df.loc[self.training_df['ExerciseNumber'] == self.exercise_number, 'Set'].values[0]

        self.weight = self.training_df.loc[
            (self.training_df['ExerciseNumber'] == self.exercise_number) &
            (self.training_df['Set'] == self.set),
            'Weight'].values[0]
        for ex in self.list_exercise_numbers:
            goal_reps = self.training_df.loc[self.training_df['ExerciseNumber'] == ex, 'GoalReps'].sum()
            last_reps = self.training_df.loc[self.training_df['ExerciseNumber'] == ex, 'Reps'].sum()
            if goal_reps <= last_reps:
                exercise_set_weight = self.training_df.loc[
                                        (self.training_df['ExerciseNumber'] == ex) &
                                        (self.training_df['Set'] == self.set),
                                        'Weight'].values[0]
                current_weigt_index = self.weight_steps.index(exercise_set_weight)
                next_weight = self.weight_steps[current_weigt_index + 1]
                self.training_df.loc[self.training_df['ExerciseNumber'] == ex, 'Reps'] = "*"
                self.new_training_df.loc[self.new_training_df['ExerciseNumber'] == ex, 'Weight'] = next_weight

        self.rep = self.training_df.loc[
            (self.training_df['ExerciseNumber'] == self.exercise_number) &
            (self.training_df['Set'] == self.set),
            'Reps'].values[0]    
        print(self.training_df)
        print(self.new_training_df)
        print('here')


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


    def blink_label(self, color):
        if self.is_visible:
            self.actual_rep_label.config(fg=color)
        else:
            self.actual_rep_label.config(fg=self.actual_rep_label["bg"])  
        self.is_visible = not self.is_visible

        # Store the after ID for future cancellation
        self.blink_id = self.window.after(1000, lambda: self.blink_label(color))

    def handle_controller_input(self, keycode):
        match keycode:
            case "BTN_B":
                self.set_idle_timer(0)    
            case "DOWN" | "UP":
                self.update_exercise(keycode)
            case "RIGHT" | "LEFT":
                self.update_set(keycode)
            case "BTN_A":
                self.insert_rep = True
                self.set_rep()
        
    def set_rep(self):
        if hasattr(self, 'blink_id'):
            self.window.after_cancel(self.blink_id)  # Cancel the blinking

        # Now start the blink in yellow
        self.blink_label("yellow")

    def update_set(self, keycode):
        self.max_set = self.training_df[self.training_df['Training'] == self.training]["Set"].max()
        if keycode == "RIGHT" and self.set < self.max_set:
            self.set = self.set + 1
            self.update_set_layout()
        elif keycode == "LEFT" and self.set > 1:
            self.set = self.set - 1
            self.update_set_layout()

    def update_exercise(self, keycode):
        self.max_exercise = self.training_df[self.training_df['Training'] == self.training]["ExerciseNumber"].max()
        if keycode == "UP" and self.exercise_number < self.max_exercise: 
            self.exercise_number += 1
            self.update_exercise_layout()
        elif keycode == "DOWN" and self.exercise_number > 1:
            self.exercise_number -= 1
            self.update_exercise_layout()

    def update_exercise_layout(self):
        self.exercise = self.training_df.loc[self.training_df['ExerciseNumber'] == self.exercise_number, 'Exercise'].values[0]
        self.set = self.training_df.loc[self.training_df['ExerciseNumber'] == self.exercise_number, 'Set'].values[0]
        self.rep = self.training_df.loc[
            (self.training_df['ExerciseNumber'] == self.exercise_number) &
            (self.training_df['Set'] == self.set),
            'Reps'].values[0]
        self.weight = self.training_df.loc[
            (self.training_df['ExerciseNumber'] == self.exercise_number) &
            (self.training_df['Set'] == self.set),
            'Weight'].values[0]

        self.exercise_label.config(text=self.exercise)
        self.weight_label.config(text=f"W: {self.weight}")
        self.set_label.config(text=f"S: {self.set}")
        self.last_rep_label.config(text=f"Rep:{self.rep} / ")

    def update_set_layout(self):
        self.rep = self.training_df.loc[
            (self.training_df['ExerciseNumber'] == self.exercise_number) &
            (self.training_df['Set'] == self.set),
            'Reps'].values[0]
        self.weight = self.training_df.loc[
            (self.training_df['ExerciseNumber'] == self.exercise_number) &
            (self.training_df['Set'] == self.set),
            'Weight'].values[0]

        self.set_label.config(text=f"S: {self.set}")
        self.weight_label.config(text=f"W: {self.weight}")
        self.last_rep_label.config(text=f"Rep:{self.rep} / ")

        