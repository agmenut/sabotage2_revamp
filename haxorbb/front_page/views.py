# -*- coding: utf-8 -*-
from __future__ import absolute_import
from haxorbb import app
from haxorbb.models import Articles
from flask import render_template, redirect, send_from_directory, request


@app.route('/')
def home_page():
    articles = []
    results = Articles.query.all()
    for row in results:
        out = {k.name: getattr(row, k.name) for k in row.__table__.columns}
        if out['has_image']:
            image_data = row.image[0]
            image = {k.name: getattr(image_data, k.name) for k in image_data.__table__.columns}
            image['image_title'] = image.pop('title')
        else:
            image = None
        out.update(image)
        articles.append(out)
    return render_template("index.html", articles=articles)


@app.route('/oldnews/', defaults={'page': 'oldnews'})
@app.route('/page=<page>/')
def other_page(page):
    if page == "oldnews":
        return redirect('http://www.sabotage2.com/index.php?page=oldnews', 301)
    else:
        return 'Page does not exist', 404


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])


@app.errorhandler(404)
def page_not_found(e):
    return '404 Is full of goats', 404