from flask.ext.mail import Message
from threading import Thread
from flask import current_app, render_template
from . import mail


def send_async_email(app, msg):
    with app.app_context():
            mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    print "CONFIG:", app.config['MAIL_USE_TLS']
    print app.config['MAIL_USE_SSL']
    print type(app.config['MAIL_USE_SSL'])
    msg = Message(app.config['MAIL_PREFIX'] + ' ' + subject, sender=app.config['MAIL_REPLY'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
