# -*- coding: utf-8 -*-
from flask import render_template, redirect, url_for, flash, request, abort, make_response, current_app
from . import auth
from .forms import (Registration, Login, ChangePassword, ResetPassword,
                    ResetPasswordRequest, TFAToken)
from .. import db
from ..email import send_mail
from ..models import User, OTP
from flask_login import (login_user, logout_user, login_required, fresh_login_required,
                             current_user)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from io import BytesIO
from datetime import timedelta
import pyqrcode
from os import path, mkdir


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    cookie = False
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).one()
        except NoResultFound:
            flash("Authentication failed")
            return redirect(url_for('auth.login'))
        if user is not None and user.verify_password(form.password.data):
            print("OK to login")
            login_user(user, form.remember.data)
            if current_user.otp is not None:
                jar = request.cookies.get('2FA')
                if jar and current_user.otp is not None and current_user.otp.validate_machine_token(jar):
                    cookie = True
                if user.otp.secret and not cookie:
                    return redirect(url_for('auth.validate'))
            return redirect(request.args.get('next') or url_for('front_page.home_page'))
        flash('Authentication failed')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = Registration()
    if form.validate_on_submit():
        user = User()
        user.email = form.email.data
        user.username = form.username.data
        user.password = form.password.data
        db.session.add(user)
        try:
            db.session.commit()
            token = user.generate_confirmation_token()
            send_mail(user.email, 'Confirm your account',
                      'auth/email/confirm', user=user, token=token)
            flash('A confirmation email has been sent.')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred')
            print(form.errors, e)
        return redirect(url_for('front_page.home_page'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('front_page.home_page'))
    if current_user.confirm(token):
        current_app.logger.info("Starting confirmation process for newly registered user: {}".format(
                current_user.username))
        # Create user directories on account confirmation
        mkdir(path.join(current_app.config['MEDIA_ROOT'], 'users', current_user.username))
        mkdir(path.join(current_app.config['MEDIA_ROOT'], 'users', current_user.username, 'tn'))
        flash("Your account has been confirmed.")
    else:
        current_app.logger.warning("User {} tried to confirm an account with an invalid link".format(current_user.username))
        flash("Confirmation link invalid.")
    return redirect(url_for('front_page.home_page'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm your account',
              'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to {}.'.format(current_user.email))
    current_app.logger.info("A new confirmation email has been sent to {}.".format(current_user.email))
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
    current_app.logger.info("User {} has requested a password change".format(current_user.username))
    return render_template('auth/change_password.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.':
        current_user.seen()
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/recover', methods=['GET', 'POST'])
def recover_account():
    if not current_user.is_anonymous:
        current_app.logger.warning("Known user {}".format(current_user.username))
        return redirect(current_user.landing_page)
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
        print("Validated")
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


@auth.route('/enable_2fa')
@login_required
def enable_2fa():
    return render_template('auth/two_factor_enable.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@auth.route('/qrcode')
@login_required
def qrcode():
    if current_user is None:
        abort(404)
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        abort(404)

    if user.otp is None:
        otp = OTP()
        otp.add_opt_secret(current_user)

    url = pyqrcode.create(user.otp.get_totp_uri(current_user.username))
    stream = BytesIO()
    url.svg(stream, scale=3)
    return stream.getvalue().encode('utf-8'), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@auth.route('/validate', methods=['GET', 'POST'])
def validate():
    if current_user.is_authenticated:
        print("OK")
    if current_user is None:
        abort(404)
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        abort(404)

    ten_years = timedelta(days=3650)

    form = TFAToken()
    if form.validate_on_submit():
        if user.otp.verify_totp(form.token.data):
            resp = make_response(redirect(url_for('front_page.home_page')))
            if form.remember.data:
                resp.set_cookie('2FA', current_user.otp.generate_machine_token(),
                                max_age=ten_years.total_seconds(),
                                expires=ten_years.total_seconds()
                                )
            return resp
        else:
            flash("Invalid token")
    return render_template('auth/validate2fa.html', form=form)


@auth.route('/generate_backup_codes')
@login_required
def generate_backup_codes():
    if not current_user.is_authenticated or current_user is None:
        abort(401)
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        abort(404, "No such user")

    user.otp.generate_backup_codes()
    return redirect(url_for('profile.edit_profile', username=current_user.username))


@auth.route('/disable_2FA', methods=['GET'])
def disable_2fa():
    if not current_user.is_authenticated or current_user is None:
        abort(401)
    user = User.query.filter_by(username=current_user.username).first()
    if user is None:
        abort(404, "No such user")

    user.remove_otp_token()
    return redirect(url_for('profile.edit_profile', username=current_user.username))
