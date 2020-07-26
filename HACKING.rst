Hacking
=======

These are the necessary information you need to know
to contribute to Donate Anything's website repository.

You also agree to the Code of Conduct linked in the repository.

Settings
--------

Moved to settings_.

.. _settings: http://cookiecutter-django.readthedocs.io/en/latest/settings.html

Basic Commands
--------------

Setting Up Data
^^^^^^^^^^^^^^^

* To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

* To create an **superuser account**, use this command::

    $ docker-compose -f local.yml run --rm django python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

The purpose of user accounts is to manage your organization, talk
in discussion rooms on the website, chat with organizations, etc..

Data for fast setup::

    $ docker-compose -f local.yml run --rm django python manage.py create_item_data
    $ docker-compose -f local.yml run --rm django python manage.py create_charity_data

If you use PyCharm, there is a run configuration called "Restart" which will
set up all the needed data for you with a provided superuser: test, test@test.com, test.
Lint
^^^^

Typically, I run my lint with system interpreter. My command::

    $ black donate_anything config && isort -y -rc -lai 2

It's already loaded for PyCharm users.

Type checks
^^^^^^^^^^^

Running type checks with mypy:

::

  $ docker-compose -f local.yml run --rm django mypy donate_anything

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ docker-compose -f local.yml run --rm django coverage run -m pytest
    $ docker-compose -f local.yml run --rm django coverage html
    $ open htmlcov/index.html

Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ docker-compose -f local.yml run --rm django pytest

Email Server
^^^^^^^^^^^^

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server `MailHog`_ with a web interface is available as docker container.

Container mailhog will start automatically when you will run all docker containers.
Please check `cookiecutter-django Docker documentation`_ for more details how to start all containers.

With MailHog running, to view messages that are sent by your application, open your browser and go to ``http://127.0.0.1:8025``

.. _mailhog: https://github.com/mailhog/MailHog
.. _`cookiecutter-django Docker documentation`: http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html

Setting Environment Variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When making a PR, if you need to set an environment variable for production
use, specify the environment variable name. We use Travis to encrypt our
files for Zappa, which means you'll not be able to decrypt the settings file.
