# -*- coding: utf-8 -*-
from . import forum
from flask import render_template, g
from flask.ext.login import current_user
from .. import db
from ..models import Forums, Threads, Posts, User
from .forms import NewThread
from datetime import datetime


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
    print threads
    g.threads = threads
    return render_template('forum/thread_table.html', forum_id=forum_id)


@forum.route('/<int:forum_id>/new_thread/', methods=['GET', 'POST'])
def new_thread(forum_id):
    g.user = current_user
    form = NewThread()
    if form.validate_on_submit():
        thread = Threads()
        thread.title = form.title.data
        thread.fk_forum = forum_id
        thread.last_post = datetime.utcnow()
        thread.thread_author = current_user.id
        thread_id = thread.post()

        post = Posts()
        post.body = form.body.data
        post.timestamp = thread.last_post
        post.poster = current_user.id
        post.thread = thread_id
        post.post()

    return render_template('forum/new_thread.html', form=form)
