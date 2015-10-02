# -*- coding: utf-8 -*-
from __future__ import absolute_import
from haxorbb import app
from haxorbb.models import Articles
from flask import render_template, redirect, send_from_directory, request


@app.route('/')
def home_page():
    articles = []
    results = Articles.query.order_by(Articles.datestamp.desc()).all()
    for row in results:
        articles.append(row)
    return render_template("index.html", articles=articles)


@app.route('/<article>')
def get_article(article):
    qry = Articles.query.filter_by(slug=article)
    item = qry.one()
    return render_template("article.html", article=item)


@app.route('/oldnews/', defaults={'page': 'oldnews'})
@app.route('/page=<page>/')
def other_page(page):
    if page == "oldnews":
        return redirect('http://www.sabotage2.com/index.php?page=oldnews', 301)
    else:
        return render_template("error.html")


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error=e)
