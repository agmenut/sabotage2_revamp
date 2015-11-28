# -*- coding: utf-8 -*-
from . import forum
from flask import render_template, g
from flask.ext.login import current_user, login_required


@forum.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.seen()


@forum.route('/')
@login_required
def forum_index():
    g.user = current_user
    return render_template('forum/index.html')

