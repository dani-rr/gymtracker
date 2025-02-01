import tkinter as tk
from tkinter import font
from lib.libhelper.db import *
from lib.libclass.timer_form import *
from lib.libclass.controller import Controller


class TrainingForm:
    def __init__(self, user):
        import main
        self.user = user  
        self.training_window = None
        self.buttons = []
        self.index = 0
        self.selected_training = None
        cc = Controller()
        cc.register_listener(self.handle_controller_input_training) 
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
        from main import call_userForm
        self.training_window.destroy() 
        call_userForm()


    def select_training(self, option):
        self.selected_training = option
        self.training_window.destroy() 
        timer_app = TimerForm(self.user, self.selected_training)
        timer_app.set_idle_timer(0)
        timer_app.update_current_time()
        timer_app.training_time(0)

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
        # Create the selection window layout
        trainings, trainings_strings = get_trainings(self.user)

        self.training_window = tk.Tk()
        self.training_window.geometry("960x320")
        self.training_window.configure(bg='black')

        menu_font = font.Font(family="Digital-7 Mono", size=50)

        label = tk.Label(self.training_window, text="What are we gonna train today?", font=menu_font, bg="black", fg="white")
        label.pack(pady=20)

        training_1_button = tk.Button(
            self.training_window, 
            bg='black',
            fg='white',
            bd=0,
            highlightthickness=0,
            text=trainings_strings[0], 
            font=menu_font, 
            command=lambda: self.select_training(trainings[0])
        )
        training_1_button.place(x=100, y=150, width=250, height=80)

        training_2_button = tk.Button(
            self.training_window, 
            bg='black',
            fg='white',
            bd=0,
            highlightthickness=0,
            text=trainings[1], 
            font=menu_font, 
            command=lambda: self.select_training(trainings[2])
        )
        training_2_button.place(x=355, y=150, width=250, height=80)

        training_3_button = tk.Button(
            self.training_window, 
            bg='black',
            fg='white',
            bd=0,
            highlightthickness=0,
            text=trainings[2], 
            font=menu_font, 
            command=lambda: self.select_training(trainings[2])
        )
        training_3_button.place(x=610, y=150, width=250, height=80)

        self.buttons = [training_1_button, training_2_button, training_3_button]

    def init_selection_training(self):
        # Start the window's main loop
        self.training_window.after(100, lambda: (self.buttons[0].focus_set(), self.highlight_button(self.buttons[0])))
        self.training_window.mainloop()
