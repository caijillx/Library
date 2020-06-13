from LibraryApp import app
from flask_script import Manager
from LibraryApp.models import *
from LibraryApp.timer import main as timer_task

manager = Manager(app)
timer_task()

if __name__ == "__main__":
    manager.run()