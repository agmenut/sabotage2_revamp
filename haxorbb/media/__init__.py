# -*- coding: utf-8 -*-
from flask import Blueprint

media = Blueprint('media', __name__, url_prefix='/media')

from . import views



