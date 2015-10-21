# -*- coding: utf-8 -*-
from flask import Blueprint, current_app
from flask_login import current_user
import pytz

filters = Blueprint('filters', __name__)


def datetime_filter(value):
    if current_user.is_anonymous:
        usertz = pytz.timezone(current_app.config['TIME_ZONE'])
    else:
        usertz = pytz.timezone(current_user.timezone)
    if value:
        utc_value = pytz.utc.localize(value)
        user_value = usertz.normalize(utc_value)
        return user_value.strftime("%Y-%m-%d %H:%M:%S %Z")
    else:
        return "None"
filters.add_app_template_filter(datetime_filter)
