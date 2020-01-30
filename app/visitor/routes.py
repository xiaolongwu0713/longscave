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
from app.visitor import bp
# from longscave import app


@bp.route('/')
#@login_required
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('/visitor/visitor.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@bp.route('/hireme', methods=['GET', 'POST'])
def hireme():
    # flash('jump to main')
    #flash(current_user.username)
    return render_template('/visitor/hireme.html')
    # return '<title>我的第一个 HTML 页面</title>'
    # return redirect(url_for('default.explore'))


@bp.route('/aboutme', methods=['GET', 'POST'])
def aboutme():
    # flash('jump to main')
    #flash(current_user.username)
    return render_template('/visitor/aboutme.html')


@bp.route('/course', methods=['GET', 'POST'])
def course():
    # flash('jump to main')
    #flash(current_user.username)
    return render_template('/visitor/course.html')
