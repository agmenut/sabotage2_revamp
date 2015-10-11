# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import (StringField, PasswordField, BooleanField, SubmitField)
from wtforms import validators
from wtforms import ValidationError
from ..models import User

class Registration(Form):
    email = StringField