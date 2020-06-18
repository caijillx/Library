from LibraryApp import app
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from LibraryApp.models import *
from LibraryApp.func import *

scheduler = APScheduler()
scheduler.init_app(app)
scheduler = BackgroundScheduler()
# 间隔30秒钟执行一次
scheduler.add_job(timer_task, 'interval', seconds=5, args=[BorrowInfo])
# 这里的调度任务是独立的一个线程
scheduler.start()
