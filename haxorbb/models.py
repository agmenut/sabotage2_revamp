# -*- coding: utf-8 -*-
from . import db


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
    image = db.relationship('ArticleImages', backref='articles', lazy='joined')

    def post(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class ArticleImages(db.Model):
    __tablename = 'article_images'
    __table_args__ = {"schema": "portal"}
    id = db.Column(db.Integer, db.ForeignKey('portal.articles.fk_image'), primary_key=True)
    location = db.Column(db.String(255))
    title = db.Column(db.String(255))
    link = db.Column(db.String(2048))

