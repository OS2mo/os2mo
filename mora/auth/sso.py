#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import contextlib
import os

import flask
import flask_saml
import requests

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
    })

    with _flask_saml_context_manager():
        flask_saml.FlaskSAML(app)

    flask_saml.saml_authenticated.connect(acs, app)


@contextlib.contextmanager
def _flask_saml_context_manager():
    if settings.SAML_IDP_INSECURE:
        orig_fn = flask_saml._get_metadata
        flask_saml._get_metadata = _get_metadata_insecure
        yield
        flask_saml._get_metadata = orig_fn
    else:
        yield


def _get_metadata_insecure(metadata_url):
    """A optionally insecure version of _get_metadata from flask_saml.py"""
    response = requests.get(
        metadata_url, verify=not settings.SAML_IDP_INSECURE)
    if response.status_code != 200:
        exc = RuntimeError(
            'Unexpected Status Code: {0}'.format(response.status_code))
        exc.response = response
        raise exc
    return response.text
