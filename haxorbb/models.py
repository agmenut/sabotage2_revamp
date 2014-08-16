# -*- coding: utf-8 -*-
from . import db


class Articles(db.Model):
    __tablename__ = "articles"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255))
    title = db.Column(db.String(255))
    image = db.Column(db.String(50))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)
