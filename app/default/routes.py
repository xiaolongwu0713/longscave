# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, send_from_directory, json
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db, login
# from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate
from app.default import bp
# from longscave import app


@bp.route('/index', methods=['GET', 'POST'])
@bp.route('/', methods=['GET', 'POST'])
def index():
    # flash('jump to main')
    #flash(current_user.username)
    return render_template('default/index.html')
    # return '<title>我的第一个 HTML 页面</title>'
    # return redirect(url_for('default.explore'))



