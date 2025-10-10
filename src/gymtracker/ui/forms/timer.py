from __future__ import annotations

import time
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from tkinter import font
from typing import Optional

from ...devices.controller import Controller
from ...services.training_service import TrainingService


@dataclass(frozen=True)
class ExerciseSnapshot:
    exercise_number: int
    exercise_name: str
    set_number: int
    weight: int
    last_rep: int
    planned_rep: int


class TrainingSession:
    """Encapsulate data preparation and navigation for a training session."""

    _WEIGHT_STEPS = [4, 7, 9, 11, 14, 16, 18, 20, 23, 25, 27, 30, 32, 34, 36, 39, 41]

    def __init__(self, service: TrainingService, user: str, training: str) -> None:
        self._service = service
        self._user = user
        self._training = training

        self._training_df = None
        self._planned_df = None
        self._exercise_numbers: list[int] = []
        self.exercise_number: int = 1
        self._current_set: int = 1

        self._load_training_data()

    @property
    def training(self):
        return self._training

    def _load_training_data(self) -> None:
        training_df = self._service.fetch_last_training(self._user, self._training).copy()
        if training_df.empty:
            raise ValueError("Training data is empty")

        training_df['Reps'] = training_df['Reps'].astype('Int64')
        planned_df = training_df.copy()
        planned_df = planned_df.assign(Reps=0)
        planned_df = planned_df.assign(Date=datetime.today().strftime('%Y-%m-%d'))

        self._training_df = training_df
        self._planned_df = planned_df
        self._exercise_numbers = sorted(planned_df['ExerciseNumber'].unique())
        self.exercise_number = self._exercise_numbers[0]
        self._current_set = int(training_df.loc[training_df['ExerciseNumber'] == self.exercise_number, 'Set'].min())

        self._apply_weight_progression()

    def _apply_weight_progression(self) -> None:
        for exercise_number in self._exercise_numbers:
            goal_reps = int(
                self._training_df.loc[
                    self._training_df['ExerciseNumber'] == exercise_number, 'GoalReps'
                ].sum()
            )
            last_reps = int(
                self._training_df.loc[
                    self._training_df['ExerciseNumber'] == exercise_number, 'Reps'
                ].sum()
            )
            if goal_reps <= last_reps:
                weight_value = int(
                    self._training_df.loc[
                        (self._training_df['ExerciseNumber'] == exercise_number)
                        & (self._training_df['Set'] == self._current_set),
                        'Weight',
                    ].values[0]
                )
                current_index = self._WEIGHT_STEPS.index(weight_value)
                next_weight = self._WEIGHT_STEPS[current_index + 1]
                self._training_df.loc[
                    self._training_df['ExerciseNumber'] == exercise_number, 'Reps'
                ] = 0
                self._planned_df.loc[
                    self._planned_df['ExerciseNumber'] == exercise_number, 'Weight'
                ] = next_weight

    def snapshot(self) -> ExerciseSnapshot:
        exercise_mask = self._training_df['ExerciseNumber'] == self.exercise_number
        exercise_name = str(
            self._training_df.loc[exercise_mask, 'Exercise'].iloc[0]
        )
        set_mask = exercise_mask & (self._training_df['Set'] == self._current_set)
        weight = int(self._training_df.loc[set_mask, 'Weight'].iloc[0])
        last_rep = int(self._training_df.loc[set_mask, 'Reps'].iloc[0])
        planned_rep = int(self._planned_df.loc[set_mask, 'Reps'].iloc[0])
        return ExerciseSnapshot(
            exercise_number=self.exercise_number,
            exercise_name=exercise_name,
            set_number=self._current_set,
            weight=weight,
            last_rep=last_rep,
            planned_rep=planned_rep,
        )

    def move_exercise(self, delta: int) -> bool:
        index = self._exercise_numbers.index(self.exercise_number) + delta
        if not 0 <= index < len(self._exercise_numbers):
            return False
        self.exercise_number = self._exercise_numbers[index]
        mask = self._training_df['ExerciseNumber'] == self.exercise_number
        self._current_set = int(self._training_df.loc[mask, 'Set'].min())
        return True

    def move_set(self, delta: int) -> bool:
        mask = self._training_df['ExerciseNumber'] == self.exercise_number
        available_sets = sorted(self._training_df.loc[mask, 'Set'].unique())
        current_index = available_sets.index(self._current_set) + delta
        if not 0 <= current_index < len(available_sets):
            return False
        self._current_set = int(available_sets[current_index])
        return True

    def save_new_rep(self, value: int) -> None:
        mask = (
            (self._planned_df['ExerciseNumber'] == self.exercise_number)
            & (self._planned_df['Set'] == self._current_set)
        )
        self._planned_df.loc[mask, 'Reps'] = value

    @property
    def planned_training(self):
        return self._planned_df.copy()


