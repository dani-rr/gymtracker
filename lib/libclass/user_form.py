import tkinter as tk
from tkinter import font
from lib.libhelper.db import *


class UserForm:
    def __init__(self):
        self.selection_window = None
        self.buttons = []
        self.index = 0
        self.selected_user = None 

    def select_user(self, option):
        self.selected_user = option
        self.selection_window.destroy()

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
        focused_widget = self.selection_window.focus_get()
        if focused_widget in self.buttons:
            focused_widget.invoke()

    def selection_user_layout(self):
        # Create the selection window layout
        names = get_names()

        self.selection_window = tk.Tk()
        self.selection_window.geometry("960x320")

        self.selection_window.configure(bg='black')

        menu_font = font.Font(family="Digital-7 Mono", size=50)

        label = tk.Label(self.selection_window, text="Who is gonna sweat today?", font=menu_font, bg="black", fg="white")
        label.pack(pady=20)

        for i, name in enumerate(names):
            button = tk.Button(
                self.selection_window,
                bg='black',
                fg='white',
                bd=0,
                highlightthickness=0,
                text=name,
                font=menu_font,
                command=lambda name=name: self.select_user(name)
            )
            button.place(x=250 + (i * 310), y=150, width=250, height=80) 
            self.buttons.append(button)

    def init_selection_user(self):
        # Start the window's main loop
        self.selection_window.after(100, lambda: (self.buttons[0].focus_set(), self.highlight_button(self.buttons[0])))
        self.selection_window.bind('<Left>', self.switch_button)
        self.selection_window.bind('<Right>', self.switch_button)
        self.selection_window.bind('<Return>', self.on_enter)
        self.selection_window.mainloop()
