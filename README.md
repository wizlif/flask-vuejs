Quick Setup
-----------

1. Clone this repository.
2. Create a virtualenv `virtualenv --python=python3.6 venv` 
3. Install the requirements (`pip install -r requirements/common.txt`)
3. Run the database migrations (`python manage.py db upgrade`)
4. If you do not already have a redis instance running on your machine,Open a second terminal window and start a local Redis server (if you are on Linux or Mac, execute `python manage.py run_redis` to install and launch a private copy).
5. Open a third terminal window. Set two environment variables `MAIL_USERNAME` and `MAIL_PASSWORD` to a valid EMAIL account credentials (these will be used to send emails through your SMTP server). 
6. Then start a Celery worker: `python manage.py celery_worker` and Celery Beat: `python manage.py celery_beat`.
7. Start Flasky on your first terminal window: `python manage.py runserver`.
8. Make calls to `http://localhost:5000/` for the api!

**Note:** Remember to set proper configuration variables in `config.py`

Setting up Apache2 mod_wsgi
---------------------------
1. Install apache2-dev and python3.6-dev \
`sudo aptitude install apache2-dev python3.6-dev`
2. Remove libapache2-mod-wsgi and libapache2-mod-wsgi-py3 \
`sudo apt-get remove libapache2-mod-wsgi libapache2-mod-wsgi-py3` 
3. Create a virtual environment or if you already have one, activate it.
4. Install mod_wsgi `pip install mod_wsgi`
5. Install mod_wsgi module using `venv/bin/mod_wsgi-express install-module` and copy the output.
6. Create an apache2 module `wsgi_express.{conf,load}` with the contents copied in 5 above in `/etc/apache2/mods-available`.
7. Enable the module `sudo a2enmod wsgi_express`
8. Restart apache2
9. Go get a cup of coffee.

Production Setup
-----------

1. Clone this repository
2. Install the requirements globally (`pip install -r requirements/common.txt`)
3. Run the database migrations (`python manage.py db upgrade`)
4. Run the deployment script (`python manage.py deploy`)
5. Start redis if not running with  (`python manage.py run_redis`)
6. Copy the supervisor configuration for celery worker and beat to supervisor  `sudo cp -avr ./deploy_confs/celeryd.conf /etc/supervisor/conf.d` and change the absolute paths to match those on the system.
7. Start `celeryd.conf` with the following commands \
`sudo supervisorctl reread`\
`sudo supervisorctl update` \
`sudo supervisorctl start celery-workers`\
confirm that the supervisor process is running by checking the celery beat and celery worker log files.
8. Using either the `apache2_mod_wsgi.conf` or `apache2_proxy.conf`, setup your apache2 configuration, editing where required.
Use the `application.wsgi` for your mod_wsgi configuration. 
9. Restart apache2 with `sudo apache2 reload`
10. Open the configured server name in a browser to check if everything is operational.

Note: Edit your `celeryd.conf`,`application.wsgi` and `apache2_mod_wsgi.conf` with respect to your system.
