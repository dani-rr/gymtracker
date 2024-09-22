import tkinter as tk
from tkinter import font
from lib.libhelper.db import *

class TrainingForm:
    def __init__(self, user):
        self.user = user  
        self.training_window = None
        self.buttons = []
        self.index = 0

    def select_training(self, option):
        self.selected_training = option
        self.training_window.destroy() 

    def highlight_button(self, button):
        for btn in self.buttons:
            btn.configure(bg='black', fg='white') 
        button.configure(bg='white', fg='black') 

    def switch_button(self, event):
        # Switch focus between buttons
        if event.keysym == 'Left':
            if self.index > 0:
                self.index -= 1
        elif event.keysym == 'Right':
            if self.index < len(self.buttons) - 1:
                self.index += 1
        self.buttons[self.index].focus_set()
        self.highlight_button(self.buttons[self.index])

    def on_enter(self, event):
        # Invoke the currently focused button
        focused_widget = self.training_window.focus_get()
        if focused_widget in self.buttons:
            focused_widget.invoke()

    def selection_training_layout(self):
        # Create the selection window layout
        trainings = get_trainings(self.user)

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
            text=trainings[0], 
            font=menu_font, 
            command=lambda: self.select_training(trainings[0])
        )
        training_1_button.place(x=150, y=150, width=150, height=80)

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
        training_2_button.place(x=405, y=150, width=150, height=80)

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
        training_3_button.place(x=660, y=150, width=150, height=80)

        self.buttons = [training_1_button, training_2_button, training_3_button]

    def init_selection_training(self):
        # Start the window's main loop
        self.training_window.after(100, lambda: (self.buttons[0].focus_set(), self.highlight_button(self.buttons[0])))
        self.training_window.bind('<Left>', self.switch_button)
        self.training_window.bind('<Right>', self.switch_button)
        self.training_window.bind('<Return>', self.on_enter)
        self.training_window.mainloop()
