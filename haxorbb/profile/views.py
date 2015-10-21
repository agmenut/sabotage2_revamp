# -*- coding: utf-8 -*-
from . import profile
from .. import db
from flask import (current_app, url_for, request, redirect, render_template)
from ..models import User
from .forms import Profile
from flask.ext.login import login_required, current_user
from datetime import datetime, timedelta
import os

try:
    from os import scandir
except ImportError:
    from scandir import scandir


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
    user = User.query.filter_by(username=username).first()
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', user.username)
    form = Profile()
    # Check if the user is using 2FA, and needs to auth.
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
    file_list = [f.stat().st_size for f in scandir(file_path)]
    disk_use = sum(file_list)
    return render_template('profile/edit.html', user=user, form=form, tfa=tfa_state, disk_use=disk_use)


@profile.route('/view/<username>/files', methods=['GET', 'POST'])
@login_required
def manage_files(username):
    filedata = []
    if current_user.username != username and not current_user.is_administrator:
        return redirect(url_for('front_page.home_page'))

    user = User.query.filter_by(username=username).first()
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', user.username)
    if not os.path.isdir(file_path):
        print "Path does not exist"
        os.mkdir(file_path)
    file_list = [{'name': f.name, 'size': f.stat().st_size} for f in scandir(file_path)]
    if file_list:
        for userfile in file_list:
            data = {
                'name': userfile['name'],
                'size': userfile['size'],
                'URL': url_for('media', filename='users/{}/{}'.format(user.username, userfile))
                }
            if user.avatar_url and user.avatar_url.endswith(userfile['name']):
                print "Current avatar"
                data['avatar'] = True
            if user.picture_url and user.picture_url.endswith(userfile['name']):
                data['picture'] = True
            filedata.append(data)
    return render_template('profile/manage_files.html', user=user, filedata=filedata)
