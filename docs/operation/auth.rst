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

This guide assumes basic knowledge and understanding of the
`SAML 2.0 Web Browser SSO Profile <https://en.wikipedia.org/wiki/SAML_2.0#Web_browser_SSO_profile>`_.
We support SAML 2.0 Web-based SSO for login and logout. It is based on the
`OneLogin implementation <https://github.com/onelogin/python3-saml>`_.
Currently, as a result, we support the HTTP-POST binding for login,
and HTTP-Redirect for logout.

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

To enable SAML SSO, we need to specify a number of settings.

We need to enable `saml_sso` and specify the location of the IdP metadata
The metadata can be specified either as a URL, or a file path to an xml-file
containing this information.

.. code-block:: toml

  [saml_sso]
  enable = true
  idp_metadata_url = "http://url-to-adfs.com/fs/metadata.xml"

It is recommended instead that you configure the domain and URL schema for the
OS2mo deployment. This allows the metadata to be generated with the correct
values, no matter if the endpoint is called from ``localhost``.
Without this information, the auth module will attempt to infer this from the request.

The following options will result in paths being generated for
``https://domain.com/saml/*``

.. code-block:: toml

  [saml_sso]
  force_https = true
  sp_domain = "domain.com"

If the IdP is ADFS, the following configuration needs to be set.
ADFS URL encodes SAML data as lowercase, whereas Python's ``urllib`` encodes
as uppercase. This results in a signature verification mismatch, so this
parameter forces ``urllib`` to match ADFS's encoding:

.. code-block:: toml

  [saml_sso]
  lowercase_urlencoding = true

OS2mo currently does not depend on any attributes from the IdP, apart from the
NameID which is used as the identifier for the logged in user in the upper
right corner of the UI. So if the IdP configures the NameID as the user's
email, then the email will appear as the user's name in OS2mo.

If for whatever reason we want to base the logged in user's name on a specific
attribute instead of NameID, it can be done with the following options. Note
that these options are *specific* to OS2mo, and do not exist in the auth
module:

.. code-block:: toml

  [saml_sso]
  # Whether or not the username should be read from the NameID returned from
  # the IdP. This is the default.
  username_from_nameid = true
  # If username is not read from NameID, the username will be read from an
  # attribute with this name.
  username_attr = ""

Finally, the credentials for the session database need to be specified:

.. code-block:: toml

  [session.database]
  host = "localhost"
  name = "sessions"
  password = "sessions"

The settings above comprise a *minimal* setup. Different IdP setups have
different requirements, so a number of additional configuration options
are available to handle these cases.

Detailed descriptions of these configuration options can be found in the
`Flask SAML SSO configuration <https://flask-saml-sso.readthedocs.io/en/latest/README.html#configuration>`_
documentation.
The auth module expects configuration settings as a part of Flask app
configuration object, so OS2mo performs a mapping between its own configuration
format and the configuration keys in Flask. For the exact mapping
between ``flask_saml_sso`` configuration options and OS2mo
configuration options, please refer to the ``app_config`` object in
``backend/mora/settings.py``.

Troubleshooting
^^^^^^^^^^^^^^^

For troubleshooting, it is beneficial to set the log level to ``DEBUG``.
This makes the auth module log information about the entire login flow,
and the contents of various variables. During SSO/SLO the control flow bounces
from us as SP, to the IdP, and back to us, so it is important to know in
*which* part of the flow the problem occurs.

When auth fails, in general, two situations can occur.

- A request is sent to the IdP, from which we never receive a response.

  - Usually this is accompanied by an error message on the IdP login page.
  - This can be caused by incorrect configuration of the IdP, incorrect
    configuration of our SP in the IdP, but also an incompatible/incorrect
    request being sent from us.
  - Further troubleshooting requires **looking at the IdP error message**

- The auth module fails either before redirecting to the IdP, or upon receiving
  a response.

  - This can be caused by configuration issues on our end, or the IdP sending
    an incompatible response
  - Further troubleshooting requires **looking at our own error log**


Auth issues are manifold and incredibly varied. So it is difficult to create
an exhaustive guide for dealing with every issue that may occur.

The various configuration options for the auth module are meant to handle
problems *on our end*, where the IdPs have specific requirements and behavior.

Refer to the Flask SAML SSO configuration for descriptions of these additional
values.

Integrating with OS2mo
^^^^^^^^^^^^^^^^^^^^^^

When OS2mo is running with authentication enabled, using the REST API requires
an API-token.

Refer to the
`API token <https://flask-saml-sso.readthedocs.io/en/latest/README.html#api-tokens>`_
documentation for more information of how to work with API tokens.

Authorization
-------------

Role-based authorization is currently not implemented for OS2mo

Testing
-------

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
