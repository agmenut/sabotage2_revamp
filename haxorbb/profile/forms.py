# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from flask import Markup
from wtforms import (Field, StringField, PasswordField, BooleanField, SubmitField)
from wtforms.validators import Length, Email, EqualTo, DataRequired
from wtforms.fields.html5 import EmailField
from wtforms.widgets.core import html_params
from wtforms import ValidationError
from ..models import User


class ButtonWidget(object):
    html_params = staticmethod(html_params)

    def __init__(self, input_type='submit', text=''):
        self.input_type = input_type
        self.text = text

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', field.type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        return Markup('<button type="submit"{}>{}</button>'.format(
            self.html_params(name=field.name, **kwargs), field.text)
        )


class Button(Field):
    widget = ButtonWidget()

    def __init__(self, label=None, validators=None, text="Submit", **kwargs):
        super(Button, self).__init__(label, validators, **kwargs)
        self.text = text

    def _value(self):
        if self.data:
            return u''.join(self.data)
        else:
            return u''


class Profile(Form):
    fullname = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    picture_url = StringField('Picture', validators=[Length(0, 250)])
    avatar_url = StringField('Avatar', validators=[Length(0, 250)])
    avatar_text = StringField('Avatar Text', validators=[Length(0, 250)])
    submit = Button('Submit Changes')
