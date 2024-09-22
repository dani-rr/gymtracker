# import os, sys
# os.chdir("/home/elda/projects/gymtracker" )

from lib.libhelper.db import *
from lib.libclass.training_form import TrainingForm
from lib.libclass.timer_form import TimerForm
from lib.libclass.user_form import UserForm


def main():
    # Connect to the database
    db_connect()
    names = get_names()

    # Initialize SelectionForm
    selection_app = UserForm()
    selection_app.selection_user_layout()
    selection_app.init_selection_user()


    selected_user = selection_app.selected_user 
    # 
    # Initialize TrainingForm with the selected user
    training_app = TrainingForm(selected_user) 
    training_app.selection_training_layout()
    training_app.init_selection_training()

    # Initialize TimerApp (if it uses the same user context, pass it as needed)
    timer_app = TimerForm()
    timer_app.set_idle_timer(0)
    timer_app.update_current_time()
    timer_app.training_time(0)

if __name__ == "__main__":
    main()