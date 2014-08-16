# -*- coding: utf-8 -*-
import os
import json

_cwd = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(_cwd, 'local.conf')) as config_file:
    db_conf = json.load(config_file)

DB_USER = db_conf['user']
DB_PASS = db_conf['pass']
DB_HOST = db_conf['host']


class BaseConfiguration(object):
    DEBUG = False
    SECRET_KEY = 'RANDOMIZE ME'
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_ECHO = True


class TestConfiguration(BaseConfiguration):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
