# -*- coding: utf-8 -*-
import os
import base64
import onetimepass
from . import db, login_manager
from .utilities.utils import Utilities
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import ARRAY
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer, Signer, BadSignature
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app
from datetime import datetime
import markdown
import bleach


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    html_body = db.Column(db.Text)
    datestamp = db.Column(db.DateTime)
    slug = db.Column(db.String(30))
    visibility = db.Column(db.Boolean, default=True)

    @property
    def is_public(self):
        return self.visibility

    def post(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def on_changed_body(target, value, oldvalue, initator):
        allowed_tags = ['a', 'b', 'i', 'code', 'strong', 'pre', 'ul', 'li',
                        'em', 'ol', 'p', 'img', 'table', 'tr', 'td', 'th',
                        'h1', 'h2', 'h3', 'br', 'code', 'pre', 'strike']
        allowed_attr = ['src', 'alt', 'title', 'href', 'align']
        target.html_body = bleach.clean(markdown.markdown(
            value, output_format='html5', extensions=['markdown.extensions.tables']),
            tags=allowed_tags, attributes=allowed_attr, strip=True)

    @staticmethod
    def on_changed_title(target, value, oldvalue, initiator):
        target.slug = Utilities.generate_slug(value)

db.event.listen(Articles.content, 'set', Articles.on_changed_body)
db.event.listen(Articles.title, 'set', Articles.on_changed_title)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    roles_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    forum_roles_id = db.Column(db.Integer, db.ForeignKey('forum_roles.id'))
    password_hash = db.Column(db.String(160), nullable=False)
    username = db.Column(db.String(32), nullable=False, unique=True, index=True)
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
    threads_posted_to = db.Column(db.Integer, default=0)
    confirmed = db.Column(db.Boolean, default=False)
    articles = db.relationship('Articles', backref='author', lazy='dynamic')
    threads = db.relationship('Threads', backref='poster', lazy='dynamic')
    otp = db.relationship('OTP', uselist=False, backref='otp')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User {!r}>'.format(self.username)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha512:5000', salt_length=12)

    @property
    def thread_count(self):
        return self.get_thread_count()

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
        db.session.commit()

    def set_avatar_url(self, url):
        self.avatar_url = url
        db.session.commit()

    def set_picture(self, url):
        self.picture_url = url
        db.session.commit()

    def allowed(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def forum_permissions(self, permissions):
        return False

    def is_administrator(self):
        return self.allowed(Permissions.ADMINISTRATOR)

    def is_forum_administrator(self):
        return self.forum_permissions(ForumPermissions.ADMINISTRATOR)

    def increment_post_count(self):
        self.posts += 1

    def get_thread_count(self):
        return self.threads.count()

class AnonymousUser(AnonymousUserMixin):
    def is_administrator(self):
        return False

    def is_forum_administrator(self):
        return False

    def allowed(self, permissions):
        return False

login_manager.anonymous_user = AnonymousUser


class OTP(db.Model):
    __tablename__ = 'otp'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_userid = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    secret = db.Column(db.String(16))
    backup_code = db.Column(ARRAY(Integer))

    def add_opt_secret(self, user):
        if self.secret is None:
            self.secret = base64.b32encode(os.urandom(10)).decode('utf-8')
            self.fk_userid = user.id
            db.session.add(self)
            db.session.commit()

    def get_totp_uri(self, username):
        return 'otpauth://totp/haxorbb:{}?secret={}&issuer=haxorbb'.format(
            username, self.secret
        )

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.secret)

    def generate_machine_token(self):
        s = Signer(self.secret)
        s = s.sign('haxxorbb')
        return s

    def validate_machine_token(self, token):
        s = Signer(self.secret)
        try:
            s.unsign(token)
            return True
        except BadSignature:
            return False


class Permissions(object):
    AUTHOR = 0x02
    EDITOR = 0x04
    ADMINISTRATOR = 0xff


class ForumPermissions(object):
    USER = 0x01
    MODERATOR = 0x02
    ADMINISTRATOR = 0xff


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permissions.AUTHOR, True),
            'Editor': (Permissions.EDITOR, False),
            'Administrator': (Permissions.ADMINISTRATOR, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            print role
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role {!r}>".format(self.name)


class ForumRole(db.Model):
    __tablename__ = 'forum_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='forum_role', lazy='dynamic')

    def __repr__(self):
        return "<Role {!r}>".format(self.name)


class Forums(db.Model):
    __tablename__ = 'forum'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    subtitle = db.Column(db.String)
    group = db.Column(db.String)
    restricted = db.Column(db.Boolean, default=False)
    threads = db.relationship('Threads', backref='thread', lazy='dynamic')

    def __repr__(self):
        return "<Forum {!r}>".format(self.title)


class Threads(db.Model):
    __tablename__ = 'thread'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False, index=True)
    fk_forum = db.Column(db.Integer, db.ForeignKey('forum.id', ondelete='cascade'))
    thread_author = db.Column(db.Integer, db.ForeignKey('users.id'))
    last_post = db.Column(db.DateTime, nullable=False)
    posts = db.relationship('Posts', backref='posts', lazy='dynamic')
    views = db.Column(db.Integer, default=0)

    def post(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self.id
        except Exception as e:
            db.session.rollback()
            raise e


class Posts(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    poster = db.Column(db.Integer, db.ForeignKey('users.id'))
    thread = db.Column(db.Integer, db.ForeignKey('thread.id', ondelete='cascade'))
    body = db.Column(db.Text)
    html_body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False)
    edit_time = db.Column(db.DateTime)

    def post(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def on_changed_body(target, value, oldvalue, initator):
        allowed_tags = ['a', 'b', 'i', 'code', 'strong', 'pre', 'ul', 'li',
                        'em', 'ol', 'p', 'img', 'table', 'tr', 'td', 'th',
                        'h1', 'h2', 'h3', 'br', 'code', 'pre', 'strike']
        allowed_attr = ['src', 'alt', 'title', 'href', 'align']
        target.html_body = bleach.clean(markdown.markdown(
            value, output_format='html5', extensions=['markdown.extensions.tables']),
            tags=allowed_tags, attributes=allowed_attr, strip=True)

db.event.listen(Posts.body, 'set', Posts.on_changed_body)