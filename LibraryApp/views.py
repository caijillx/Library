# 定义视图
from LibraryApp import app

from flask import render_template, redirect, session, url_for, flash, request, jsonify
from LibraryApp.forms import LoginForm
from LibraryApp.func import fine_of_returnbook, reserve_email
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
        # print(data["name"])
        admin = Admin.query.filter_by(user_name=data["name"]).first()
        # print(admin)
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
    isbn_list = [book.isbn for book in books]
    return render_template('putin.html', books=books, agent_id=agent_id, isbns=json.dumps(isbn_list))


# 借书界面

@app.route('/borrowbook', methods=['POST', 'GET'])
@admin_login_req
def borrowbook():
    if request.method == 'GET':  # 处理get请求
        bookisbn = request.args.get('bookisbn')
        print('isbn=', bookisbn)
        if bookisbn == None:  # isbn为空，则显示所有书的信息
            book_list = Book.query.all()
            print('book_list', book_list)
            book_list_dict = []
            for book in book_list:
                print(book.isbn)
                book_list_dict.append(
                    {
                        'isbn': book.isbn,
                        'name': book.name,
                        'author': book.author,
                        'publisher': book.publisher,
                        'pub_date': book.pub_date
                    }
                )
            # print(book_list_dict)
            # book_list_json = json.dumps(book_list_dict)

            # return book_list_json
            return render_template('borrowbook.html', books=book_list_dict)
        book_info = BookInfo.query.filter_by(isbn=bookisbn).all()  # isbn不为空，返回具体的书本状态
        bookinfo_list_dict = []
        for book in book_info:
            print(book.isbn)
            bookinfo_list_dict.append(
                {
                    'book_id': book.book_id,
                    'isbn': book.isbn,
                    'location': book.location,
                    'status': book.status
                }
            )
        return render_template('borrowbook.html', bookinfo=bookinfo_list_dict)
    else:  # 处理post请求
        book_id = request.form.get('book_id')
        isbn = request.form.get('isbn')
        id = request.form.get('id')
        user_id = session['user_id']  # session中取经办人id
        book_info = BookInfo.query.filter_by(isbn=isbn).all()  # isbn不为空，返回具体的书本状态
        bookinfo_list_dict = []
        for book in book_info:
            print(book.isbn)
            bookinfo_list_dict.append(
                {
                    'book_id': book.book_id,
                    'isbn': book.isbn,
                    'location': book.location,
                    'status': book.status
                }
            )
        print("book_id:" + book_id)
        print("isbn:" + isbn)
        print("id:" + id)
        print("user_id:" + user_id)
        reader_id = Reader.query.filter_by(id=id).first()
        if reader_id != None:
            # 查询读者借书总数有无超过十本
            bookcount = BorrowInfo.query.filter(BorrowInfo.reader_id == id, BorrowInfo.return_date == None).count()
            print("bookcount:" + bookcount)
            if bookcount >= 10:
                return jsonify({"state": 103, "msg": "借阅成功"})  # 超出借书数量
            # 插入借书记录
            borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前时间 Y-m-d
            due_date = (datetime.datetime.now() + datetime.timedelta(days=60)).strftime("%Y-%m-%d")  # 60天后

            try:
                borroInfo = BorrowInfo()
                borroInfo.reader_id = id
                borroInfo.book_id = book_id
                borroInfo.borrow_date = borrow_date
                borroInfo.due_date = due_date
                borroInfo.agent_id = user_id
                db.session.add(borroInfo)
                db.session.commit()
                bookInfo = BookInfo.query.filter(BookInfo.book_id == book_id).first()
                bookInfo.status = "已借出"
                db.session.commit()
                print("book_status change success")
                return jsonify({"state": 104, "msg": "借阅成功"})  # 由borrowbook的ajax接受，弹窗显示
            except Exception as e:
                print(e)
                return jsonify({"state": 105, "msg": e})  # 由borrowbook的ajax接受，弹窗显示

        else:
            # id在数据库中找不到
            return jsonify({"state": 106, "msg": "没有这个id!"})

        # return render_template('borrowbook.html', bookinfo=bookinfo_list_dict)


