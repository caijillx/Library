# 定义视图
from LibraryApp import app

from flask import render_template, redirect, session, url_for, flash, request
from LibraryApp.forms import LoginForm
from LibraryApp.models import *
from functools import wraps
import json
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
    """
    if form.validate_on_submit(): 意思为如果有表单提交 且通过验证
    等价于 if request.method == "POST"： 意思为如果有POST请求
    :return:
    """
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        print(data["name"])
        admin = Admin.query.filter_by(user_name=data["name"]).first()
        print(admin)
        if admin is None:
            flash("该用户不存在！", "err")
            return redirect(url_for("login"))
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for("login"))
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
    books = Book.query.all()
    agent_id = session["user_id"]
    return render_template('putin.html', books=books, agent_id=agent_id)


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


# 修改书目数目
@app.route('/change_isbn_num', methods=['POST'])
def change_isbn_num():
    """
    用来修改书目数目，暂时无用，请不要乱用哦。
    :return:
    """
    try:
        book = Book.query.filter(Book.isbn == request.form.get('isbn')).first()
        book.amount = request.form.get('num')
        db.session.commit()
        print("success")
        return json.dumps({"state": 200, "message": "修改成功！"})
    except Exception as e:
        print(e)
        return json.dumps({"message": e})


# 获取book_info
@app.route('/get_BI_by_ibsn', methods=['POST'])
def get_BI_by_ibsn():
    """
    在修改时获取书本信息，给用户参考。
    :return:返回格式为json格式的数组，包括书本id，书本所在地，书本状态。
    """
    print(request.form.get('isbn'))
    bookinfos = BookInfo.query.filter(BookInfo.isbn == request.form.get('isbn')).all()
    ls = []
    for b in bookinfos:
        ls.append({"book_id": b.book_id, "location": b.location, "status": b.status})
    return json.dumps(ls)


# 添加书本
@app.route('/add_bookinfo', methods=['POST'])
def add_bookinfo():
    """
    使用 request.form.get获取json中的数据，并向数据库添加书本数据。
    :return:返回格式为json格式，若成功则返回status为200，和对应的提示信息，失败则返回status为0。
    """
    try:
        agent_id = request.form.get('agent_id')
        isbn = request.form.get('isbn')
        book_ids = json.loads(request.form.get('book_id'))
        locations = json.loads(request.form.get('location'))
        for index, location in enumerate(locations):
            book_info = BookInfo()
            book_info.book_id = book_ids[index]
            book_info.isbn = isbn
            book_info.status = "未借出" if locations == "图书流通室" else "不外借"
            book_info.agent_id = agent_id
            book_info.location = location
            print(book_info)
            db.session.add(book_info)
        db.session.commit()
        return json.dumps({"state": 200, "message": "修改成功！"})
    except Exception as e:
        print(e)
        return json.dumps({"state": 0, "message": e})
