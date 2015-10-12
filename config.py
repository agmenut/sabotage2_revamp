# -*- coding: utf-8 -*-
import os


class BaseConfiguration(object):
    DEBUG = False
    MEDIA_ROOT = os.environ.get('MEDIA')

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

class ProductionConfig(BaseConfiguration):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    
    MAIL_REPLY = os.environ.get('MAIL_REPLY')
    MAIL_PREFIX = os.environ.get('MAIL_PREFIX')

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
