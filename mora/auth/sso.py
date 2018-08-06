import os

import flask
import flask_saml

from . import auth as moauth
from . import tokens
from .. import settings

basedir = os.path.dirname(__file__)


def acs(sender, subject, attributes, auth):
    """Custom assertion consumer service (acs) for use with flask_saml"""
    flask.session[moauth.COOKIE_NAME] = tokens.pack(str.encode(str(auth.assertion)))
    flask.session['username'] = subject


def init_app(app):
    """
    Initalize flask_saml, creating the associated endpoints
    :param app: The flask app
    """
    app.config.update({
        'SAML_METADATA_URL': settings.SSO_SAML_METADATA_URL,
    })

    flask_saml.FlaskSAML(app)

    flask_saml.saml_authenticated.connect(acs, app)