# 借书界面的搜索功能
@app.route('/searchbook', methods=['POST', 'GET'])
@admin_login_req
def searchbook():
    keywords = request.args.get('keywords')
    # 根据书名搜
    book_list = Book.query.filter(Book.name.like("%" + keywords + "%") if keywords is not None else ""
                                  ).all()
    # 根据isbn搜
    if not book_list:
        book_list = Book.query.filter(Book.isbn.like("%" + keywords + "%") if keywords is not None else ""
                                      ).all()
    # 根据作者搜
    if not book_list:
        book_list = Book.query.filter(Book.author.like("%" + keywords + "%") if keywords is not None else ""
                                      ).all()
    # 根据出版社搜
    if not book_list:
        book_list = Book.query.filter(Book.publisher.like("%" + keywords + "%") if keywords is not None else ""
                                      ).all()
    print('book_list', book_list)
    book_list_dict = []
    for book in book_list:
        print(book.isbn)
        book_list_dict.append(
            {
                'isbn': book.isbn,
                'name': book.name,
                'author': book.author,
                'publisher': book.publisher,
                'pub_date': book.pub_date
            }
        )
    # print(book_list_dict)
    # book_list_json = json.dumps(book_list_dict)

    # return book_list_json
    return render_template('borrowbook.html', books=book_list_dict)


# 在预约界面查询读者
@app.route('/searchreader', methods=['POST', 'GET'])
@admin_login_req
def searchreader():
    keywords = request.args.get('keywords')
    # 根据姓名搜
    reader_list = Reader.query.filter(Reader.name.like("%" + keywords + "%") if keywords is not None else ""
                                      ).all()
    # 根据id搜
    if not reader_list:
        reader_list = Reader.query.filter(Reader.id.like("%" + keywords + "%") if keywords is not None else ""
                                          ).all()

    print('reader_list', reader_list)
    reader_list_dict = []
    for reader in reader_list:
        print(reader.id)
        reader_list_dict.append(
            {
                'id': reader.id,
                'name': reader.name,
                'phone': reader.phone,
                'Email': reader.Email
            }
        )
    # print(book_list_dict)
    # book_list_json = json.dumps(book_list_dict)

    # return book_list_json
    return render_template('orderbook.html', readers=reader_list_dict)


# 预约界面(主要显示读者的预约信息)
@app.route('/orderbook')
@admin_login_req
def orderbook():
    id = request.args.get('id')
    if id == None:
        # 显示所有读者信息
        readers = Reader.query.all()
        print('readers', readers)
        reader_list_dict = []
        for reader in readers:
            print(reader.id)
            reader_list_dict.append(
                {
                    'id': reader.id,
                    'name': reader.name,
                    'phone': reader.phone,
                    'Email': reader.Email
                }
            )
        return render_template('orderbook.html', readers=reader_list_dict)
    else:
        # 显示选定id读者的预约信息
        print("!!")
        reserves = ReserveInfo.query.filter(ReserveInfo.reader_id == id).all()
        reserveinfo_list_dict = []
        for reserve in reserves:
            reserveinfo_list_dict.append(
                {
                    'reader_id': reserve.reader_id,
                    'isbn': reserve.isbn,
                    'reserve_date': reserve.reserve_date,
                    'status': reserve.status,
                    'agent_id': reserve.agent_id,
                }
            )
        return render_template('orderbook.html', readerinfo=reserveinfo_list_dict)
    return render_template('orderbook.html')


