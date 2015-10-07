# -*- coding: utf-8 -*-
from flask import Blueprint
front_page = Blueprint('front_page', '__name__')
from . import views