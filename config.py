# -*- coding: utf-8 -*-
import os
import ast


class BaseConfiguration(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MEDIA_ROOT = os.environ.get('MEDIA')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_REPLY = os.environ.get('MAIL_REPLY')
    MAIL_PREFIX = os.environ.get('MAIL_PREFIX')
    MAIL_USE_TLS = ast.literal_eval(os.environ.get('MAIL_USE_TLS'))
    MAIL_USE_SSL = ast.literal_eval(os.environ.get('MAIL_USE_SSL'))
    TIME_ZONE = os.environ.get('TIME_ZONE')
    # Set max file upload to 16MB unless another value set in env. config.
    MAX_CONTENT_LENGTH = os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024
    # Set the logging directory to application root unless overridden in env
    LOG_DIR = os.environ.get('LOG_DIR') or os.path.dirname(os.path.realpath(__file__))


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
