[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FDonate-Anything%2FDonate-Anything.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2FDonate-Anything%2FDonate-Anything?ref=badge_shield)

Donate Anything
===============

A website that shows charities by filtering on the items you want to donate.

Created on 11 July 2020

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style
.. image:: https://readthedocs.org/projects/donate-anything/badge/?version=latest
    :target: https://donate-anything.readthedocs.io/en/latest/_source/?badge=latest
    :alt: Documentation Status


:License: Apache 2.0

Guide
-----

Our goal is not to change people's perspective. In business, the general rule is to not change consumer's perspective but follow them or build upon them.

In this case, it's waste disposal. Some people are poor to not be able to clean. Others' are too lazy or don't care. We cannot change those habits...

But we can solve or, what I like to call, "re-route" the problems they generate. It's not a good social goal as racking up problems is terrible for society, but Donate Anything is a bandage.

If you want REAL societal solutions to waste instead of a bandage, visit `Donate-Everything`_.

.. _Donate-Everything: https://github.com/Donate-Everything

General Functionality
^^^^^^^^^^^^^^^^^^^^^

You do not need an account to use the website, as that's the
most desired outcome. The point is that you can search up
an item and find a charity you can donate to.

A user can also search up multiple items. What's returned
are charities that can fulfill all items, if possible. Those
charities must be specific about those items, however.
For example, the Salvation Army won't be shown unless they
choose the items themselves.

Charities and Other Services
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Charities do not need to signup on the platform to be listed.
Users (either on GitHub in the Feedback repository or the
website itself) can tell us how to manage their content.

However, this service is not exclusively for charities or 501(c)3's.
We welcome several for-profit programs, including recycling, nursing
facilities, and small businesses as this platform is about donations.
Additionally, it is up to the donor as to who to donate to.
For for-profit businesses like recyclers and small business owners,
there is a separate process for identifying yourself and certain limits
and regulations.

Charities can manage their content on the website by filling
out a form to be "verified." Once manually verified on the
platform, they can manage their content with custom text
without further verification for change on the website.

Charities are typically 501(c)3's. Any user can register
a charity by filling out an HTML form that includes
the 501(c)3 record, website that specifies how to donate,
and a template description and how-to-donate instruction.

Roadmap
-------

Our roadmap is very complex for an open-source organization.
However, in our regards, we aim to grow this like a business.
This project is in early development, so understand that some
good ideas may pop up, but they may not be good due to the
site being in use for such little time.

Recall our core guideline: Our goal is not to change people's perspective. In business, the general rule is to not change consumer's perspective but follow them or build upon them.

Please keep this in mind before suggesting new ideas. Donate Anything is a bandage; visit Donate Everything, a societal solution.

- Migrate from PostgreSQL to Elasticsearch (it's already setup, but using Elasticsearch early on would be too costly. Visit `this GH issue <https://github.com/Donate-Anything/Donate-Anything/issues/1>`_ for integration).
- Machine learn what's "good," "ok/mild," or "bad" condition based on images. Should be easy with the amount of data from current charities. This makes filtering and deciding if items can be collected easier for donor's end.
- Improve text search with content context
- Gamify the donation process. Should organizations be giving the points? Or automatic upon verification?

Hacking
-------

Follow HACKING.rst for all set up needs. You don't need
Docker necessarily, but it'll be helpful to set up.

For quick setup, you can use Docker compose::

    $ docker-compose -f local.yml build
    $ docker-compose -f local.yml run --rm django python manage.py migrate
    $ docker-compose -f local.yml up

Or you can setup a PostgreSQL database and a Python virtualenv
to properly start the development server. Celery (and thus Redis)
is not yet needed on this development platform, so Windows users
do not need to set these up.

License
-------

Donate Anything is licensed under the Apache 2.0 License. You can find
the license in the `LICENSE`_ file.

.. _LICENSE: https://github.com/Donate-Anything/Donate-Anything/blob/master/LICENSE

::

    Copyright 2020 Andrew Chen Wang

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FDonate-Anything%2FDonate-Anything.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FDonate-Anything%2FDonate-Anything?ref=badge_large)