# 查询isbn是否有可借的书本
@app.route('/is_book_avalable', methods=['POST'])
def is_book_avalable():
    isbn = request.form.get('isbn')
    print(isbn)
    try:
        bookinfo = BookInfo.query.filter(BookInfo.isbn == isbn, BookInfo.status == "未借出").all()
        print(bookinfo)
        if not bookinfo:
            bookinfo = BookInfo.query.filter(BookInfo.isbn == isbn, BookInfo.status == "已借出").all()
            if not bookinfo:
                return json.dumps({"state": 201, "msg": "该书不可外借"})
            return json.dumps({"state": 202, "msg": "可预约！"})
        else:
            return json.dumps({"state": 203, "msg": "此书有空闲，无需预约！"})
    except Exception as e:
        print(e)
        return json.dumps({"message": e})


# 预约操作
@app.route('/doreservebook', methods=['POST'])
def doreservebook():
    isbn = request.form.get('isbn')
    id = request.form.get('id')
    print("genge")
    print(isbn + ',' + id)
    reader_id = Reader.query.filter_by(id=id).first()
    if not reader_id:
        return json.dumps({"state": 106, "msg": "没有这个id!"})
    # 查询是否已有预约记录
    have_reserve = ReserveInfo.query.filter(ReserveInfo.reader_id == id, ReserveInfo.isbn == isbn,
                                            ReserveInfo.status != "已完成").all()
    if have_reserve:
        return json.dumps({"state": 204, "msg": "您已预约该书！"})
    # 插入预约信息(reader_id,isbn,agent_id)
    user_id = session['user_id']  # session中取经办人id
    # print(user_id)
    reserInfo = ReserveInfo()
    reserInfo.reader_id = id
    reserInfo.isbn = isbn
    reserInfo.reserve_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前时间 Y-m-d
    reserInfo.status = "等待"
    reserInfo.agent_id = user_id
    """
    reserve_date需讨论
    """
    try:
        db.session.add(reserInfo)
        db.session.commit()
        return json.dumps({"state": 205, "msg": "预约成功"})
    except Exception as e:
        return json.dumps({"state": 206, "msg": e})


# 还书界面
@app.route('/returnbook', methods=['POST', 'GET'])
@admin_login_req
def returnbook():
    id = request.args.get('id')
    if not id:
        # 显示所有读者信息
        readers = Reader.query.all()
        # print('readers', readers)
        reader_list_dict = []
        for reader in readers:
            # print(reader.id)
            reader_list_dict.append(
                {
                    'id': reader.id,
                    'name': reader.name,
                    'phone': reader.phone,
                    'Email': reader.Email
                }
            )
        print("returnbook")
        return render_template('returnbook.html', readers=reader_list_dict)
    else:
        # 显示选定id读者的还书
        # print("!!")
        borrows = BorrowInfo.query.filter(BorrowInfo.reader_id == id).all()
        borrowinfo_list_dict = []
        for borrow in borrows:
            # print(borrow.book.book.name)
            print("查询fine")
            fine = fine_of_returnbook(borrow.due_date)
            borrowinfo_list_dict.append(
                {
                    'reader_id': borrow.reader_id,
                    'book_id': borrow.book_id,
                    'book_name': borrow.book.book.name,
                    'borrow_date': borrow.borrow_date.strftime("%Y-%m-%d"),
                    'due_date': borrow.due_date.strftime("%Y-%m-%d"),
                    'fine': fine,
                    'return_date': borrow.return_date,
                    'agent_id': borrow.agent_id
                }
            )
        return render_template('returnbook.html', readerinfo=borrowinfo_list_dict)
    return render_template('returnbook.html')


