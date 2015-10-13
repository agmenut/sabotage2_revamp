# -*- coding: utf-8 -*-
import os
import ast


class BaseConfiguration(object):
    DEBUG = False
    MEDIA_ROOT = os.environ.get('MEDIA')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_REPLY = os.environ.get('MAIL_REPLY')
    MAIL_PREFIX = os.environ.get('MAIL_PREFIX')
    MAIL_USE_TLS = ast.literal_eval(os.environ.get('MAIL_USE_TLS'))
    MAIL_USE_SSL = ast.literal_eval(os.environ.get('MAIL_USE_SSL'))

    @staticmethod
    def initapp(app):
        pass


class DevelopmentConfig(BaseConfiguration):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @classmethod
    def initapp(cls, app):
        BaseConfiguration.initapp(app)
        print app.config


class ProductionConfig(BaseConfiguration):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    @classmethod
    def initapp(cls, app):
        BaseConfiguration.initapp(app)



class TestConfiguration(BaseConfiguration):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
          }
