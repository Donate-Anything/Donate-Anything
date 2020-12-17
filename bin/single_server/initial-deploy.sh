#!/bin/bash
#
# initial-deploy.sh
# Velnota
#
# Created by Andrew Chen Wang on 2020/12/8
# Copyright (c) 2020 Velnota LLC
#

# Does the initial deployment of a single server
# doing blue/green deployment. Not actually
# used by us though since we use supervisor

# ~/donate_anything
cd $DONATE_ANYTHING_HOME_DIR
VENV_DIR=$DONATE_ANYTHING_HOME_DIR/venv

if [ ! -f "$VENV_DIR" ]; then
  virtualenv venv
fi
source venv/bin/activate
pip install -r requirements/raspberry.txt

export DJANGO_SETTINGS_MODULE=config.settings.self_hosted
python manage.py collectstatic --noinput
python manage.py compress
python manage.py migrate

# Check if any nginx scripts are in sites-enabled
BLUE_FILE=/etc/nginx/sites-enabled/da-blue.conf
GREEN_FILE=/etc/nginx/sites-enabled/da-green.conf
if [ -f "$GREEN_FILE" ]; then
  gunicorn config.wsgi -w 2 --daemon --bind 127.0.0.1:49153 --chdir $DONATE_ANYTHING_HOME_DIR
else
  if [ ! -f "$BLUE_FILE" ]; then
    ln -s /etc/nginx/sites-available/da-blue.conf /etc/nginx/sites-enabled
    service nginx reload
  fi
  gunicorn config.wsgi -w 2 --daemon --bind 127.0.0.1:49152 --chdir $DONATE_ANYTHING_HOME_DIR
fi

deactivate
