# coding=utf-8
import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
# 告诉flask login 哪个视图允许用户登录,这里给出的是视图函数login，见views.login
lm.login_view = 'login'
# Flask-OpenID 扩展需要一个存储文件的临时文件夹的路径。对此，我们提供了一个 tmp 文件夹的路径。
oid = OpenID(app, os.path.join(basedir, 'tmp'))

from app import views, models