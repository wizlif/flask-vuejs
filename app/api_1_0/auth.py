"""
.. module:: Authorization
    :platform: Linux
    :synopsis: module managing user authentication

.. moduleauthor:: Obella Isaac <iobella@i3c.co.ug>
"""

import base64
import datetime

from flask import json, jsonify, render_template
from flask import request, current_app, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from werkzeug.utils import redirect

from . import api
from .decorators import exception, gzipped
from .messages import bad_request, success, unauthorized, not_found
from .. import bcrypt, db
from .. import blacklist
from ..models import Users
from ..tasks import write_to_log

prefix = '/auth'


@api.route(f'{prefix}/login', methods=['POST'])
@exception(message='Error occurred while signing in.')
@gzipped
def login():
    """
    .. http:post:: /api/v1/login

       Sign in to the generic domains registry using valid ``credentials``.

       :reqheader Accept: application/json
       :reqheader Authorization: mandatory OAuth token to authenticate
       :resheader Content-Type: application/json
       :status 200: when successful
       :status 400: when form parameters are missing
       :status 401: when unauthorized
       :status 404: when user doesn't exist
       :status 500: when an error occurs

    ..  http:example:: curl wget httpie python-requests

        POST /api/v1/login HTTP/1.1
        Host: localhost:5000
        Accept: application/json
        Content-Type: application/json


        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1NDMzOTIyNTYsIm5iZiI6MTU0MzM5MjI1NiwianRpIjoiZTI5MzNkOTQtZmFkNC00MTFhLWE5MmMtMzk3ZTU3ZWY2N2E4IiwiZXhwIjoxNTQzNDAzMDU2LCJpZGVudGl0eSI6MjA5LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MifQ.visqnE2urdROlRKUg2KdJEIJQviVZEsBzUhfLyMLzL4",
            "user_token": "eyJhZG1pbl9pZCI6IG51bGwsICJjaXR5IjogImthbXBhbGEiLCAiY291bnRyeSI6ICJVRyIsICJjcmVhdGVkX2F0IjogIk1vbiwgMDEgT2N0IDIwMTggMDU6MjU6NTIgR01UIiwgImNyZWRpdF9iYWxhbmNlIjogODg3NC4wLCAiZW1haWwiOiAiaW9iZWxsYUBpM2MuY28udWciLCAiZmF4IjogbnVsbCwgImZpcnN0bmFtZSI6ICJvYmVsbGEiLCAiaWQiOiAyMDksICJsYXN0X2xvZ2luIjogIldlZCwgMjggTm92IDIwMTggMDk6MDg6MjkgR01UIiwgImxhc3RuYW1lIjogImlzYWFjIiwgIm1pbl9iYWxhbmNlIjogbnVsbCwgIm1vYmlsZV9waG9uZSI6ICIrMjU2Ljc3ODkxNjM1MyIsICJuYW1lIjogIm9iZWxsYSBpc2FhYyIsICJuczEiOiAibnMxLmNmaS5jby51ZyIsICJuczFfaXAiOiAiNTAuMjIuMjA4LjEzMCIsICJuczIiOiAibnMyLmNmaS5jby51ZyIsICJuczJfaXAiOiAiNTAuMjIuMjA4LjE0MCIsICJuczMiOiAibnMzLmNmaS5jby51ZyIsICJuczNfaXAiOiAiMTk4LjIzLjkwLjE1NSIsICJuczQiOiAibnM0LmNmaS5jby51ZyIsICJuczRfaXAiOiAiMTkyLjE2OC4xMDAuMjQ5IiwgIm9yZ2FuaXphdGlvbiI6ICJpbmZpbml0eSBjb21wdXRlcnMiLCAicGFzc3dvcmRfcmVzZXRfc2VudF9hdCI6ICJNb24sIDAzIFNlcCAyMDE4IDE3OjUxOjU5IEdNVCIsICJwaG9uZSI6ICIrMjU2Ljc3ODkxNjM1MyIsICJwb3N0YWxfY29kZSI6ICI2NzgyIiwgInByaXZpbGVnZXMiOiAiU3VwZXIgQWRtaW4iLCAic3RhdGVfcHJvdmluY2UiOiAiY2VudHJhbCIsICJzdGF0dXMiOiAiQUNUSVZFIiwgInN0cmVldF9hZGRyZXNzIjogInBsb3QgNmIgd2luZHNvciBsb29wIiwgInVwZGF0ZWRfYXQiOiBudWxsfQ=="
        }
"""
    req = request.json

    username = req.get('email', None)
    password = req.get('password', None)

    if not username:
        return bad_request("Missing username parameter")
    if not password:
        return bad_request("Missing password parameter")

    user = Users.query.filter_by(email=username).first()

    if not user:

        write_to_log.apply_async(kwargs={'message': f'{username}\'s account doesn\'t exist.',
                                         'action': 'Login Failure',
                                         'ip_address': request.remote_addr},
                                 queue='SHORT')

        return not_found('User doesn\'t exist')
    elif user.status == 2:

        write_to_log.apply_async(kwargs={'message': f'{username}\'s account not activated.',
                                         'action': 'Login Failure',
                                         'ip_address': request.remote_addr},
                                 queue='SHORT')

        return unauthorized('Account not activated')
    elif bcrypt.check_password_hash(user.password_digest, password):

        expires = datetime.timedelta(hours=3)
        access_token = create_access_token(identity=user.id, expires_delta=expires)

        user_token = (
            base64.b64encode(json.dumps(user.to_json()).encode('ascii'))).decode(
            'utf-8')

        write_to_log.apply_async(kwargs={'user_id': user.id,
                                         'message': f'{user.name()} logged in.',
                                         'action': 'Admin Login Success' if user.admin() else 'User Login Success',
                                         'ip_address': request.remote_addr},
                                 queue='SHORT')

        user.last_login = datetime.datetime.now()
        db.session.commit()

        return jsonify(access_token=access_token, user_token=user_token)
    else:

        write_to_log.apply_async(kwargs={'message': f'{username}\'s invalid username or password.',
                                         'action': 'Login Failure',
                                         'ip_address': request.remote_addr
                                         },
                                 queue='SHORT')

        return unauthorized('Invalid username or password.')


