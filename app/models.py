# coding=utf-8
# 从项目自身app.__init__.py中import db这个变量
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    # 一个新的字段称为 posts，它是被构建成一个 db.relationship 字段。这并不是一个实际的数据库字段
    # 对于一个一对多的关系，db.relationship 字段通常是定义在“一”这一边。在这种关系下，我们得到一个 user.posts 成员，它给出一个用户所有的 blog
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.nickname


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    # user_id 字段初始化成外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post %r>' % self.body
