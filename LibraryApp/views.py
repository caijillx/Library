# 定义视图
from LibraryApp import app

from flask import render_template, redirect, session, url_for, flash, request,jsonify
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

@app.route('/borrowbook',methods=['POST','GET'])
@admin_login_req
def borrowbook():
    if request.method == 'GET': #处理get请求
        bookisbn = request.args.get('bookisbn')
        print('isbn=', bookisbn)
        if bookisbn == None:    #isbn为空，则显示所有书的信息
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

            #return book_list_json
            return render_template('borrowbook.html',books=book_list_dict)
        book_info = BookInfo.query.filter_by(isbn=bookisbn).all() # isbn不为空，返回具体的书本状态
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
    else:   #处理post请求
        book_id = request.form.get('book_id')
        isbn = request.form.get('isbn')
        id = request.form.get('id')
        user_id = session['user_id'] #session中取经办人id
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
        print("book_id:"+book_id)
        print("isbn:"+isbn)
        print("id:"+id)
        print("user_id:"+user_id)
        reade_id = Reader.query.filter_by(id=id).first()
        if reade_id != None:
            #插入借书记录
            borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前时间 Y-m-d
            due_date = (datetime.datetime.now() + datetime.timedelta(days=60)).strftime("%Y-%m-%d")  # 60天后
            # borroInfo = BorrowInfo(reader_id=id,book_id=book_id,borrow_date=borrow_date,due_date=due_date,agent_id=user_id)
            # db.session.add(borroInfo)
            # db.session.commit()
            # 上面的借书记录插入数据库写不通！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
            # 除了插入借书记录还需要更改书的状态
            # 所需数据已给出：isbn/book_id
            try:
                borroInfo = BorrowInfo()
                borroInfo.reader_id = id
                borroInfo.book_id = book_id
                borroInfo.borrow_date = borrow_date
                #borroInfo.borrow_date = "2020-05-18"
                borroInfo.due_date = due_date
                borroInfo.agent_id = user_id
                db.session.add(borroInfo)
                db.session.commit()
                bookInfo = BookInfo.query.filter(BookInfo.book_id == book_id).first()
                bookInfo.status = "已借出"
                db.session.commit()
                print("book_status change success")
                return jsonify({"success": 1001, "msg": "借阅成功"})#由borrowbook的ajax接受，弹窗显示
            except Exception as e:
                print(e)
                return jsonify({"error": 200, "msg": e})#由borrowbook的ajax接受，弹窗显示

        else:
            #id在数据库中找不到
            return jsonify({"error": 201, "msg": "没有这个id!"})

        # return render_template('borrowbook.html', bookinfo=bookinfo_list_dict)

#借书界面的搜索功能
@app.route('/searchbook',methods=['POST','GET'])
@admin_login_req
def searchbook():
    keywords = request.args.get('keywords')
    #根据书名搜
    book_list = Book.query.filter(Book.name.like("%"+keywords+"%") if keywords is not None else ""
                                  ).all()
    #根据isbn搜
    if not book_list:
        book_list = Book.query.filter(Book.isbn.like("%" + keywords + "%") if keywords is not None else ""
                                      ).all()
    #根据作者搜
    if not book_list:
        book_list = Book.query.filter(Book.author.like("%" + keywords + "%") if keywords is not None else ""
                                      ).all()
    #根据出版社搜
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

# 预约界面
@app.route('/orderbook')
@admin_login_req
def orderbook():
    id = request.args.get('id')
    if id == None:
        #显示所有读者信息
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
        #显示选定id读者的预约信息
        print("!!")
        reserves = ReserveInfo.query.filter(ReserveInfo.reader_id==id).all()
        reserveinfo_list_dict = []
        for reserve in reserves:
            reserveinfo_list_dict.append(
                {
                    'reader_id': reserve.readerid,
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
    print(isbn+','+id)
    """
    还没做
    """
    return json.dumps({"state": 204, "msg": "预约成功"})

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
