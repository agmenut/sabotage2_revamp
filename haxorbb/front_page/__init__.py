# -*- coding: utf-8 -*-
from flask import Blueprint
front_page = Blueprint('front_page', '__name__')
from . import views
from ..models import Permissions


@front_page.app_context_processor
def inject_permissions():
    return dict(Permissions=Permissions)


