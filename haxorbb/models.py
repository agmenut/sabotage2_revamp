# -*- coding: utf-8 -*-
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin


class Articles(db.Model):
    __tablename__ = 'articles'
    __table_args__ = {"schema": "portal"}
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.userinfo.userid'))
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
    __tablename__ = 'userinfo'
    __table_args__ = {'schema': 'users'}
    userid = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    username = db.Column(db.String(32))
    fullname = db.Column(db.String(64))
    email = db.Column(db.String(254))
    registration_date = db.Column(db.DateTime)
    location = db.Column(db.String(64))
    avatar_url = db.Column(db.String(250))
    picture_url = db.Column(db.String(250))
    quota = db.Column(db.Integer)
    disk_used = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    last_seen = db.Column(db.DateTime)
    articles = db.relationship('Articles', backref='author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2', salt_length=12)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
