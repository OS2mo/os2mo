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
