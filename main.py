from LibraryApp import app
from flask_script import Manager
from LibraryApp.models import *
from LibraryApp.timer import *

manager = Manager(app)

if __name__ == "__main__":
    manager.run()