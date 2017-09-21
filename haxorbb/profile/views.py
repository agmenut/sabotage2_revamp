# -*- coding: utf-8 -*-
from . import profile
from .. import db
from flask import (current_app, url_for, redirect, render_template, flash, send_file, abort)
from werkzeug.utils import secure_filename
from ..models import User
from .forms import Profile, Upload, Rename, Transload, Signature
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os
from PIL import Image
from io import BytesIO
from ..utilities.utils import generate_thumbnail
import pytz
from requests import get as transload

try:
    from os import scandir
except ImportError:
    from scandir import scandir

ALLOWED_EXTENSIONS = ['png', 'jpg', 'gif', 'jpeg']


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
            user.posts_per_day = user.post_count / float(days.days)
        except (ValueError, TypeError, AttributeError):
            user.posts_per_day = 0
        return render_template('profile/profile.html', user=user)
    else:
        return redirect('front_page.home_page')


def build_timezone_list():
    return [(tz, tz) for tz in pytz.common_timezones]


@profile.route('/view/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    user = User.query.filter_by(username=username).first()
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', user.username)
    form = Profile()
    form.time_zone.choices = build_timezone_list()

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
        user.timezone = form.time_zone.data
        db.session.add(user)
        db.session.commit()

    form.fullname.data = user.fullname or None
    form.location.data = user.location or None
    form.avatar_url.data = user.avatar_url or None
    form.avatar_text.data = user.avatar_text or None
    form.time_zone.data = user.timezone
    try:
        file_list = [f.stat().st_size for f in scandir(file_path)]
        disk_use = sum(file_list)
    except OSError:
        disk_use = 0
    return render_template('profile/edit.html', user=user, form=form,
                           tfa=tfa_state, disk_use=disk_use)


@profile.route('/view/<username>/edit_signature', methods=['GET', 'POST'])
@login_required
def edit_signature(username):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    user = User.query.filter_by(username=username).first()
    form = Signature()

    form.signature.data = user.signature_text

    if form.validate_on_submit():
        print "Signature form fired"
        user.signature_text = form.signature.data
        db.session.add(user)
        db.session.commit()

    return render_template('profile/signature.html', user=user, form=form)


@profile.route('/view/<username>/files', methods=['GET', 'POST'])
@login_required
def manage_files(username):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    filedata = []
    user = User.query.filter_by(username=username).first()
    file_list, file_path = get_file_list(user)
    if file_list:
        for userfile in file_list:
            data = {
                'name': userfile['name'],
                'size': userfile['size'],
                'URL': url_for('media', filename='users/{}/{}'.format(user.username, userfile))
                }
            if user.avatar_url and user.avatar_url.endswith(userfile['name']):
                data['avatar'] = True
            if user.picture_url and user.picture_url.endswith(userfile['name']):
                data['picture'] = True
            im = Image.open(os.path.join(file_path, userfile['name']))
            data['w'] = im.size[0]
            data['h'] = im.size[1]
            if data['w'] > 300 and data['h'] > 300:
                data['resize'] = True
                if not os.path.isfile(os.path.join(file_path, 'tn/tn_{}'.format(userfile['name']))):
                    dest_path = os.path.join(file_path, 'tn')
                    generate_thumbnail(userfile['name'], source_path=file_path, dest_path=dest_path, width=300)
            filedata.append(data)
    return render_template('profile/manage_files.html', user=user, filedata=filedata)


def get_file_list(user):
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', user.username)
    if not os.path.isdir(file_path):
        os.makedirs(file_path)
    file_list = [{'name': f.name, 'size': f.stat().st_size} for f in scandir(file_path) if f.is_file()]
    return file_list, file_path


@profile.route('/view/<username>/files/upload', methods=['GET', 'POST'])
@login_required
def user_upload(username):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    user = User.query.filter_by(username=username).first()
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', username)
    form = Upload()

    if form.validate_on_submit():
        file_data = form.file.data
        filename = secure_filename(file_data.filename)
        if filename.rsplit('.')[1].lower() in ALLOWED_EXTENSIONS:
            try:
                file_data.save(os.path.join(file_path, filename))
            except IOError:
                flash('Image appears corrupted or failed verification')
                return redirect(url_for('profile.manage_files', username=username))
        else:
            flash("Unacceptable file type submitted for upload")
            return redirect(url_for('profile.manage_files', username=username))
        flash("Filed uploaded successfully")
        return form.redirect()

    return render_template('profile/upload.html', username=username, form=form, user=user)


@profile.route('/view/<username>/files/transload', methods=['GET', 'POST'])
@login_required
def user_transload(username):
    if current_user.username != username and not current_user.is_administrator():
            return redirect(url_for('front_page.home_page'))
    user = User.query.filter_by(username=username).first()
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', username)
    form = Transload()

    if form.validate_on_submit():
        url = form.url.data
        response = transload(url)
        if int(response.headers['Content-Length']) > int(current_app.config['MAX_CONTENT_LENGTH']):
            return abort(413)
        img = Image.open(BytesIO(response.content))

        if img.format.lower() in ALLOWED_EXTENSIONS:
            secured_name = secure_filename(response.url.split('/')[-1])
            outfile = os.path.join(file_path, secured_name)
            try:
                img.save(outfile, img.format)
            except IOError:
                flash('Image appears corrupted or failed verification')
                return redirect(url_for('profile.manage_files', username=username))
        else:
            flash("Unacceptable file type submitted for upload")
        return redirect(url_for('profile.manage_files', username=username))
    return render_template('profile/transload.html', username=username, form=form, user=user)


@profile.errorhandler(413)
def request_entity_too_large(error):
    return "File exceeds upload limits", 413


@profile.route('/view/<username>/files/rename/<filename>', methods=['GET', 'POST'])
@login_required
def rename_file(username, filename):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    form = Rename()
    if form.validate_on_submit():
        file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', username)
        os.rename(os.path.join(file_path, filename),
                  os.path.join(file_path, form.filename.data))
        return redirect(url_for('profile.manage_files', username=username))
    form.filename.data = filename
    return render_template('profile/rename.html', form=form)


@profile.route('/view/<username>/files/delete/<filename>', methods=['GET'])
@login_required
def delete_file(username, filename):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    current_app.logger.info("User {} requested deletion of file {}".format(username, filename))
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', username, filename)
    os.remove(file_path)
    return redirect(url_for('profile.manage_files', username=username))


@profile.route('/view/<username>/files/<filename>/set_avatar', methods=['GET'])
@login_required
def set_avatar(username, filename):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    user = User.query.filter_by(username=username).first()
    new_avatar = url_for('media', filename='users/{}/{}'.format(user.username, filename))
    user.set_avatar_url(new_avatar)
    return redirect(url_for('profile.manage_files', username=username))


@profile.route('/view/<username>/files/<filename>/set_picture', methods=['GET'])
@login_required
def set_picture(username, filename):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    user = User.query.filter_by(username=username).first()
    new_picture = url_for('media', filename='users/{}/{}'.format(user.username, filename))
    user.set_picture(new_picture)
    return redirect(url_for('profile.manage_files', username=username))


@profile.route('/view/<username>/download/<filename>')
@login_required
def download_file(username, filename):
    if current_user.username != username and not current_user.is_administrator():
        return redirect(url_for('front_page.home_page'))
    file_path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', username, filename)
    img_type = filename.rsplit('.')[1]
    return send_file(file_path, mimetype='image/{}'.format(img_type), as_attachment=True)