# 还书操作
@app.route('/doreturnbook', methods=['POST', 'GET'])
def doreturnbook():
    reader_id = request.form.get('reader_id')
    book_id = request.form.get('book_id')
    borrow_date = request.form.get('borrow_date')
    due_date = request.form.get('due_date')
    # print(isbn+','+id)
    borrowinfo = BorrowInfo.query.filter(BorrowInfo.reader_id == reader_id, BorrowInfo.book_id == book_id
                                         , BorrowInfo.borrow_date == borrow_date).first()
    reserveinfo = ReserveInfo.query.filter(ReserveInfo.isbn == borrowinfo.book.isbn).first()

    # 有人预约
    if reserveinfo:
        print("有预约")
        try:
            # bookinfo:已借出->已预约
            bookinfo = BookInfo.query.filter(BookInfo.book_id == book_id).first()
            bookinfo.status = "已预约"
            db.session.commit()
            # 添加return_date
            borrowinfo = BorrowInfo.query.filter(BorrowInfo.reader_id == reader_id, BorrowInfo.book_id == book_id
                                                 , BorrowInfo.borrow_date == borrow_date).first()
            borrowinfo.return_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前时间 Y-m-d
            db.session.commit()
            # reserveinfo: 等待->已通知
            reserveinfo = ReserveInfo.query.filter(ReserveInfo.isbn == borrowinfo.book.isbn).first()
            reserveinfo.status = "已通知"
            # 添加inform_date
            reserveinfo.inform_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前时间 Y-m-d
            db.session.commit()
            # 发邮件通知
            reserve_email(reserveinfo.reader_id, book_id)
            return jsonify({"state": 208, "msg": "还书成功"})

        except Exception as e:
            return jsonify({"state": 209, "msg": e})

    # 无人预约，直接归还
    else:
        print("无预约")
        try:
            # bookinfo:已借出->未借出
            bookinfo = BookInfo.query.filter(BookInfo.book_id == book_id).first()
            print(book_id)
            bookinfo.status = "未借出"
            db.session.commit()
            # 添加return_date
            borrowinfo = BorrowInfo.query.filter(BorrowInfo.reader_id == reader_id, BorrowInfo.book_id == book_id
                                                 , BorrowInfo.borrow_date == borrow_date).first()
            borrowinfo.return_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前时间 Y-m-d
            db.session.commit()
            return jsonify({"state": 208, "msg": "还书成功"})

        except Exception as e:
            return jsonify({"state": 208, "msg": e})
    return jsonify({"state": 209, "msg": "e"})


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
        return json.dumps({"state": 200, "message": "增加成功！"})
    except Exception as e:
        print(e)
        return json.dumps({"state": 0, "message": e})


# 删除书本
@app.route('/del_bookinfo', methods=['POST'])
def del_bookinfo():
    """
    使用 request.form.get获取json中的数据，并向数据库删除书本数据。
    :return:返回格式为json格式，若成功则返回status为200，和对应的提示信息，失败则返回status为0。
    """
    try:
        isbn = request.form.get('isbn')
        book_ids = json.loads(request.form.get('book_id'))
        for book_id in book_ids:
            print(book_id)
            book = BookInfo.query.filter(BookInfo.book_id == book_id).first()
            print(book)
            if book.status == "已借出" or book.status == "已预约":
                return json.dumps({"state": -1, "message": "该书已经借出或被预约，无法删除！"})
            if len(BorrowInfo.query.filter(BorrowInfo.book_id == book_id).all()):
                return json.dumps({"state": -2, "message": "尚存在该书的借阅记录，无法删除！"})
            db.session.delete(book)
        db.session.commit()
        return json.dumps({"state": 200, "message": "删除成功！"})
    except Exception as e:
        print(e)
        return json.dumps({"state": 0, "message": e})


# 添加书目
@app.route('/add_bookisbn', methods=['POST'])
def add_bookisbn():
    try:
        isbn = request.form.get('isbn')
        author = request.form.get('author')
        bookname = request.form.get('bookname')
        publisher = request.form.get('publisher')
        publish_date = request.form.get('publish_date')
        agent_id = request.form.get('agent_id')
        book = Book()
        book.isbn = isbn
        book.name = bookname
        book.author = author
        book.agent_id = agent_id
        book.amount = 0
        book.publisher = publisher
        book.pub_date = publish_date
        db.session.add(book)
        db.session.commit()
        return json.dumps({"state": 200, "message": "添加成功！"})
    except Exception as e:
        print(e)
        return json.dumps({"state": 0, "message": e})
