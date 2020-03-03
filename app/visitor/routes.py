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
from app.models import User, Post, MessageToMe,Article
from app.translate import translate
from app.visitor import bp
from app.main.forms import CKarticle


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
# @login_required
def index():
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter(Article.id != 3).order_by(Article.timestamp.desc()).paginate(
        page, current_app.config['ARTICLES_PER_PAGE'], False)
    next_url = url_for('.index', page=articles.next_num) \
        if articles.has_next else None
    prev_url = url_for('.index', page=articles.prev_num) \
        if articles.has_prev else None
    return render_template('/visitor/visitor.html', title=_('Explore'),
                           articles=articles.items, next_url=next_url,prev_url=prev_url)


@bp.route('/articles', methods=['GET', 'POST'])
# @login_required
def article():
    ckarticle = CKarticle()
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.id.desc()).paginate(
        page, current_app.config['ARTICLE_PER_PAGE'], False)
    next_url = url_for('.article', page=articles.next_num) \
        if articles.has_next else None
    prev_url = url_for('.article', page=articles.prev_num) \
        if articles.has_prev else None
    return render_template('/visitor/articles.html', title=_('Explore'),form=ckarticle,
                           articles=articles.items, next_url=next_url,prev_url=prev_url)


# visitor send message in modal. This function receive message and store in db
@bp.route('/sendMeMessageModal', methods=['GET', 'POST'])
def sendMeMessageModal():
    # uniqueId = request.form['uniqueid']
    name = request.form['name']
    location = request.form['location']
    tel = request.form['tel']
    email = request.form['email']
    msg = request.form['msg']
    #flash(name + location + email + tel + msg)
    message = MessageToMe(username=name, location=location, tel=tel, email=email, msg=msg)
    db.session.add(message)
    db.session.commit()
    return jsonify('success')
