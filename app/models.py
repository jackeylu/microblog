# coding=utf-8
# 从项目自身app.__init__.py中import db这个变量
from app import db

ROLE_USER = 0
ROLE_ADMIN = 1


# Flask-Login 扩展需要在我们的 User 类中实现一些特定的方法。但是类如何去实现这些方法却没有什么要求。
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    # 一个新的字段称为 posts，它是被构建成一个 db.relationship 字段。这并不是一个实际的数据库字段
    # 对于一个一对多的关系，db.relationship 字段通常是定义在“一”这一边。
    # 在这种关系下，我们得到一个 user.posts 成员，它给出一个用户所有的 blog
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # is_authenticated 方法有一个具有迷惑性的名称。
    # 一般而言，这个方法应该只返回 True，除非表示用户的对象因为某些原因不允许被认证。
    def is_authenticated(self):
        return True

    # is_active 方法应该返回 True，除非是用户是无效的，比如因为他们的账号是被禁止。
    def is_active(self):
        return True

    # is_anonymous 方法应该返回 True，除非是伪造的用户不允许登录系统。
    def is_anonymous(self):
        return False

    def get_id(self):
        # 返回一个用户唯一的标识符，以 unicode 格式。我们使用数据库生成的唯一的 id。
        # 需要注意地是在 Python 2 和 3 之间由于 unicode 处理的方式的不同我们提供了相应的方式。
        try:
            return unicode(self.id) # Python 2
        except NameError:
            return str(self.id) # Python 3

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
