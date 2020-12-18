#!/bin/bash
#
# single-deploy.sh
# Velnota
#
# Created by Andrew Chen Wang on 2020/12/8
# Copyright (c) 2020 Velnota LLC
#

# Does Blue/Green Deployment

# Rebuild
cd $DONATE_ANYTHING_HOME_DIR
git pull origin master

# ~/donate_anything
deactivate || echo
VENV_DIR=$DONATE_ANYTHING_HOME_DIR/venv
if [ ! -f "$VENV_DIR" ]; then
  virtualenv venv
fi
source $VENV_DIR/bin/activate
pip install -r requirements/raspberry.txt

export DJANGO_SETTINGS_MODULE=config.settings.self_hosted
python manage.py collectstatic --noinput
python manage.py compress
python manage.py migrate

BLUE_FILE=/etc/nginx/sites-enabled/da-blue.conf
GREEN_FILE=/etc/nginx/sites-enabled/da-green.conf

if [ -f "$BLUE_FILE" ]; then
  # Switch to green
  rm $BLUE_FILE
  ln -s /etc/nginx/sites-available/da-green.conf /etc/nginx/sites-enabled
  # Export so that further scripts can use
  export DEL_PORT=49152
  export NEW_PORT=49153
else
  rm $GREEN_FILE
  ln -s /etc/nginx/sites-available/da-blue.conf /etc/nginx/sites-enabled
  export DEL_PORT=49153
  export NEW_PORT=49152
fi

bash $DONATE_ANYTHING_HOME_DIR/bin/single_server/health-check.sh &
gunicorn config.wsgi -w 2 --bind 127.0.0.1:$NEW_PORT --chdir $DONATE_ANYTHING_HOME_DIR
