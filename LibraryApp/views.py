# 定义视图
from LibraryApp import app

from flask import render_template, redirect, session, url_for, flash, request
from LibraryApp.forms import LoginForm
from LibraryApp.models import *
from functools import wraps
import datetime
import os


# 定义登录判断装饰器
def admin_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # session不存在时请求登录
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# 导航界面
@app.route('/')
@admin_login_req
def index():
    return render_template('index.html')


# 登录界面
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(user_name=data["name"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("home.login"))
        session["user"] = data["name"]
        session["user_id"] = admin.user_id
        return redirect(url_for("index"))
    return render_template('login.html', form=form)


# 定义登出视图
@app.route("/logout/")
@admin_login_req
def logout():
    session.pop("user")
    session.pop("user_id")
    return redirect(url_for("login"))


# 入库管理界面
@app.route('/putin')
@admin_login_req
def putin():
    return render_template('putin.html')


# 借书界面
@app.route('/borrowbook')
@admin_login_req
def borrowbook():
    return render_template('borrowbook.html')


# 预约界面
@app.route('/orderbook')
@admin_login_req
def orderbook():
    return render_template('orderbook.html')


# 还书界面
@app.route('/returnbook')
@admin_login_req
def returnbook():
    return render_template('returnbook.html')
