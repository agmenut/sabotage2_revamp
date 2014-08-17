# -*- coding: utf-8 -*-
from . import db


class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255))
    title = db.Column(db.String(255))
    has_image = db.Column(db.Boolean)
    fk_image = db.Collumn(db.Intger, db.ForeignKey(ArticleImage.id))
    content = db.Column(db.Text)
    datestamp = db.Column(db.DateTime)


class ArticleImage(db.Model):
    __tablename = 'article_images'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255))
    title = db.Column(db.String(255))
    link = db.Column(db.String(2048))

