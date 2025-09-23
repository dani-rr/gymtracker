import tkinter as tk
from tkinter import font
from typing import Callable

from ...devices.controller import Controller
from ...services.training_service import TrainingService


class TrainingForm:
    def __init__(
        self,
        user: str,
        service: TrainingService,
        on_training_selected: Callable[[str], None],
        on_back: Callable[[], None],
    ) -> None:
        self.user = user
        self._service = service
        self._on_training_selected = on_training_selected
        self._on_back = on_back
        self.training_window: tk.Tk | None = None
        self.buttons: list[tk.Button] = []
        self.index = 0
        self.selected_training: str | None = None
        self.controller = Controller()
        self.controller.register_listener(self.handle_controller_input_training)
        self.selection_training_layout()

    def handle_controller_input_training(self, keycode):
        match keycode:
            case "RIGHT" | "LEFT":
                self.switch_button(keycode)
            case "BTN_A":
                self.on_enter()
            case "BTN_B":
                self.go_back()
        
    def go_back(self):
        if self.training_window is None:
            return
        self.controller.stop()
        self.training_window.destroy()
        self._on_back()


    def select_training(self, option: str):
        if self.training_window is None:
            return
        self.selected_training = option
        self.controller.stop()
        self.training_window.destroy()
        self._on_training_selected(option)

    def highlight_button(self, button):
        for btn in self.buttons:
            btn.configure(bg='black', fg='white') 
        button.configure(bg='white', fg='black') 

    def switch_button(self, event):
        # Switch focus between buttons
        if event == "LEFT":
            if self.index > 0:
                self.index -= 1
        elif event == "RIGHT":
            if self.index < len(self.buttons) - 1:
                self.index += 1
        self.buttons[self.index].focus_set()
        self.highlight_button(self.buttons[self.index])

    def on_enter(self):
        # Invoke the currently focused button
        focused_widget = self.training_window.focus_get()
        if focused_widget in self.buttons:
            focused_widget.invoke()

    def selection_training_layout(self):
        trainings, trainings_strings = self._service.list_trainings(self.user)

        self.training_window = tk.Tk()
        self.training_window.geometry("960x320")
        self.training_window.configure(bg='black')

        menu_font = font.Font(family="Digital-7 Mono", size=50)

        label = tk.Label(
            self.training_window,
            text="What are we gonna train today?",
            font=menu_font,
            bg="black",
            fg="white",
        )
        label.pack(pady=20)

        base_x = 100
        spacing = 255

        for idx, display_text in enumerate(trainings_strings):
            training_value = trainings[idx]
            button = tk.Button(
                self.training_window,
                bg='black',
                fg='white',
                bd=0,
                highlightthickness=0,
                text=display_text,
                font=menu_font,
                command=lambda value=training_value: self.select_training(value),
            )
            button.place(x=base_x + idx * spacing, y=150, width=250, height=80)
            self.buttons.append(button)

    def init_selection_training(self):
        # Start the window's main loop
        if not self.training_window or not self.buttons:
            return
        self.training_window.after(
            100, lambda: (self.buttons[0].focus_set(), self.highlight_button(self.buttons[0]))
        )
        self.training_window.mainloop()
