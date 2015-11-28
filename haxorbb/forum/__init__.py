# -*- coding: utf-8 -*-
from flask import Blueprint
forum = Blueprint('forum', __name__, url_prefix='/forum')
from . import views
