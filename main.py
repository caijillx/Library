from LibraryApp import app
from flask_script import Manager
from LibraryApp.models import *
manager = Manager(app)

if __name__ == "__main__":
    # reader = Reader(id="17121385",name="mmmm",phone="111111",Email="15151@qq.com")
    # db.session.add(reader)
    # db.session.commit()
    manager.run()