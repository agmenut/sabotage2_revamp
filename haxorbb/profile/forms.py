# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from flask import Markup
from wtforms import (Field, StringField, FileField, SelectField)
from wtforms.validators import Length, DataRequired
from wtforms.widgets.core import html_params


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
    # tz = None
    #
    # def __init__(self, timezone):
    #     super(Profile, self).__init__()
    #     self.tz = timezone
    #     print self.tz
    # tz_data = build_timezone_set()
    fullname = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    picture_url = StringField('Picture', validators=[Length(0, 250)])
    avatar_url = StringField('Avatar', validators=[Length(0, 250)])
    avatar_text = StringField('Avatar Text', validators=[Length(0, 250)])
    time_zone = SelectField('Time Zone', coerce=str)
    submit = Button('Submit Changes')


class Upload(Form):
    file = FileField('File')
    submit = Button('Uploads')


class Rename(Form):
    filename = StringField('Filename', validators=[DataRequired(), Length(5, 64)])
    submit = Button('Uploads')

