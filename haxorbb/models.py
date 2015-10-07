# -*- coding: utf-8 -*-
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin


class Articles(db.Model):
    __tablename__ = 'articles'
    __table_args__ = {"schema": "portal"}
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255))
    title = db.Column(db.String(255))
    has_image = db.Column(db.Boolean)
    fk_image = db.Column(db.Integer)
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
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2', salt_length=12)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
