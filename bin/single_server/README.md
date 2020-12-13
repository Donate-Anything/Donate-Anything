# Deployment on Raspberry Pi

Deploying on a Raspberry Pi involves
manually doing blue/green deployment.
The stack is not in a Docker compose
orchestration like before, but instead
will use different ports for gunicorn
to bind to.

Unfortunately, I have zero clue on how
to run this smoothly like Blue/Green
since the program keeps auto-restarting.

---
## How to run

For initial deployment, run:

```shell
sh ./bin/single_server/initial-deploy.sh
```

To update the code, run:

```shell
bash ./bin/single_server/single-deploy.sh
```

On the server, we'll run `supervisorctl update donateanything`.

Some elements like the nginx.conf files
and supervisor configuration files are not
displayed here in case of malicious usage
posing danger to the website.

To debug while following the logs: `tail -fn +1 supervisord.log`
