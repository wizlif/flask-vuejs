from flask import current_app, render_template, json
from flask.ext.mail import Message

from app import celery, mail
from .tasks import write_to_log,warning


@celery.task
def send_async_email(msg):
    mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    send_async_email.apply_async(args=[msg],queue='MAIL')


@celery.task
def send_email_extra(to: list, subject, html, text, cc=None):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=to,
                  cc=cc)
    msg.body = text
    msg.html = html
    warning(msg)
    mail.send(msg)
    write_to_log.apply_async(kwargs={'mail_to':str(msg.send_to), 'subject':msg.subject, 'body':msg.body, 'type':4},queue='SHORT')
