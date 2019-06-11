from celery import Celery
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from app.client import docs_bp
from config import Config, config

db = SQLAlchemy()
mail = Mail()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

blacklist = set()


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mail.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    celery.conf.update(app.config)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        ''''''
        # sslify = SSLify(app)

    from .api_1_0 import api as api_1_0_blueprint
    from .client import client_bp

    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1')
    app.register_blueprint(client_bp)
    app.register_blueprint(docs_bp)

    return app
