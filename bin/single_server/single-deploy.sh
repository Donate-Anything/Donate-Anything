#!/bin/sh
#
# single-deploy.sh
# Velnota
#
# Created by Andrew Chen Wang on 2020/12/8
# Copyright (c) 2020 Velnota LLC
#

# Does Blue/Green Deployment

BLUE_FILE=./blue.txt
GREEN_FILE=./green.txt

# Rebuild the images
docker-compose -f production.blue.yml build

# It's not really blue green
if [ -f "$BLUE_FILE" ]; then
  rm $BLUE_FILE
  touch $GREEN_FILE
  docker service update --label-add "traefik.http.routers.colors-green.priority=100" appli-green_django
  docker service update --label-add "traefik.http.routers.colors-blue.priority=0" appli-blue_django
else
  rm $GREEN_FILE
  touch $BLUE_FILE
  docker service update --label-add "traefik.http.routers.colors-blue.priority=100" appli-blue_django
  docker service update --label-add "traefik.http.routers.colors-green.priority=0" appli-green_django
fi
