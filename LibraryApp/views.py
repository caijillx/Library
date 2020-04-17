# 定义视图
from LibraryApp import app

from flask import render_template,redirect,sessions,url_for
from LibraryApp.models import *
import datetime
import os


@app.route('/')
def index():
    admin = Admin.query.filter(Admin.user_name=="ys").first()
    return "<h1>欢迎来到主页！{}</h1>".format(admin.user_name)

@app.route('/login')
def login():
    return render_template('login.html')