class TimerForm:
    def __init__(
        self,
        user: str,
        training: str,
        service: TrainingService,
        controller: Controller,
    ) -> None:

        self.user = user
        self.training = training
        self._service = service
        self.controller = controller

        self.session = TrainingSession(service, user, training)

        self.window = self._create_window()
        self.principal_font: font.Font
        self.small_font: font.Font
        self._configure_fonts()
        self._build_interface()

        snapshot = self.session.snapshot()

        self.insert_rep = False
        self.new_rep = snapshot.planned_rep
        self.is_visible = True
        self.blink_id: Optional[str] = None
        self.idle_timer_seconds = 0
        self.idle_timer_id: Optional[str] = None
        self.training_time_seconds = 0

        self._apply_snapshot(snapshot)
        self._restart_blink("white")
        self.set_idle_timer(0)
        self.update_current_time()
        self.training_time(0)

        self.controller.set_listener(self.handle_controller_input)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.window.mainloop()

    def _create_window(self) -> tk.Tk:
        window = tk.Tk()
        window.geometry("960x320")
        window.configure(bg="black")
        return window

    def _configure_fonts(self) -> None:
        self.principal_font = font.Font(family="Digital-7 Mono", size=100)
        self.small_font = font.Font(family="Digital-7 Mono", size=30)

    def _build_interface(self) -> None:
        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self) -> None:
        self.left_frame = tk.Frame(self.window, bg="black", width=650)
        self.left_frame.pack_propagate(False)
        self.left_frame.pack(fill="y", side="left")

        self.left_frame_top = tk.Frame(self.left_frame, bg="black", height=240)
        self.left_frame_top.pack_propagate(False)
        self.left_frame_top.pack(fill="x", side="top")

        self.left_frame_bottom = tk.Frame(self.left_frame, bg="black", height=80)
        self.left_frame_bottom.pack_propagate(False)
        self.left_frame_bottom.pack(fill="x", side="top")

        self.timer_label = tk.Label(
            self.left_frame_top,
            font=self.principal_font,
            bg="black",
            fg="red",
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2,
        )
        self.timer_label.pack(expand=True, fill="both", side="top")

        self.training_time_label = tk.Label(
            self.left_frame_bottom,
            font=self.small_font,
            bg="black",
            fg="white",
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2,
        )
        self.training_time_label.pack(expand=True, fill="both", side="left")

        self.current_time_label = tk.Label(
            self.left_frame_bottom,
            font=self.small_font,
            bg="black",
            fg="white",
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2,
        )
        self.current_time_label.pack(expand=True, fill="both", side="right")

    def _build_right_panel(self) -> None:
        self.right_frame = tk.Frame(self.window, width=310)
        self.right_frame.pack_propagate(False)
        self.right_frame.pack(side="right", fill="y")

        self.exercise_label = tk.Label(
            self.right_frame,
            text="",
            font=self.small_font,
            bg="black",
            fg="white",
            anchor="center",
            justify="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2,
            wraplength=280,
        )
        self.exercise_label.pack(expand=True, fill="both", side="top")

        self.right_middle_frame = tk.Frame(self.right_frame, bg="black")
        self.right_middle_frame.pack(expand=True, fill="both", side="top")

        self.weight_label = tk.Label(
            self.right_middle_frame,
            text="",
            font=self.small_font,
            bg="black",
            fg="white",
            height=1,
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2,
        )
        self.weight_label.pack(expand=True, fill="both", side="left")

        self.set_label = tk.Label(
            self.right_middle_frame,
            text="",
            font=self.small_font,
            bg="black",
            fg="white",
            height=1,
            anchor="center",
            bd=2,
            highlightbackground="white",
            highlightcolor="white",
            highlightthickness=2,
        )
        self.set_label.pack(expand=True, fill="both", side="right")

        self.border_frame = tk.Frame(self.right_frame, bg="white", bd=2)
        self.border_frame.pack(expand=True, fill="both")

        self.inner_frame = tk.Frame(self.border_frame, bg="black")
        self.inner_frame.pack(expand=True, fill="both")

        self.last_rep_label = tk.Label(
            self.inner_frame,
            text="Rep:- / ",
            font=self.small_font,
            bg="black",
            fg="white",
            width=11,
            height=1,
            anchor="e",
        )
        self.last_rep_label.pack(expand=True, fill="both", side="left")

        self.new_rep_label = tk.Label(
            self.inner_frame,
            text="-",
            font=self.small_font,
            bg="black",
            fg="white",
            width=2,
            height=1,
            anchor="w",
        )
        self.new_rep_label.pack(expand=True, fill="both", side="right")

    def _apply_snapshot(self, snapshot: ExerciseSnapshot) -> None:
        self.exercise_label.config(text=snapshot.exercise_name)
        self.weight_label.config(text=f"W: {snapshot.weight}")
        self.set_label.config(text=f"S: {snapshot.set_number}")
        self.last_rep_label.config(
            text="Rep:- / " if snapshot.last_rep == 0 else f"Rep:{snapshot.last_rep} / "
        )
        self.new_rep = snapshot.planned_rep
        self._update_new_rep_label()

    def _update_new_rep_label(self) -> None:
        if self.new_rep == 0:
            self.new_rep_label.config(text="-")
        else:
            self.new_rep_label.config(text=self.new_rep)

    def set_idle_timer(self, seconds: int) -> None:
        self.idle_timer_seconds = seconds
        if self.idle_timer_id is not None:
            self.window.after_cancel(self.idle_timer_id)
        self.update_idle_timer()

    def update_idle_timer(self) -> None:
        hours, remainder = divmod(self.idle_timer_seconds, 3600)
        mins, secs = divmod(remainder, 60)
        timeformat = f"{hours:02d}:{mins:02d}:{secs:02d}"
        self.timer_label.configure(text=timeformat)
        self.idle_timer_seconds += 1
        self.idle_timer_id = self.window.after(1000, self.update_idle_timer)

    def update_current_time(self) -> None:
        current_time = time.strftime("%H:%M:%S")
        self.current_time_label.config(text=current_time)
        self.window.after(1000, self.update_current_time)

    def training_time(self, seconds: int) -> None:
        self.training_time_seconds = seconds
        hours, remainder = divmod(seconds, 3600)
        mins, secs = divmod(remainder, 60)
        timeformat = f"{hours:02d}:{mins:02d}:{secs:02d}"
        self.training_time_label.configure(text=timeformat)
        self.window.after(1000, lambda: self.training_time(self.training_time_seconds + 1))

    def blink_label(self, color: str) -> None:
        if self.new_rep > 0:
            self.new_rep_label.config(fg=color)
            self.blink_id = None
            return
        if self.is_visible:
            self.new_rep_label.config(fg=color)
        else:
            self.new_rep_label.config(fg=self.new_rep_label["bg"])
        self.is_visible = not self.is_visible
        self.blink_id = self.window.after(1000, lambda: self.blink_label(color))

    def _restart_blink(self, color: str) -> None:
        if self.blink_id is not None:
            self.window.after_cancel(self.blink_id)
            self.blink_id = None
        self.is_visible = True
        self.blink_label(color)

    def handle_controller_input(self, keycode) -> None:
        if self.window is None:
            return
        self.window.after(0, lambda code=keycode: self._dispatch_controller_input(code))

    def _dispatch_controller_input(self, keycode) -> None:
        if self.window is None:
            return
        match keycode:
            case "BTN_B":
                if self.insert_rep:
                    self.set_rep_cancel()
                else:
                    self.set_idle_timer(0)
            case "DOWN" | "UP":
                if self.insert_rep:
                    self.update_rep(keycode)
                else:
                    self.update_exercise(keycode)
            case "RIGHT" | "LEFT":
                if not self.insert_rep:
                    self.update_set(keycode)
            case "BTN_A":
                if self.insert_rep:
                    self.save_rep()
                else:
                    self.insert_rep = True
                    self.set_rep()

    def save_rep(self) -> None:
        self.session.save_new_rep(self.new_rep)
        self.insert_rep = False
        snapshot = self.session.snapshot()
        self._apply_snapshot(snapshot)
        self._restart_blink("white")

    def set_rep(self) -> None:
        self._restart_blink("yellow")

    def set_rep_cancel(self) -> None:
        self.insert_rep = False
        snapshot = self.session.snapshot()
        self._apply_snapshot(snapshot)
        self._restart_blink("white")

    def update_set(self, keycode: str) -> None:
        delta = 1 if keycode == "RIGHT" else -1
        if self.session.move_set(delta):
            snapshot = self.session.snapshot()
            self._apply_snapshot(snapshot)
            if not self.insert_rep:
                self._restart_blink("white")

    def update_exercise(self, keycode: str) -> None:
        delta = 1 if keycode == "UP" else -1
        if self.session.move_exercise(delta):
            snapshot = self.session.snapshot()
            self._apply_snapshot(snapshot)
            if not self.insert_rep:
                self._restart_blink("white")

    def update_rep(self, keycode: str) -> None:
        delta = 1 if keycode == "UP" else -1
        self.new_rep = max(0, self.new_rep + delta)
        self._update_new_rep_label()

    def on_close(self) -> None:
        self.controller.set_listener(None)
        if self.window is not None:
            self.window.destroy()
            self.window = None
