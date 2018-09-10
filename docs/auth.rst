Authentication
==============

OS2MO supports two types of authentication.

* SAML based single sign-on
* SAML token auth

Both methods currently require a LoRa backend setup to have
authentication enabled as well, as LoRa is in charge of verifying
the validity of the authentication tokens produced by both methods.

Additionally, both methods produce authentication tokens containing SAML
assertions, and are effectively identical in that regard.
The only difference is how the user identity is verified and how the
initial SAML assertion is acquired.

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

The following configuration entries are relevant for SAML SSO:

* ``"AUTH"``: Which auth module to enable, e.g. ``"sso"``
* ``"SSO_SAML_METADATA_URL"``: The URL to the IdPs metadata
* ``"SSO_SAML_USERNAME_ATTR"``: The name of the attribute in the SAML assertion
  containing the username
* ``"SAML_IDP_INSECURE"``: Whether or not the IdP metadata endpoint should be
  accessed insecurely (useful is testing setups where the IdP uses self-signed
  certificates)
* ``"SAML_AUTHN_REQUESTS_SIGNED"``: Whether authorization requests towards the
  IdP should be signed
* ``"SAML_KEY_FILE"``: Path to private key file, used for signing requests.
* ``"SAML_CERT_FILE"``: Path to a public certificate file, used for signing
  requests.

Example configuration entries::

  {
    ...
    "AUTH": "sso",
    "SSO_SAML_METADATA_URL": "https://192.168.1.212/simplesaml/saml2/idp/metadata.php",
    "SSO_SAML_USERNAME_ATTR": "urn:oid:2.5.4.41",
    "SAML_IDP_INSECURE": true,
    "SAML_AUTHN_REQUESTS_SIGNED": true,
    "SAML_KEY_FILE": "/etc/ssl/server.key",
    "SAML_CERT_FILE": "/etc/ssl/server.crt"
    ...
  }


SAML token auth **(deprecated)**
--------------------------------

...
