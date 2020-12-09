#!/bin/sh
#
# initial-deploy.sh
# Velnota
#
# Created by Andrew Chen Wang on 2020/12/8
# Copyright (c) 2020 Velnota LLC
#

# Does the initial deployment of a single server
# doing blue/green deployment

docker swarm init
docker network create -d overlay da-front-network
docker stack deploy -c production.blue.yml appli-blue
docker stack deploy -c production.traefik.yml http
docker stack deploy -c production.green.yml appli-green
touch ./blue.txt
