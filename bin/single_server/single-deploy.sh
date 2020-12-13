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

BLUE_FILE=/etc/nginx/sites-enabled/da-blue.conf
GREEN_FILE=/etc/nginx/sites-enabled/da-green.conf

if [ -f "$BLUE_FILE" ]; then
  # Switch to green
  rm $BLUE_FILE
  ln -s /etc/nginx/sites-available/da-green.conf /etc/nginx/sites-enabled
  DEL_PORT=49152
  NEW_PORT=49153
else
  rm $GREEN_FILE
  ln -s /etc/nginx/sites-available/da-blue.conf /etc/nginx/sites-enabled
  DEL_PORT=49153
  NEW_PORT=49152
fi

# Below is from https://stackoverflow.com/a/51866665
# Some variables were changed from the answer
# By: takasoft
# Licensed under CC BY-SA 4.0
pid=`ps ax | grep gunicorn | grep $DEL_PORT | awk '{split($0,a," "); print a[1]}' | head -n 1`
if [ -z "$pid" ]; then
  echo "no gunicorn deamon on port $DEL_PORT"
else
  kill $pid
  echo "killed gunicorn deamon on port $DEL_PORT"
fi

service nginx reload
gunicorn config.wsgi -w 2 --bind 0.0.0.0:$NEW_PORT --chdir $DONATE_ANYTHING_HOME_DIR
