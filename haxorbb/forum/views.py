# -*- coding: utf-8 -*-
from . import forum
from flask import render_template, g
from flask.ext.login import current_user
from .. import db
from ..models import Forums, Threads, Posts, User


@forum.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.seen()


@forum.route('/')
def forum_index():
    g.user = current_user
    fora = [f for f in Forums.query.all()]
    return render_template('forum/index.html', fora=fora)


@forum.route('/<int:forum_id>')
def show_forum(forum_id):
    g.user = current_user
    title = Forums.query.with_entities(Forums.title).filter_by(id=forum_id).one()
    g.title_ = title[0]
    threads = Threads.query.order_by(Threads.last_post.desc()).all()
    g.threads = threads

    return render_template('forum/thread_table.html')
