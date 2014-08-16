# -*- coding: utf-8 -*-
from __future__ import absolute_import
from haxorbb import app
from flask import render_template, redirect, send_from_directory, request


@app.route('/')
def start():
    return render_template("index.html")


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
def page_not_found():
    return '404 Is full of goats', 404