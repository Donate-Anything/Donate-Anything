# Deployment on Raspberry Pi

Deploying on a Raspberry Pi involves
manually doing blue/green deployment.
The stack is not in a Docker compose
orchestration like before, but instead
will have Postgres + Redis in the Pi
itself and Django + Celery will run in
a Docker compose stack.

This was mostly copied from
[rodolpheche/bluegreen-traefik-docker](https://github.com/rodolpheche/bluegreen-traefik-docker)

---
## How to run

For initial deployment, run:

```shell
sh ./bin/single_server/initial-deploy.sh
```

To update the code, run:

```shell
sh ./bin/single_server/single-deploy.sh
```

To clean up:
```shell
docker stack rm http appli-green appli-blue
docker network rm da-front-network
```
