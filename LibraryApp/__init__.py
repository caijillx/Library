# 初始化文件
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:llx17121541@cdb-mg4o2vhq.cd.tencentcdb.com:10089/Library?charset=utf8"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = "llx17121541"
app.config["UP_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
app.config["FC_DIR"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/admin/")
app.config["SCHEDULER_API_ENABLED"] = True
app.debug = False
db = SQLAlchemy(app)

import LibraryApp.views


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

