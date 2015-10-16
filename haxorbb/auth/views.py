# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request
from . import auth
from .forms import Registration, Login, ChangePassword, ResetPassword, ResetPasswordRequest
from .. import db
from ..email import send_mail
from ..models import User
from flask.ext.login import (login_user, logout_user, login_required, fresh_login_required,
                             current_user)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).one()
        except NoResultFound:
            flash("Authentication failed")
            return redirect(url_for('auth.login'))
        if user is not None and user.verify_password(form.password.data):
            print "OK to login"
            login_user(user, form.remember.data)
            return redirect(request.args.get('next') or url_for('front_page.home_page'))
        flash('Authentication failed')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = Registration()
    if form.validate_on_submit():
        print "Good"
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.password = form.password.data
        db.session.add(user)
        print "Trying commit of new user"
        try:
            db.session.commit()
            token = user.generate_confirmation_token()
            send_mail(user.email, 'Confirm your account',
                      'auth/email/confirm', user=user, token=token)
            flash('A confirmation email has been sent.')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred')
            print form.errors
        return redirect(url_for('front_page.home_page'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('front_page.home_page'))
    if current_user.confirm(token):
        flash("Your account has been confirmed.")
    else:
        flash("Confirmation link invalid.")
    return redirect(url_for('front_page.home_page'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm your account',
              'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to {}.'.format(current_user.email))
    return redirect(url_for('front_page.home_page'))


@auth.route('/change_password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        if current_user.verify_password(form.current.data):
            flash("Password has been updated")
            current_user.password = form.new.data
            db.session.add(current_user)
            db.session.commit()
            send_mail(current_user.email, 'Your password has changed',
                      'auth/email/password_change', user=current_user)
            return redirect(url_for('front_page.home_page'))
    return render_template('auth/change_password.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.':
        current_user.seen()
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/recover', methods=['GET', 'POST'])
def recover_account():
    if not current_user.is_anonymous:
        return redirect(url_for('front_page.home_page'))
    form = ResetPasswordRequest()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_mail(user.email, 'Reset your password',
                      'auth/email/reset_password',
                      user=user, token=token, next=request.args.get('next'))
            flash('An email with password reset instructions has been sent to the email address you entered')
            return redirect(url_for('front_page.home_page'))
    return render_template('auth/reset_request.html', form=form)


@auth.route('/recover/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('front_page.home_page'))
    form = ResetPassword()
    if form.validate_on_submit():
        print "Validated"
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('front_page.home_page'))
        if user.reset_password(token, form.password.data):
            flash('Password Reset')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('front_page.home_page'))
    return render_template('auth/reset_password.html', form=form, token=token)


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('front_page.home_page'))
    return render_template('auth/unconfirmed.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('front_page.home_page'))
