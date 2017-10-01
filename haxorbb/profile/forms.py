# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask import Markup, request, redirect, url_for
from flask_pagedown.fields import PageDownField
from urllib.parse import urlparse, urljoin
from wtforms import (Field, StringField, FileField, SelectField, HiddenField)
from wtforms.fields.html5 import URLField
from wtforms.validators import Length, URL, DataRequired, Optional
from wtforms.widgets.core import html_params, HTMLString


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


class CustomFileInput:
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        img = url_for('static', filename='ic_file_upload_black_24px.svg')
        return HTMLString(f"<input type=file id={field.id}><div class=\"dragtarget\">Drop file here</div>")


class DragAndDropFileField(StringField):
    widget = CustomFileInput()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectableForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class Profile(FlaskForm):
    fullname = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    picture_url = StringField('Picture', validators=[Length(0, 250)])
    avatar_url = StringField('Avatar', validators=[Length(0, 250)])
    avatar_text = StringField('Avatar Text', validators=[Length(0, 250)])
    time_zone = SelectField('Time Zone', coerce=str)
    redirect_target = SelectField('Preferred redirect target', coerce=str)
    submit = Button('Submit Changes')


class Signature(FlaskForm):
    signature = PageDownField('Signature')
    submit = Button('Update signature')


class Upload(RedirectableForm):
    # file = FileField('File', validators=[DataRequired()])
    upload_file = DragAndDropFileField(validators=[Optional()])
    submit = Button(text='Upload')

    # def validate(self):
    #     if self.upload_file.data:
    #         print("Data encountered")


class Transload(RedirectableForm):
    url = URLField('Image URL', validators=[DataRequired(), URL()])
    submit = Button('Transload')


class Rename(FlaskForm):
    filename = StringField('Filename', validators=[DataRequired(), Length(5, 64)])
    submit = Button('Rename')

