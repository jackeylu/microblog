# coding=utf-8
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm
from models import User, ROLE_USER, ROLE_ADMIN


# lm是在app.__init__.py中声明的LoginManager类的实例
@lm.user_loader
def load_user(id):
    # 从数据库加载用户。这个函数将会被 Flask-Login 使用.
    # 在 Flask-Login 中的用户 ids 永远是 unicode 字符串，
    # 因此在我们把 入参中的字符串id 发送给 Flask-SQLAlchemy 之前，把 id 转成整型是必须的，否则会报错！
    return User.query.get(int(id))

# 任何使用了 before_request 装饰器的函数在接收请求之前都会运行。
# 因此这就是我们设置我们 g.user 的地方
@app.before_request
def before_request():
    # 全局变量 current_user 是被 Flask-Login 设置的，
    # 因此我们只需要把它赋给 g.user ，让访问起来更方便。
    # 有了这个，所有请求将会访问到登录用户，即使在模版里。
    g.user = current_user


@app.route('/')
@app.route('/index')
@login_required # 添加了 login_required 装饰器。这确保了这页只被已经登录的用户看到。
def index():
    user = g.user
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,# 把 g.user 传入给模版，代替之前使用的伪造对象。
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
# oid.loginhandle 告诉 Flask-OpenID 这是我们的登录视图函数。
@oid.loginhandler
def login():
    # 检查 g.user 是否被设置成一个认证用户，如果是的话将会被重定向到首页
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    """

    :param resp: resp 参数传入给 after_login 函数，它包含了从 OpenID 提供商返回来的信息。
    :return:
    """
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    # 从数据库中搜索邮箱地址。如果邮箱地址不在数据库中，
    # 我们认为是一个新用户，因为我们会添加一个新用户到数据库
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    # 注册这个有效的登录，我们调用 Flask-Login 的 login_user 函数
    login_user(user, remember=remember_me)
    # 如果在 next 页没有提供的情况下，我们会重定向到首页，否则会重定向到 next 页。
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    # 登出的功能
    logout_user()
    return redirect(url_for('index'))
