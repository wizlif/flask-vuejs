import functools
import gzip
from io import BytesIO as IO

from flask import after_this_request, request

from .exceptions import handler, create_logger
from .messages import internal_error


def exception(original_function=None, message='Some error occurred on our end.'):
    def decorator(function):
        @functools.wraps(function)
        def wrapper_function(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                print(e)
                handler(create_logger(), e)
                return internal_error(message)

        return wrapper_function

    if original_function:
        return decorator(original_function)

    return decorator


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                    response.status_code >= 300 or
                    'Content-Encoding' in response.headers):
                return response

            gzip_buffer = IO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)

            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func
