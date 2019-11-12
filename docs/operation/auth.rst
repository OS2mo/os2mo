Authentication
==============

Authentication in OS2mo is based on SAML 2.0 single sign-on.
Support for this is implemented through the module
`Flask SAML SSO <https://github.com/magenta-aps/flask_saml_sso>`_.

Once a user has been authenticated, a session is created containing the
attributes given to us from the IdP, e.g. the Active Directory groups the
user belongs to

The module can also optionally be enabled for LoRa in case its REST API needs
to be available externally. The auth module then allows for a shared session
between LoRa and OS2mo.

SAML based single sign-on (SSO)
-------------------------------

SAML SSO delegates the login process to the IdP, and as such, requires an
IdP supporting SAML single sign-on.

Instructions (in Danish) for configuring ADFS for SAML SSO
can be found in :ref:`cookbook`.

OS2mo has to be registered as a Service Provider (SP) in the IdP - To
facilitate this, we expose an endpoint containing all the necessary metadata::

  http://<OS2MO URL>/saml/metadata/

Most IdPs support consuming this metadata directly, automatically registering
the SP with correct configuration.

Configuration
^^^^^^^^^^^^^

Detailed instructions for configuring OS2mo authentication can be found in the
documentation for
`Flask SAML SSO <https://flask-saml-sso.readthedocs.io/en/latest/>`_. For the
exact mapping between ``flask_saml_sso`` configuration options and OS2MO
configuration options, please refer to the ``app_config`` object in
``backend/mora/settings.py``.

The following additional configuration entries exist for auth in OS2MO.

* ``"SAML_USERNAME_FROM_NAMEID"``: Whether or not the username should be read
  from the NameID returned from the IdP. This is the default.
* ``"SAML_USERNAME_ATTR"``: If username is not read from NameID, the username
  will be read from an attribute with this name.

All configuration of OS2MO is done as described in :ref:`settings`. The
relevant section for authentication is called ``[saml_sso]``.

Minimal example
"""""""""""""""

The auth module contains sane defaults for a large number of the parameters,
which should work with *most* IdPs. The following is a minimal example for
configuring SAML auth and sessions::

  [saml_sso]
  enable = true
  idp_metadata_url = "http://url-to-adfs.com/fs/metadata.xml"

  [session.database]
  host = "localhost"
  name = "sessions"
  password = "sessions"

Testing
^^^^^^^

.. highlight:: shell

The easiest way to set up a SAML Identity Provider for testing and
development, is to use the ``test-saml-idp`` `docker image`_. First,
run the ``full-run`` development server::

  ./flask.sh full-run --idp-url http://localhost:8000

Note the port that it uses, typically ``8080``::

  export MO_URL=http://localhost:8080

Then run the docker image::

  docker run --name=testsamlidp_idp \
    -p 8000:8080 \
    -e SIMPLESAMLPHP_SP_ENTITY_ID=$MO_URL/saml/metadata/ \
    -e SIMPLESAMLPHP_SP_ASSERTION_CONSUMER_SERVICE=$MO_URL/saml/acs/ \
    -e SIMPLESAMLPHP_SP_SINGLE_LOGOUT_SERVICE=$MO_URL/saml/sls/ \
    -d kristophjunge/test-saml-idp

This will download the image if necessary and start it with port 8080
redirected to 8000, and configured to use and allow
``http://localhost:8000`` as the Service Provider.

Two users exist in the test IdP image; ``user1`` and ``user2`` with the
passwords ``user1pass`` and ``user2pass`` respictively.

.. _docker image: https://hub.docker.com/r/kristophjunge/test-saml-idp/

Authorization
-------------

Role-based authorization is currently not implemented for OS2mo
