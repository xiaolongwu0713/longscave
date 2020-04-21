import pymysql
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.admin import bp
from app.alipay.forms import queryorderform
from app.alipay.routes import init_alipay_cfg
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
from flask_login import current_user, login_required
from flask_user import roles_required


@bp.route('/', methods=['GET', 'POST'])
@login_required
#Flask_User and Flask_Login not working togather properly
#@roles_required('Admin')
def index():
    #flash(current_user.username)
    form = queryorderform()
    if form.validate_on_submit():
        trade_number = form.order_number.data
        env = form.env.data
        result = init_alipay_cfg(env).api_alipay_trade_query(out_trade_no=trade_number)
        return render_template('admin/index.html',  form=form, result=result)
    return render_template('admin/index.html', form=form)
    # return '<title>我的第一个 HTML 页面</title>'


@bp.route('/aboutme', methods=['GET', 'POST'])
def aboutme():
    # flash('jump to main')
    # flash(current_user.username)
    return render_template('/admin/aboutme.html')


@bp.route('/hireme', methods=['GET', 'POST'])
def hireme():
    # flash('jump to main')
    # flash(current_user.username)
    return render_template('/admin/hireme.html')
    # return '<title>我的第一个 HTML 页面</title>'
    # return redirect(url_for('default.explore'))


@bp.route('/course', methods=['GET', 'POST'])
def course():
    # flash('jump to main')
    # flash(current_user.username)
    return render_template('/admin/course.html')


# query table data against mysql through sqlalchemy
@bp.route('/user_admin', methods=['GET', 'POST'])
def user_admin():
    env_name = request.args.get('env_name')
    #flash('prd_env captured')
    page = request.args.get('page', 1, type=int)
    rows = User.query.order_by(User.id.asc()).paginate(
        page, current_app.config['ROWS_PER_PAGE'], False)
    next_url = url_for('admin.user_admin', page=rows.next_num, env_name='prd_env') \
        if rows.has_next else None
    prev_url = url_for('admin.user_admin', page=rows.prev_num, env_name='prd_env') \
        if rows.has_prev else None
    return render_template('admin/userTable.html', env_name=env_name,
                           rows=rows.items, next_url=next_url,
                           prev_url=prev_url)


# query table data against mysql directly, no sqlalchemy
@bp.route('/add_user', methods=['GET','POST'])
def add_user():
    # uniqueId = request.form['uniqueid']
    name = request.form['username']
    password = generate_password_hash(request.form['password'])
    email = request.form['email']
    about_me = request.form['about_me']
    # flash(uniqueId + name + email + address + phone)

    # update database
    mysqlconn = pymysql.connect(
        host='localhost',
        user='longscave',
        password='xiaowu',
        db='longscave',
        cursorclass=pymysql.cursors.DictCursor)
    with mysqlconn.cursor() as mysqlcursor:
        sql = "insert into user (username, password_hash, email, about_me) values (%s, %s, %s, %s);"
        #flash ("inserting" + name)
        try:
            mysqlcursor.execute(sql, (name, password, email, about_me))
            mysqlconn.commit()
            #flash("inserting")
        except:
            flash("rollbacking")
            mysqlconn.rollback()
        finally:
            #flash("close mysql connection")
            mysqlconn.close()
    return jsonify('success')


# query table data against mysql directly, no sqlalchemy
@bp.route('/edituser', methods=['GET', 'POST'])
def edituser():
    uniqueid = request.form['uniqueid']
    name = request.form['username']
    email = request.form['email']
    about_me = request.form['about_me']
    last_seen = request.form['last_seen']
    # flash("message:" + uniqueId + ipaddress + connectionstr + description + backupdesc + jobs)

    mysqlconn = pymysql.connect(
        host='localhost',
        user='longscave',
        password='xiaowu',
        db='longscave',
        cursorclass=pymysql.cursors.DictCursor)
    sql = "update user set username=%s, email=%s, about_me=%s where id=%s;"
    try:
        mysqlconn.cursor().execute(sql, (name, email, about_me, uniqueid))
        mysqlconn.commit()
    except:
        flash("rollbacking")
        mysqlconn.rollback()
    finally:
        # flash("close mysql connection")
        mysqlconn.close()
    return jsonify('success')


# query table data against mysql directly, no sqlalchemy
@bp.route('/deluser', methods=['GET','POST'])
def deluser():
    uniqueid = request.form['uniqueid']
    mysqlconn = pymysql.connect(
        host='localhost',
        user='longscave',
        password='xiaowu',
        db='longscave',
        cursorclass=pymysql.cursors.DictCursor)
    with mysqlconn.cursor() as mysqlcursor:
        sql = "delete from user where id = %s;"
        #flash (uniqueId)
        mysqlcursor.execute(sql,(uniqueid))
        mysqlconn.commit()
        #flash("deleted")
        mysqlconn.close()
    return jsonify('success')


# online tool to check order status
@bp.route('/query_alipay_order', methods=['GET', 'POST'])
def query_alipay_order():
    form = queryorderform()
    if form.validate_on_submit():
        trade_number = form.order_number.data
        env = form.env.data
        result = init_alipay_cfg(env).api_alipay_trade_query(out_trade_no=trade_number)
        return render_template('/alipay/queryorder.html',  form=form, result=result)
    return render_template('/alipay/queryorder.html',  form=form)
