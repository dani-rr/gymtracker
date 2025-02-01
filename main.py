# import os, sys
# os.chdir("/home/elda/projects/gymtracker" )

from lib.libhelper.db import *
from lib.libclass.training_form import TrainingForm
from lib.libclass.timer_form import TimerForm
from lib.libclass.user_form import UserForm
from lib.libclass.controller import *



def call_userForm():
    # Initialize SelectionForm
    user_app = UserForm()
    user_app.init_selection_user()

def call_trainingForm(user):
    # Initialize TrainingForm with the selected user
    training_app = TrainingForm(user) 
    training_app.init_selection_training()

def call_timerForm(user, training):
    # Initialize TimerApp (if it uses the same user context, pass it as needed)
    timer_app = TimerForm(user, training)
    timer_app.set_idle_timer(0)
    timer_app.update_current_time()
    timer_app.training_time(0)



def main():
    # Connect to the database
    db_connect()
    names = get_names()
    call_userForm()

if __name__ == "__main__":
    main()