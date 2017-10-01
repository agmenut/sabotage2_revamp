#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists('.env'):
    print("Found .env file, loading...")
    with open('.env') as env:
        for line in env:
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]

from haxorbb import initialize_app, db
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand
from haxorbb.models import User, Role

app = initialize_app(os.getenv('FLASK_CONFIG'))
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

server = Server(host='0.0.0.0')
manager.add_command('runserver', server)


def make_shell_context():
    return {'app': app, 'db': db, 'User': User, 'Role': Role}


manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
