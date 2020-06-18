'''
is_in_library 判断图书馆是否有该书
is_isbn_correct
is_book_id_correct
is_reader_id_correct
book_available 判断该书籍是否有库存
send_email
reserve_email 通知预约读者取书
due_email   催读者还书
timer_task 每天催还有三天到期的读者还书
fine_of_returnbook 还书的罚金计算
encryption 密码加密
'''

from LibraryApp.models import *
from sqlalchemy import and_, or_, not_
import re
import datetime
from hashlib import sha256

# smtplib 用于邮件的发信动作
import smtplib
# email 用于构建邮件内容
from email.mime.text import MIMEText
# 用于构建邮件头
from email.header import Header


def is_in_library(isbn):
    '''
    判断图书馆是否有该书
    :param isbn
    :return: True or False
    '''
    flag = Book.query.filter(Book.isbn == isbn).first()
    return True if flag != None else False


def is_isbn_correct(isbn):
    '''
    ISBN号，大写的"ISBN"开头，格式为'ISBNn-nnn-nnnnn-n'共17为。
    :param isbn
    :return: True代表格式正确，False代表格式错误。1为错误1，
    '''
    if isbn[0:4] != 'ISBN':
        return "未以大写ISBN开头。示例：ISBN7-302-02368-9"
    elif len(isbn) != 17:
        return "长度不正确。示例：ISBN7-302-02368-9"
    else:
        result = re.match(r'ISBN[0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9]-[0-9]', isbn, re.I)
        return False if result == None else True


def is_book_id_correct(book_id):
    '''
    示例：C832.1
    :param isbn
    :return: True代表格式正确，False代表格式错误。
    '''
    if book_id[0] != 'C':
        return "未以大写C开头。示例：C832.1"
    elif len(book_id) != 6:
        return "长度不正确。示例：C832.1"
    else:
        result = re.match(r'C[0-9][0-9][0-9]\.[0-9]', book_id, re.I)
        return False if result == None else True


def is_reader_id_correct(reader_id):
    '''
    判断读者号是否存在
    :param reader_id
    :return: True代表格式正确，False代表格式错误。
    '''
    result = re.match(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]', reader_id, re.I)
    return False if result == None else True


def book_available(isbn):
    '''
    判断该书籍是否有库存
    :param isbn
    :return: book_ids: 图书号的list
    '''
    if is_isbn_correct(isbn) == True:
        if is_in_library(isbn):
            obj = BookInfo.query.filter(and_(BookInfo.isbn == isbn, BookInfo.status == '未借出')).all()
            book_ids = [book.book_id for book in obj]
            return book_ids
        else:
            return None
    else:
        return is_isbn_correct(isbn)


def send_email(to_addr, context):
    '''
    发送邮件
    :param to_addr: 收件人邮箱
    :param context: 邮件内容
    :return:
    '''
    # 发信服务器
    smtp_server = 'smtp.163.com'
    # 发信方的信息：发信邮箱，163邮箱授权码
    from_addr = 'sh26_404@163.com'
    password = 'YKFTAOUJEASSZZDW'

    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
    msg = MIMEText(context, 'plain', 'utf-8')
    # 邮件头信息
    msg['From'] = Header(from_addr)
    msg['To'] = Header(to_addr)
    msg['Subject'] = Header('图书管理系统通知')

    # 开启发信服务，这里使用的是加密传输
    server = smtplib.SMTP_SSL(host=smtp_server)
    server.connect(host=smtp_server, port=465)
    # 登录发信邮箱
    server.login(from_addr, password)
    # 发送邮件
    server.sendmail(from_addr, to_addr, msg.as_string())
    # 关闭服务器
    server.quit()


def reserve_email(reader_id, book_id):
    '''
    发送邮件催预约人取书
    :param reader_id:
    :param book_id:
    :return:
    '''
    from LibraryApp.models import Reader, BookInfo, Book
    if is_reader_id_correct(reader_id) and is_book_id_correct(book_id):
        reader_obj = Reader.query.filter(Reader.id == reader_id).first()
        reader_name = reader_obj.name
        to_addr = reader_obj.Email
        isbn = BookInfo.query.filter(BookInfo.book_id == book_id).first().isbn
        book_name = Book.query.filter(Book.isbn == isbn).first().name
        context = "亲爱的读者{}(读者号：{})您好：\n\n     您预定的图书《{}》({})现已有库存，请即使前往图书馆领取图书。谢谢\n\n校图书管理系统".format(reader_name,
                                                                                                    reader_id,
                                                                                                    book_name,
                                                                                                    isbn)
        print("From reserve_email:\n", context)
        send_email(to_addr, context)

def due_email(reader_id, book_id):
    '''
    发送邮件催借阅人还书
    :param reader_id:
    :param book_id:
    :return:
    '''
    from LibraryApp.models import Reader,BookInfo,Book

    if is_reader_id_correct(reader_id) and is_book_id_correct(book_id):
        reader_obj = Reader.query.filter(Reader.id == reader_id).first()
        reader_name = reader_obj.name
        to_addr = reader_obj.Email
        isbn = BookInfo.query.filter(BookInfo.book_id == book_id).first().isbn
        book_name = Book.query.filter(Book.isbn == isbn).first().name
        context = "亲爱的读者{}(读者号：{})您好：\n\n     您借阅的图书《{}》({})将在3天后到期，请按时前往图书馆归还或续借图书。谢谢\n\n校图书管理系统".format(reader_name,
                                                                                                    reader_id,
                                                                                                    book_name,
                                                                                                    isbn)
        print("From due_email:\n", context)
        send_email(to_addr, context)
    pass


def timer_task(BorrowInfo):
    cur_date = datetime.date.today()  # datetime.date
    borrow_objs = BorrowInfo.query.filter().all()  # list，每项为一个 记录 对象
    for obj in borrow_objs:
        if obj.due_date - cur_date == datetime.timedelta(days=3) and obj.return_date == None:
            due_email(obj.reader_id, obj.book_id)


def fine_of_returnbook(due_date):
    '''
    还书的罚金
    :param due_date:
    :return:
    '''
    now_date = datetime.datetime.now()
    print(now_date,due_date)
    due_date = due_date.strftime("%Y-%m-%d")+" 00:00:00"
    print(due_date)
    due_date = datetime.datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
    deltadate = now_date-due_date
    #print(deltadate.days)
    days = deltadate.days
    if days > 0:
        fine = days*0.3 #罚金，超一天三毛钱
        #print("fine:",fine)
        return fine

    return 0.0 #无罚金


def encryption(password):
    '''

    :param password: str 用户输入的密码
    :return: encrpted_pswd str 加密后的密码
    '''
    pswd = password.encode('utf-8')
    encrpted_pswd = sha256(pswd).hexdigest()
    return encrpted_pswd



