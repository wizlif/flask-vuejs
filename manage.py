#!/usr/bin/env python
import os
import subprocess

from flask import url_for
from flask_socketio import SocketIO

from config import Config

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage

    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db
from app.models import (Users, UserStatus, Groups)
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)


def make_shell_context():
    return dict(app=app, db=db,
                Groups=Groups,
                UserStatus=UserStatus,
                Users=Users,
                )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade

    # migrate database to latest revision
    upgrade()

    Users.insert_default_user()

    print('>>> Deployment Successful')


def _bash(cmd, **kwargs):
    """ Helper Bash Call"""
    print('>>> {}'.format(cmd))
    return subprocess.call(cmd, env=os.environ, shell=True, **kwargs)


@manager.command
def serve():
    """ Run Vue Development Server"""
    print('Starting Vue dev server...')
    cmd = 'yarn serve'
    _bash(cmd, cwd=Config.CLIENT_DIR)


@manager.command
def build():
    """ Builds Vue Application """
    cmd = 'yarn build'
    _bash(cmd, cwd=Config.CLIENT_DIR)
    print('Build completed')


@manager.command
def lint():
    """ Lints Vue Application """
    cmd = 'yarn lint'
    _bash(cmd, cwd=Config.CLIENT_DIR)
    print('Lint completed')


@manager.command
def run_redis():
    """ Run redis server """
    cmd = 'bash run-redis.sh'
    _bash(cmd)


@manager.command
def list_routes():
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        print(url + ' ' + methods)


@manager.command
def build_docs():
    cmd = 'cd docs && make html && rm -rfv ../app/client/docs/* && cp -avr build/html/* ../app/client/docs'
    _bash(cmd)


if __name__ == '__main__':
    # socketio.run(app)
    manager.run()
