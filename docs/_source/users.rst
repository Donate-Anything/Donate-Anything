 .. _users:

Users
======================================================================

Anyone can be a user to collect points by the number
of donations sent (depending on the items),
maintain organizations that don't have a verified owner
account or are in hybrid mode, gain points for
maintenance and voting in the community, and report content.

Maintaining an organization, if there is no verified
account, is highly likely. Users will be a part of a
community that maintains all aspects of the website.

.. automodule:: donate_anything.users.models
   :members:
   :noindex:

Emails
------

Emails can be changed by the user within the account itself.
Go to your profile and select My Info. On the other hand,
if a user attempts any other method of blocking
our emails, these are our policies:

Because we use AWS SES, our policy for handling emails is
as follows (`based on their sample documentation`_) and other
`best practices`_:

- If we receive a hard/permanent bounce, blacklist the email.
- If we receive a soft/transient bounce, raise a validation error. The email won't be blacklisted.
- If we receive a complaint, we blacklist them so no emails are further sent via a blacklist.
- If a user accidentally "complained," then they can fill out a Google Form to be un-blacklisted.
- I didn't add an SNS topic for delivery.

.. _based on their sample documentation: https://aws.amazon.com/blogs/messaging-and-targeting/handling-bounces-and-complaints/
.. _best practices: https://postmarkapp.com/guides/transactional-email-bounce-handling-best-practices
