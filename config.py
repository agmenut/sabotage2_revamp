# -*- coding: utf-8 -*-
import os
import json

_cwd = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_cwd, 'local.conf')) as config_file:
    db_conf = json.load(config_file)

DB_USER = db_conf['haxorbb']['user']
DB_PASS = db_conf['haxorbb']['pass']
DB_HOST = db_conf['haxorbb']['host']
MEDIA = ""


class BaseConfiguration(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/haxorbb'.format(DB_USER, DB_PASS, DB_HOST)
    MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')


class TestConfiguration(BaseConfiguration):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
