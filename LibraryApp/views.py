# 定义视图
from LibraryApp import app

from flask import render_template,redirect,sessions,url_for
from LibraryApp.models import *
import datetime
import os


@app.route('/')
def index():
    return "<h1>欢迎来到主页！llxnb</h1>"