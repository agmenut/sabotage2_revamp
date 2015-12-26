# -*- coding: utf-8 -*-
from flask import Blueprint, current_app
from flask_login import current_user
import pytz
from PIL import Image
from StringIO import StringIO
import os.path


filters = Blueprint('filters', __name__)


def base_datetime_filter(value, format_):
    if current_user.is_anonymous:
        usertz = pytz.timezone(current_app.config['TIME_ZONE'])
    else:
        usertz = pytz.timezone(current_user.timezone)
    if value:
        utc_value = pytz.utc.localize(value)
        user_value = usertz.normalize(utc_value)
        return user_value.strftime(format_)
    else:
        return "None"


def datetime_filter(value):
        return base_datetime_filter(value, "%Y-%m-%d %H:%M:%S %Z")
filters.add_app_template_filter(datetime_filter)


def forum_datetime(value):
    return base_datetime_filter(value, '%b %d, %Y %H:%M')
filters.add_app_template_filter(forum_datetime)


def create_timg(img):
    img = os.path.split(img)[1]
    path = os.path.join(current_app.config['MEDIA_ROOT'], 'users', current_user.username, img)
    image_buffer = StringIO()
    im = Image.open(path)
    format_ = im.format
    target_w = 300  # TODO: Replace MAGIC NUMBER with parameter
    ratio = float(im.size[0]) / float(im.size[1])
    target_h = int(target_w / ratio)
    resized = im.resize((target_w, target_h), Image.ANTIALIAS)
    resized.save(image_buffer, format_)
    image_buffer.seek(0)
    target_file = os.path.join(current_app.config['MEDIA_ROOT'], 'users', 'tn', 'tn_{}'.format(img))
    if not os.path.exists(os.path.join(current_app.config['MEDIA_ROOT'], 'users', 'tn')):
        os.mkdir(os.path.join(current_app.config['MEDIA_ROOT'], 'users', 'tn'))
    with open(target_file, 'wb') as imgfile:
        imgfile.write(image_buffer.read())
