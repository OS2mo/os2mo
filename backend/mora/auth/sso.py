#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

import flask
import flask_saml

from . import base
from . import tokens
from .. import settings

basedir = os.path.dirname(__file__)


def acs(sender, subject, attributes, auth):
    """Custom assertion consumer service for use with flask_saml"""
    flask.session[base.TOKEN_KEY] = tokens.pack(auth.xmlstr)
    flask.session['username'] = attributes[settings.SSO_SAML_USERNAME_ATTR][0]


def init_app(app):
    """
    Initalize flask_saml, creating the associated endpoints
    :param app: The flask app
    """
    app.config.update({
        'SAML_METADATA_URL': settings.SSO_SAML_METADATA_URL,
        'SAML_IDP_INSECURE': settings.SAML_IDP_INSECURE,
        'SAML_KEY_FILE': settings.SAML_KEY_FILE,
        'SAML_CERT_FILE': settings.SAML_CERT_FILE,
        'SAML_AUTHN_REQUESTS_SIGNED': settings.SAML_AUTHN_REQUESTS_SIGNED,
    })

    flask_saml.FlaskSAML(app)

    flask_saml.saml_authenticated.connect(acs, app)
