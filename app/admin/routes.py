from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.admin import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
from flask_login import current_user, login_required


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    # flash('jump to main')
    #flash(current_user.username)
    return render_template('admin/index.html')
    # return '<title>我的第一个 HTML 页面</title>'
    # return redirect(url_for('default.explore'))


# query table data against mysql through sqlalchemy
@bp.route('/user_admin', methods=['GET', 'POST'])
def user_admin():
    env_name = request.args.get('env_name')
    #flash('prd_env captured')
    page = request.args.get('page', 1, type=int)
    rows = User.query.order_by(User.id.desc()).paginate(
        page, current_app.config['ROWS_PER_PAGE'], False)
    next_url = url_for('admin.user_admin', page=rows.next_num, env_name='prd_env') \
        if rows.has_next else None
    prev_url = url_for('admin.user_admin', page=rows.prev_num, env_name='prd_env') \
        if rows.has_prev else None
    return render_template('admin/userTable.html', env_name=env_name,
                           rows=rows.items, next_url=next_url,
                           prev_url=prev_url)
