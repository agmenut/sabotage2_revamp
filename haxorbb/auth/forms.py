# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from flask import Markup
from wtforms import (Field, StringField, PasswordField, BooleanField, IntegerField)
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


class Registration(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Length(3, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('verify_password')])
    verify_password = PasswordField('Verify Password', validators=[DataRequired(), EqualTo('password')])
    submit = Button('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email address already registered")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already registered")


class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = Button('Submit')


class ChangePassword(FlaskForm):
    current = PasswordField('Current Password', validators=[DataRequired(), Length(1, 64)])
    new = PasswordField('New Password', validators=[DataRequired(), Length(1, 64), EqualTo('confirm_new')])
    confirm_new = PasswordField('Confirm Password', validators=[DataRequired(), Length(1, 64), EqualTo('new')])
    submit = Button('Change password')


class ResetPasswordRequest(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(3, 64)])
    submit = Button('Request Password Reset')


class ResetPassword(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(3, 64)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('verify_password')])
    verify_password = PasswordField('Verify Password', validators=[DataRequired(), EqualTo('password')])
    submit = Button('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Email address not found')


class TFAToken(FlaskForm):
    token = IntegerField('Token', validators=[DataRequired()])
    remember = BooleanField('Remember this computer', default=False)
    submit = Button('Validate Token')
