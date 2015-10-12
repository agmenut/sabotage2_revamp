# -*- coding: utf-8 -*-
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists('.env'):
    print "Found .env file, loading..."
    with open('.env') as env:
        for line in env:
            var = line.strip().split('=')
            print var
            if len(var) == 2:
                os.environ[var[0]] = var[1]

from haxorbb import initialize_app, db
from flask.ext.script import Manager

app = initialize_app(os.getenv('FLASK_CONFIG'))
print app.config
manager = Manager(app)

if __name__ == '__main__':
    manager.run()
