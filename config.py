import os

from kombu import Queue, Exchange

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'MAIL_SERVER'
    MAIL_PORT = 'MAIL_PORT'
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Mail Subject]'
    FLASKY_MAIL_SENDER = 'Mail Sender <EMAIL_ADDRESS>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or ['SYSTEM_ADMIN']
    FLASKY_SLOW_DB_QUERY_TIME = 0.5

    BASE_DIR = os.path.dirname(__file__)

    CLIENT_DIR = os.path.join(BASE_DIR, 'app', 'client', 'vue-app')

    SALT = '''xC)1F;M0^c'P^iLsc5:XsgFu~WEg$YY-r>a>C&}Xb7u8Q4E!TVvM[dY!g"=d:B#'''

    if not os.path.exists(CLIENT_DIR):
        raise Exception(
            'Client App directory not found: {}'.format(CLIENT_DIR))

    JWT_SECRET_KEY = '*U@j6t/H]NxTo|eBi0YC!f+m1l+Z|KEIwzf;qOn02]ko?{?%:-X$,+n0/d.|1yh'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    JSONIFY_PRETTYPRINT_REGULAR = False

    CELERY_QUEUES = (
        Queue('LONG', Exchange('LONG'), routing_key='LONG'),
        Queue('SHORT', Exchange('SHORT'), routing_key='SHORT'),
        Queue('NORMAL', Exchange('NORMAL'), routing_key='NORMAL'),
        Queue('MAIL', Exchange('MAIL'), routing_key='MAIL'),
        Queue('TRANSACTIONS', Exchange('TRANSACTIONS'), routing_key='TRANSACTIONS'),
    )
    CELERY_DEFAULT_QUEUE = 'NORMAL'
    CELERY_DEFAULT_EXCHANGE = 'NORMAL'
    CELERY_DEFAULT_ROUTING_KEY = 'NORMAL'

    CELERY_ROUTES = {
        # 'app.tasks.update_transactions': {'queue': 'TRANSACTIONS'},
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    JWT_SECRET_KEY = '''b8P5bgj}.5!'M!4M,f^e43v=Jv*0LID="Loqjmha%D@:B2pLGL]x#,zAasN9]Ql'''


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False

    JWT_SECRET_KEY = '''%@aK!KnP-mF8pizS@>LTb,mY)rG``j$ZU[*Q-)5;k"^kcN7{#<1Z'_xGbqFdN[Q'''


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    JWT_SECRET_KEY = '''>9@H=?c83TVWhY^n:AEs$MeIXq<|{$Lj%{[dISEC);M3HDAaxl(mlb}?pG/K/4H'''

    SYSTEM_ANALYSTS = ['SYSTEM_MANAGERS']

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,
    'unix': UnixConfig,
    'default': DevelopmentConfig
}
