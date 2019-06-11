from flask import jsonify


def internal_error(message):
    response = jsonify({'error': 'internal server error', 'message': message})
    response.status_code = 500
    return response


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def not_found(message):
    response = jsonify({'error': 'not found', 'message': message})
    response.status_code = 404
    return response


def success(message):
    response = jsonify({'success': 'complete', 'message': message})
    response.status_code = 200
    return response


def unprocessable(message):
    response = jsonify({'error': 'unprocessable', 'message': message})
    response.status_code = 422
    return response


def conflict(message):
    response = jsonify({'error': 'conflict', 'message': message})
    response.status_code = 409
    return response
