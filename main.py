from LibraryApp import app
from flask_script import Manager
from LibraryApp.models import *
manager = Manager(app)

if __name__ == "__main__":
    manager.run()