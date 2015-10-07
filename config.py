# -*- coding: utf-8 -*-
import os
import json

_cwd = os.path.dirname(os.path.abspath(__file__))


# with open(os.path.join(_cwd, 'local.conf')) as config_file:
#     db_conf = json.load(config_file)
#
# DB_USER = db_conf['haxorbb']['user']
# DB_PASS = db_conf['haxorbb']['pass']
# DB_HOST = db_conf['haxorbb']['host']
# MEDIA = "<PATH TO MEDIA DIR>"


class BaseConfiguration(object):
    DEBUG = False
    MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

    @staticmethod
    def initapp(app):
        pass


class DevelopmentConfig(BaseConfiguration):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    print "Database url:", os.environ.get('DATABASE_URL')

    @classmethod
    def initapp(cls, app):
            BaseConfiguration.initapp(app)


class TestConfiguration(BaseConfiguration):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
          }
