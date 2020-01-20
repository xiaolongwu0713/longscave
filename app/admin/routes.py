from flask import render_template, redirect, url_for, flash, request
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
