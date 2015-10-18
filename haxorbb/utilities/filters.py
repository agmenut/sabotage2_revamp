# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_login import current_user
import pytz

filters = Blueprint('filters', __name__)


def datetime_filter(value):
    usertz = pytz.timezone(current_user.timezone)
    if value:
        utc_value = pytz.utc.localize(value)
        user_value = usertz.normalize(utc_value)
        return user_value.strftime("%Y-%m-%d %H:%M:%S %Z")
    else:
        return "None"
filters.add_app_template_filter(datetime_filter)

