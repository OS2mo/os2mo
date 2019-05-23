Authentication
==============

OS2MO supports SAML based single sign-on for authentication

Support for this is implemented through the module `Flask SAML SSO`_.

This currently requires a LoRa backend setup to have
authentication enabled as well, using the same module.

Once logged in a session is created which is shared between OS2MO and LoRa,
containing the claims given to us from the IdP.

.. _Flask SAML SSO: https://github.com/magenta-aps/flask_saml_sso

SAML based single sign-on (SSO)
-------------------------------
SAML SSO delegates the login process to the IdP, and as such, requires an
IdP supporting SAML single sign-on.

OS2MO has to be registered as a Service Provider (SP) in the IdP - To
facilitate this, we expose an endpoint containing all the necessary metadata::

  http://<OS2MO URL>/saml/metadata/

Most IdPs support consuming this metadata directly, automatically registering
the SP with correct configuration.

Configuration
"""""""""""""

Configuration and general use of SAML SSO is documented in
the `readme`_ for Flask SAML SSO.

The following additional configuration entries exist for auth in OS2MO.

* ``"SAML_USERNAME_FROM_NAMEID"``: Whether or not the username should be read
  from the NameID returned from the IdP. This is the default.
* ``"SAML_USERNAME_ATTR"``: If username is not read from NameID, the username
  will be read from an attribute with this name.

.. _readme: https://github.com/magenta-aps/flask_saml_sso/blob/master/README.rst

Testing
"""""""

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
