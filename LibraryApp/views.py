# 定义视图
from LibraryApp import app

from flask import render_template,redirect,sessions,url_for
from LibraryApp.models import *
import datetime
import os


# 导航界面
@app.route('/')
def index():
    admin = Admin.query.filter(Admin.user_name=="ys").first()
    return "<h1>欢迎来到主页！{}</h1>".format(admin.user_name)


# 登录界面
@app.route('/login')
def login():
    return render_template('login.html')


# 入库管理界面
@app.route('/putin')
def login():
    return render_template('putin.html')


# 借书界面
@app.route('/borrowbook')
def login():
    return render_template('borrowbook.html')


# 预约界面
@app.route('/orderbook')
def login():
    return render_template('orderbook.html')


i = 1
