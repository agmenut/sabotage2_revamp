# -*- coding: utf-8 -*-
from flask import Blueprint
profile = Blueprint('profile', __name__, url_prefix='/profile')
from . import views