@api.route(f'{prefix}/logout')
@jwt_required
@exception
@gzipped
def logout():
    """
    .. http:get:: /api/v1/logout

       Sign user out of the generic domains registry.

       :reqheader Accept: application/json
       :reqheader Authorization: mandatory OAuth token to authenticate
       :resheader Content-Type: application/json
       :status 200: when successful
       :status 401: when unauthorized
       :status 422: when missing or malformed JWT token
       :status 500: when an error occurs

    ..  http:example:: curl wget httpie python-requests

        GET /api/v1/logout HTTP/1.1
        Host: localhost:5000
        Accept: application/json
        Authorization: Bearer JWT
        Content-Type: application/json


        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "status": "success",
            "message": "Successfully logged out"
        }
"""

    user = Users.query.get(get_jwt_identity())

    jti = get_raw_jwt()['jti']
    blacklist.add(jti)

    write_to_log.apply_async(kwargs={'message': f'{user.name()} logged out.',
                                     'action': 'Logout',
                                     'user_id': get_jwt_identity(),
                                     'ip_address': request.remote_addr},
                             queue='SHORT')

    return success("Successfully logged out")


@api.route(f'{prefix}/send_password_reset/<string:email>')
@exception
def send_reset_password_email(email):
    """
    .. http:get:: /api/v1/auth/send_password_reset/(string:email)

       Trigger a resend of password reset email.

       :reqheader Accept: application/json
       :resheader Content-Type: application/json
       :status 200: when successful
       :status 401: when unauthorized
       :status 500: when an error occurs

    ..  http:example:: curl wget httpie python-requests

        GET api/v1/auth/send_password_reset/``(string:email)`` HTTP/1.1
        Host: localhost:5000
        Accept: application/json
        Content-Type: application/json


        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            "status":"success",
            "message":"A Password reset has been sent to ``string:email`` with an activation link. Click on it to reset."
        }
    """
    user = Users.query.filter_by(email=email).first()

    if not user:

        write_to_log.apply_async(kwargs={'message': f'{email} is not associated with any account.',
                                         'action': 'Password reset',
                                         'ip_address': request.remote_addr},
                                 queue='SHORT')

        return bad_request('Email is not associated with any account.')
    elif user.status == 2:

        write_to_log.apply_async(kwargs={'message': f'{email}\'s account not activated.',
                                         'action': 'Password reset',
                                         'user_id': user.id,
                                         'ip_address': request.remote_addr},
                                 queue='SHORT')

        return unauthorized('Account not activated')
    else:

        token = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).dumps(user.email,
                                                                               salt=current_app.config['SALT'])

        user.password_reset_token = token
        user.password_reset_sent_at = datetime.datetime.now()
        db.session.commit()

        # UserMailer.reset_password_email(
        #     url_for('api.reset_password', token=token, _external=True),
        #     user)

        write_to_log.apply_async(kwargs={
            'message': f'Password reset sent to {email}.',
            'action': 'Password reset',
            'user_id': user.id,
            'ip_address': request.remote_addr},
            queue='SHORT')

        return success(f'A Password reset has been sent to {email} with an activation link. Click on it to '
                       'reset.')


