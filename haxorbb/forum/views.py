# -*- coding: utf-8 -*-
from . import forum
from flask import render_template, g, redirect, url_for, flash
from flask.ext.login import current_user
from .. import db
from ..models import Forums, Threads, Posts
from .forms import NewThread, Reply
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
    threads = [t for t in Threads.query.filter_by(fk_forum=forum_id).order_by(Threads.last_post.desc()).all()]
    return render_template('forum/thread_table.html', forum_id=forum_id, threads=threads)


@forum.route('/<int:forum_id>/new_thread/', methods=['GET', 'POST'])
def new_thread(forum_id):
    if current_user.is_anonymous:
        flash("You must be logged in create theads")
        return redirect(url_for('forum.forum_index'))
    g.user = current_user
    form = NewThread()
    if form.validate_on_submit():
        thread = Threads()
        thread.title = form.title.data
        thread.fk_forum = forum_id
        thread.last_post = datetime.utcnow()
        thread.author = current_user.id
        thread_id = thread.post()

        post = Posts()
        post.body = form.body.data
        post.timestamp = thread.last_post
        post.poster = current_user.id
        post.thread = thread_id
        post.post()

        current_user.increment_post_count()

    return render_template('forum/new_thread.html', form=form)


@forum.route('/thread/<int:thread_id>', methods=['GET'])
def view_thread(thread_id):
    Threads.increment_view_count(thread_id)
    g.thread_data = Threads.get_thread_metadata(thread_id)
    g.thread_data['id'] = thread_id
    g.user = current_user
    posts = [p for p in Posts.query.filter(Posts.thread == thread_id).all()]
    return render_template('forum/view_thread.html', posts=posts)


@forum.route('/thread/<int:thread_id>/reply', methods=['GET', 'POST'])
def post_reply(thread_id):
    if current_user.is_anonymous:
        flash("You must be logged in to reply.")
        return redirect(url_for('forum.view_thread', thread_id=thread_id))
    form = Reply()
    g.thread_data = Threads.get_thread_metadata(thread_id)
    g.thread_data['id'] = thread_id
    g.user = current_user
    if form.validate_on_submit():
        post = Posts()
        post.body = form.message.data
        post.timestamp = datetime.utcnow()
        post.poster = current_user.id
        post.thread = thread_id
        post.post()

        current_user.increment_post_count()
        return redirect(url_for('forum.view_thread', thread_id=thread_id))
    return render_template('forum/post_reply.html', form=form)
