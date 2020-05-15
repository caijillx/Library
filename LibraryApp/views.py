# 定义视图
from LibraryApp import app

from flask import render_template, redirect, session, url_for, flash, request,jsonify
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
                        'name': book.name
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
        id = Reader.query.filter_by(id=id).first()
        if id != None:
            #插入借书记录
            BorrowInfo.query.all()
            borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")  # 当前时间 Y-m-d
            due_date = (datetime.datetime.now() + datetime.timedelta(days=60)).strftime("%Y-%m-%d")  # 60天后
            # borroInfo = BorrowInfo(reader_id=id,book_id=book_id,borrow_date=borrow_date,due_date=due_date,agent_id=user_id)
            # db.session.add(borroInfo)
            # db.session.commit()
            # 上面的借书记录插入数据库写不通！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
            # 除了插入借书记录还需要更改书的状态
            # 所需数据已给出：isbn/book_id
            return jsonify({"success": 1001, "msg": "借阅成功"})#由borrowbook的ajax接受，弹窗显示
        else:
            #id在数据库中找不到
            return jsonify({"error": 201, "msg": "没有这个id!"})

        # return render_template('borrowbook.html', bookinfo=bookinfo_list_dict)





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
