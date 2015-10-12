# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request
from . import auth
from .forms import Registration, Login
from .. import db
from ..email import send_mail
from ..models import User
from flask.ext.login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm.exc import NoResultFound


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).one()
        except NoResultFound:
            flash("Authentication failed")
            return redirect(url_for('auth.login'))
        if user and user.verify_password(form.password.data):
            print "OK to login"
            login_user(user)
            return redirect(url_for('front_page.home_page'))

        # if User.verify_password()
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
            token = user.generated_confirmation_token()
            send_mail(user.email, 'Confirm your account',
                      'auth/email/confirm', user=user, token=token)
            flash('A confirmation email has been sent.')
        except Exception as e:
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

@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.':
        return redirect(url_for('auth.unconfirmed'))

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


