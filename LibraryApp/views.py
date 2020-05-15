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
    return render_template('index.html')

# 登录界面
@app.route('/login')
def login():
    return render_template('login.html')


# 入库管理界面
@app.route('/putin')
def putin():
    return render_template('putin.html')


# 借书界面
@app.route('/borrowbook')
def borrowbook():
    return render_template('borrowbook.html')


# 预约界面
@app.route('/orderbook')
def orderbook():
    return render_template('orderbook.html')


# 还书界面
@app.route('/returnbook')
def returnbook():
    return render_template('returnbook.html')