@api.route(f'{prefix}/reset_password/<string:token>', methods=['GET', 'POST'])
@exception
def reset_password(token):
    """
    .. http:get:: /api/v1/auth/reset_password/(string:token)

       Use token from reset email to provide password sign in interface.

        :param token: password reset token
        :type token: str

       :status 302: when successful
       :status 400: when email doesn't exist on system
       :status 401: when unauthorized
       :status 500: when an error occurs

    ..  http:example:: curl wget httpie python-requests

        GET api/v1/auth/send_password_reset/``(string:email)`` HTTP/1.1
        Host: localhost:5000
        Accept: application/json
        Content-Type: application/json


        HTTP/1.1 302 OK

    .. http:post:: /api/v1/auth/reset_password/(string:token)

       Reset user password

        :param token: account email for password reset
        :type token: str

       :status 200: when successful
       :status 400: when email doesn't exist on system
       :status 401: when unauthorized or account not activated
       :status 500: when an error occurs

    ..  http:example:: curl wget httpie python-requests

        GET api/v1/auth/reset_password/``(string:email)`` HTTP/1.1
        Host: localhost:5000
        Accept: application/json
        Content-Type: application/json


        HTTP/1.1 200 OK
        Content-Type: application/json

        {
            'success':'complete',
            'message':'Password reset successfully'
        }
    """
    if request.method == 'GET':
        try:
            email = URLSafeTimedSerializer(current_app.config['SECRET_KEY']).loads(token,
                                                                                   salt=current_app.config['SALT'],
                                                                                   max_age=24 * 60 * 60 * 60)

            user = Users.query.filter_by(email=email).first()

            write_to_log.apply_async(kwargs={'message': f'Password reset initiated for {email}.',
                                             'action': 'Password reset',
                                             'user_id': user.id,
                                             'ip_address': request.remote_addr},
                                     queue='SHORT')

            return redirect(f'#/login/password/reset/{token}')
        except SignatureExpired:

            write_to_log.apply_async(kwargs={'message': f'Token signature expired.',
                                             'action': 'Password reset',
                                             'ip_address': request.remote_addr},
                                     queue='SHORT')

            return redirect(f'#/login/password/reset_expired/{token}')
    elif request.method == 'POST':
        user = Users.query.filter_by(password_reset_token=token).first()

        if not user:
            write_to_log.apply_async(kwargs={'message': f'Token is not associated with any account.',
                                             'action': 'Password reset',
                                             'ip_address': request.remote_addr
                                             },
                                     queue='SHORT')

            return bad_request('Email is not associated with any account.')

        req = request.json

        password = req.get('password')

        if not password:
            return bad_request('Password required')

        user.password_digest = bcrypt.generate_password_hash(password)
        db.session.commit()

        write_to_log.apply_async(kwargs={'message': f'Password reset completed for {user.email}.',
                                         'action': 'Password reset',
                                         'user_id': user.id,
                                         'ip_address': request.remote_addr
                                         },
                                 queue='SHORT')

        return success('Password reset successfully.')
