# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from flask import Markup
from wtforms import (Field, StringField, BooleanField)
from wtforms.validators import Length, DataRequired
from wtforms.widgets.core import html_params
from flask.ext.pagedown.fields import PageDownField


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


class NewThread(Form):
    title = StringField('title', validators=[DataRequired(), Length(3, 80)])
    body = PageDownField('body', validators=[DataRequired()])
    submit = Button('Post')
