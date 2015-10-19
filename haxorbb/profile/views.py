# -*- coding: utf-8 -*-
from . import profile
from .. import db
from flask import (url_for, request, redirect, render_template)
from ..models import User
from .forms import Profile
from flask.ext.login import login_required, current_user
from datetime import datetime, timedelta


@profile.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.seen()


@profile.route('/view/<username>')
def view(username):
    user = User.query.filter_by(username=username).first()
    if user:
        try:
            days = datetime.now() - user.registration_date
            user.posts_per_day = user.posts / float(days.days)
        except (ValueError, TypeError, AttributeError):
            user.posts_per_day = 0
        return render_template('profile/profile.html', user=user)
    else:
        return redirect('front_page.home_page')


@profile.route('/view/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if current_user.username != username and not current_user.is_administrator:
        return redirect(url_for('front_page.home_page'))
    form = Profile()
    user = User.query.filter_by(username=username).first()
    if user.otp:
        tfa_state = True
    else:
        tfa_state = False
    if form.validate_on_submit():
        user.fullname = form.fullname.data
        user.location = form.location.data
        user.avatar_text = form.avatar_text.data
        user.avatar_url = form.avatar_url.data
        db.session.add(user)
        db.session.commit()
    form.fullname.data = user.fullname or None
    form.location.data = user.location or None
    form.avatar_url.data = user.avatar_url or None
    form.avatar_text.data = user.avatar_text or None
    return render_template('profile/edit.html', user=user, form=form, tfa=tfa_state)
