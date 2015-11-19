# -*- coding: utf-8 -*-
from . import front_page
from .. import db
from .forms import Edit
from ..models import Articles
from ..utilities.utils import Utilities
from datetime import datetime
from flask import render_template, redirect, url_for, g, current_app
from flask.ext.login import current_user, login_required
import os
from scandir import scandir


def get_file_list(username):
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', username)
    if not os.path.isdir(file_path):
        os.makedirs(file_path)
    file_list = [{'file': f.name, 'url': url_for(
        'media', filename='users/{}/{}'.format(username, f.name)
    )} for f in scandir(file_path)]
    return file_list


@front_page.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.seen()


@front_page.route('/', defaults={'article': None})
@front_page.route('/article/<article>')
def home_page(article):
    if article:
        articles = [Articles.query.filter_by(slug=article).first()]
    else:
        articles = [article for article in Articles.query.order_by(Articles.datestamp.desc()).all()]
    return render_template("front_page/index.html", articles=articles)


@front_page.route('/new_article', methods=['GET', 'POST'])
@login_required
def new_article():
    form = Edit()
    article = Articles()
    if form.validate_on_submit():
        article.content = form.body.data
        article.title = form.title.data
        article.slug = Utilities.generate_slug(form.title.data)
        article.visibility = form.visibility.data
        article.author_id = current_user.id
        article.datestamp = datetime.utcnow()
        db.session.add(article)
        try:
            db.session.commit()
        except Exception as e:
            print e
            db.session.rollback()
        return redirect(url_for('front_page.home_page'))
    file_list = get_file_list(current_user.username)
    if file_list:
        g.file_list = file_list
    return render_template('front_page/editor_.html', user=current_user, form=form)


@front_page.route('/article/<articleid>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(articleid):
    file_list = get_file_list(current_user.username)
    article = Articles.query.filter_by(id=articleid).first()
    form = Edit()
    if form.validate_on_submit():
        article.content = form.body.data
        article.title = form.title.data
        article.visibility = form.visibility.data
        db.session.add(article)
        try:
            db.session.commit()
        except Exception as e:
            print e
            db.session.rollback()
        return redirect(url_for('front_page.home_page'))
    g.articleid = articleid
    if file_list:
        g.file_list = file_list
    form.title.data = article.title
    form.body.data = article.content
    form.visibility.data = article.visibility
    return render_template("front_page/edit.html", user=current_user, form=form)


@front_page.route('/article/<articleid>/delete', methods=['GET'])
@login_required
def delete_article(articleid):
    to_remove = Articles.query.filter_by(id=articleid).first()
    db.session.delete(to_remove)
    try:
        db.session.commit()
    except Exception as e:
        print e
        db.session.rollback()
    return redirect(url_for('front_page.home_page'))


@front_page.route('/oldnews/', defaults={'page': 'oldnews'})
@front_page.route('/page=<page>/')
def other_page(page):
    if page == "oldnews":
        return redirect('http://www.sabotage2.com/index.php?page=oldnews', 301)
    else:
        return render_template("error.html")



