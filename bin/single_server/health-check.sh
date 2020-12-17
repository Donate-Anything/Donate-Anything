#!/bin/sh
#
# health-check.sh
# Velnota
#
# Created by Andrew Chen Wang on 2020/12/17
# Copyright (c) 2020 Velnota LLC
#

# Reloads nginx once gunicorn loads new app
# correctly by pinging until it's ready.

COUNTER=0

if [[ -z "${MAX_HEALTH_CHECK_LIMIT}" ]]; then
  MAX_HEALTH_CHECK_LIMIT=300
fi

IS_READY=false

while [ $COUNTER -lt $MAX_HEALTH_CHECK_LIMIT ]; do
  if nc -zw 2 127.0.0.1 $NEW_PORT; then
      IS_READY=true
      break
  fi
  COUNTER=$((COUNTER + 1))
done

if [ "$IS_READY" = true ]; then
  # Wait until Django + Axes are setup
  sleep 15
  service nginx reload

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
  # End of SO answer
fi
