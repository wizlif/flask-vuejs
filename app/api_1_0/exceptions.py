import sys

import logging
from requests_toolbelt.utils import dump


class ValidationError(ValueError):
    pass


class HttpLogger:
    def __init__(self, logger, response):
        try:
            if logger:
                logger.info(dump.dump_all(response).decode('utf-8'))
            else:
                print(dump.dump_all(response).decode('utf-8'))
        except:
            pass


class HttpException(Exception):
    def __init__(self, response, logger=None):
        message = f'\n\n{"/"* 16} HTTP REQUEST {"/"* 16}\n'
        f'URL: {response.url}\n\n'
        f'STATUS_CODE: {response.status_code}\n\n'
        f'RESPONSE:\n{response.text}\n'
        f'{"/" * 46}\n\n'

        if logger:
            logger.error(message)

        super().__init__(message)


def handler(logger, e='Exception'):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    exc_type, filename, line_no = exc_type, exc_tb.tb_frame.f_code.co_filename, exc_tb.tb_lineno

    logger.error(f'\n+{"-" * 64}\n'
                 '| Exception details:\n'
                 f'| Message: {e}\n'
                 f'| Type:\t\t{exc_type}\n'
                 f'| File:\t\t{filename}\n'
                 f'| Line No:\t\t{line_no}\n'
                 f'+{"-" * 64}\n')


def prod_log(logger, message, level='error'):
    if level == 'error':
        logger.error(f'\n{message}\n')
    elif level == 'critical':
        logger.critical(f'\n{message}\n')
    elif level == 'debug':
        logger.debug(f'\n{message}\n')
    elif level == 'info':
        logger.info(f'\n{message}\n')
    elif level == 'warning':
        logger.warning(f'\n{message}\n')
    else:
        logger.error(f'\n{message}\n')


def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("exception_logger")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    fh = logging.FileHandler("/tmp/production.log")

    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)
    return logger
