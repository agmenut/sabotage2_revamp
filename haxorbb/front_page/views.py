# -*- coding: utf-8 -*-
from . import front_page
from ..models import Articles
from flask import render_template, redirect, send_from_directory, request, current_app
from flask.ext.login import login_required, current_user


@front_page.route('/')
def home_page():
    articles = []
    results = Articles.query.order_by(Articles.datestamp.desc()).all()
    for row in results:
        articles.append(row)
    return render_template("front_page/index.html", articles=articles)


@front_page.route('/article/<article>')
def get_article(article):
    qry = Articles.query.filter_by(slug=article)
    item = qry.one()
    return render_template("front_page/article.html", article=item)


@front_page.route('/oldnews/', defaults={'page': 'oldnews'})
@front_page.route('/page=<page>/')
def other_page(page):
    if page == "oldnews":
        return redirect('http://www.sabotage2.com/index.php?page=oldnews', 301)
    else:
        return render_template("error.html")



