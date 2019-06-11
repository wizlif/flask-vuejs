import logging
import os
import sys

logging.basicConfig(stream=sys.stderr)

os.environ['FLASK_CONFIG'] = 'production'
os.environ['DATABASE_URL'] ='DATABASE_PATH'
os.environ['MAIL_USERNAME'] = 'MAIL_USER'
os.environ['MAIL_PASSWORD'] = 'MAIL_PASSWORD'

PROJECT_DIR = "APPLICATION_PATH"
sys.path.insert(0, PROJECT_DIR)

activate_this = os.path.join(PROJECT_DIR, 'VENV_BIN_PATH', 'activate_this.py')

with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from manage import app as application