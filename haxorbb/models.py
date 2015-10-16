# -*- coding: utf-8 -*-
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer
from flask.ext.login import UserMixin
from flask import current_app
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    datestamp = db.Column(db.DateTime)
    slug = db.Column(db.String(30))

    def post(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(160), nullable=False)
    username = db.Column(db.String(32), nullable=False)
    fullname = db.Column(db.String(64))
    email = db.Column(db.String(254), nullable=False)
    registration_date = db.Column(db.DateTime)
    location = db.Column(db.String(64))
    avatar_url = db.Column(db.String(250))
    avatar_text = db.Column(db.String(250))
    picture_url = db.Column(db.String(250))
    quota = db.Column(db.Integer)
    disk_used = db.Column(db.Integer)
    active = db.Column(db.Boolean, nullable=False, default=False)
    last_seen = db.Column(db.DateTime)
    timezone = db.Column(db.String(20), default='US/Pacific')
    posts = db.Column(db.Integer, default=0)
    threads = db.Column(db.Integer, default=0)
    threads_posted_to = db.Column(db.Integer, default=0)
    confirmed = db.Column(db.Boolean, default=False)
    articles = db.relationship('Articles', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {!r}>'.format(self.username)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha512:5000', salt_length=12)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def generate_reset_token(self, expiration=3600):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def confirm(self, token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except NameError:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        self.active = True
        self.registration_date = datetime.utcnow()
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print e
            return False

    def reset_password(self, token, new_password):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except NameError:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.commit()
        return True

    def seen(self):
        self.last_seen = datetime.utcnow()


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return "<Role {!r}>".format(self.name)
