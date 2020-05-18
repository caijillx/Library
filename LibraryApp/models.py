# 定义模型
# coding: utf-8
from datetime import datetime
from LibraryApp import db

class Admin(db.Model):
    __tablename__ = 'admin'

    user_id = db.Column(db.String(30), primary_key=True)
    user_name = db.Column(db.String(30))
    pswd = db.Column(db.String(30))


    def check_pwd(self,pwd):
        return self.pswd == pwd

class Reader(db.Model):
    __tablename__ = 'reader'

    id = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(30))
    phone = db.Column(db.String(30))
    Email = db.Column(db.String(30))


class Book(db.Model):
    __tablename__ = 'book'

    isbn = db.Column(db.String(30), primary_key=True)
    name = db.Column(db.String(30))
    author = db.Column(db.String(30))
    publisher = db.Column(db.String(30))
    pub_date = db.Column(db.String(30))
    amount = db.Column(db.Integer)
    agent_id = db.Column(db.ForeignKey('admin.user_id'), index=True)

    agent = db.relationship('Admin')


class BookInfo(db.Model):
    __tablename__ = 'book_info'

    book_id = db.Column(db.String(30), primary_key=True)
    isbn = db.Column(db.ForeignKey('book.isbn'), index=True)
    location = db.Column(db.String(30))
    status = db.Column(db.String(30))
    agent_id = db.Column(db.ForeignKey('admin.user_id'), index=True)

    agent = db.relationship('Admin')
    book = db.relationship('Book')


class ReserveInfo(db.Model):
    __tablename__ = 'reserve_info'

    reader_id = db.Column(db.ForeignKey('reader.id'), primary_key=True, nullable=False)
    isbn = db.Column(db.ForeignKey('book.isbn'), primary_key=True, nullable=False, index=True)
    reserve_date = db.Column(db.String, primary_key=True, nullable=False)
    status = db.Column(db.String(30))
    agent_id = db.Column(db.ForeignKey('admin.user_id'), index=True)

    agent = db.relationship('Admin')
    book = db.relationship('Book')
    reader = db.relationship('Reader')


class BorrowInfo(db.Model):
    __tablename__ = 'borrow_info'

    reader_id = db.Column(db.ForeignKey('reader.id'), primary_key=True, nullable=False)
    book_id = db.Column(db.ForeignKey('book_info.book_id'), primary_key=True, nullable=False, index=True)
    borrow_date = db.Column(db.String, primary_key=True, nullable=False)
    due_date = db.Column(db.String)
    return_date = db.Column(db.String)
    agent_id = db.Column(db.ForeignKey('admin.user_id'), index=True)

    agent = db.relationship('Admin')
    book = db.relationship('BookInfo')
    reader = db.relationship('Reader')
