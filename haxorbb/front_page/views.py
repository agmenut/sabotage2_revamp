# -*- coding: utf-8 -*-
from . import front_page
from ..models import Articles
from flask import render_template, redirect
from flask.ext.login import current_user


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


@front_page.route('/oldnews/', defaults={'page': 'oldnews'})
@front_page.route('/page=<page>/')
def other_page(page):
    if page == "oldnews":
        return redirect('http://www.sabotage2.com/index.php?page=oldnews', 301)
    else:
        return render_template("error.html")



