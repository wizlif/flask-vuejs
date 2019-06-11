from datetime import datetime

import requests
from celery.schedules import crontab
from celery.signals import task_postrun
from celery.utils.log import get_task_logger
from flask import current_app
from flask.ext.mail import Message

from app.api_1_0.exceptions import HttpException, HttpLogger
from app.function_utils import poll, MaxCallException
from . import celery, db, mail

logger = get_task_logger(__name__)


@celery.task
def send_email_background(to: list, subject, html, text, cc=None):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=to,
                  cc=cc)
    msg.body = text
    msg.html = html
    mail.send(msg)
    write_to_log.apply_async(kwargs={'mail_to': str(msg.send_to), 'subject': msg.subject, 'body': msg.body, 'type': 4},
                             queue='SHORT')


@celery.task
def warning(data):
    logger.warning(data)


@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()


@celery.task
def write_to_log(user_id=None, message=None, action=None,
                 ip_address=None, type=1,
                 mail_to=None, subject=None, body=None,
                 domain=None):
    if type == 1:
        logger.critical(message)
    elif type == 2:
        logger.info(message)
    elif type == 3:
        logger.error(message)
    elif type == 4:
        logger.warning(message)

    lgs = Logs(
        user_id=user_id,
        message=message,
        action=action,
        ipaddress=ip_address,
        type=type,
        mail_to=mail_to,
        subject=subject,
        body=body,
        domain=domain,
        timestamp=datetime.utcnow()
    )

    if ip_address:
        try:
            location_details = poll(get_log_ip_details, args=[ip_address], max_tries=2)
            lgs.city = location_details.get("city", None)
            lgs.region = location_details.get("region", None)
            lgs.region_code = location_details.get("region_code", None)
            lgs.country = location_details.get("country", None)
            lgs.country_name = location_details.get("country_name", None)
            lgs.continent_code = location_details.get("continent_code", None)
            lgs.in_eu = location_details.get("in_eu", None)
            lgs.postal = location_details.get("postal", None)
            lgs.latitude = location_details.get("latitude", None)
            lgs.longitude = location_details.get("longitude", None)
            lgs.timezone = location_details.get("timezone", None)
            lgs.utc_offset = location_details.get("utc_offset", None)
            lgs.country_calling_code = location_details.get("country_calling_code", None)
            lgs.currency = location_details.get("currency", None)
            lgs.languages = location_details.get("languages", None)
            lgs.asn = location_details.get("asn", None)
            lgs.org = location_details.get("org", None)
        except MaxCallException:
            logger.error(f'Failed to get location details for {ip_address}')
        except Exception as e:
            logger.error(e)

    db.session.add(lgs)

    db.session.commit()


def get_log_ip_details(ip):
    if ip == '127.0.0.1' or ip == '0.0.0.0':
        raise Exception(f'Invalid IP {ip}')
    req = requests.get(f'https://ipapi.co/{ip}/json')
    HttpLogger(logger, req)

    if req.status_code == 200:
        return req.json()
    else:
        raise HttpException(req, logger)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=2, minute=30),
        # import_digicert_orders.s()
    )
