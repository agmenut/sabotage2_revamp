# -*- coding: utf-8 -*-
from flask import Flask, send_from_directory, send_file, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from config import config


class ReverseProxied(object):
    """Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.refresh_view = 'auth.login'
login_manager.need_refresh_message = u"Please re-authenticate to protect your account."
login_manager.needs_refresh_message_category = 'info'

db = SQLAlchemy()
mail = Mail()


def initialize_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].initapp(app)

    app.wsgi_app = ReverseProxied(app.wsgi_app)
    login_manager.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    # Init the Media directory
    app.media = app.config['MEDIA_ROOT']

    # Register blueprints
    from .auth import auth as authentication
    app.register_blueprint(authentication)

    from .front_page import front_page
    app.register_blueprint(front_page)

    from .profile import profile
    app.register_blueprint(profile)

    from .utilities import filters
    app.register_blueprint(filters.filters)

    @app.route('/robots.txt')
    def robots():
        return send_from_directory(app.static_folder, request.path[1:])

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error.html", error=e), 404

    @app.route('/media/<path:filename>')
    def media(filename):
        return send_from_directory(app.config['MEDIA_ROOT'], filename)

    @app.route('/static/<path:filename>.svg')
    def svg_response(filename):
        print "Found filename:", filename
        return send_file('static/' + filename + '.svg',
                         mimetype='image/svg+xml')

    return app
