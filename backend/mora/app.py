#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import typing

import flask
import flask_saml_sso
import werkzeug

from . import exceptions
from . import service
from . import settings
from . import util
from .auth import base
from .integrations import serviceplatformen

basedir = os.path.dirname(__file__)
templatedir = os.path.join(basedir, 'templates')
distdir = os.path.join(basedir, '..', '..', 'frontend', 'dist')


def create_app(overrides: typing.Dict[str, typing.Any] = None):
    '''Create and return a Flask app instance for MORA.

    :param dict overrides: Settings to override prior to extension
                           instantiation.

    '''
    app = flask.Flask(__name__, root_path=distdir, template_folder=templatedir)

    app.config.from_object(settings)

    app.url_map.converters['uuid'] = util.StrUUIDConverter

    if overrides is not None:
        app.config.update(overrides)

    # Initialize SSO and Session
    flask_saml_sso.init_app(app)

    base.blueprint.before_request(flask_saml_sso.check_saml_authentication)
    app.register_blueprint(base.blueprint)

    for blueprint in service.blueprints:
        blueprint.before_request(flask_saml_sso.check_saml_authentication)
        app.register_blueprint(blueprint)

    @app.errorhandler(Exception)
    def handle_invalid_usage(error):
        """
        Handles errors in case an exception is raised.

        :param error: The error raised.
        :return: JSON describing the problem and the apropriate status code.
        """

        if not isinstance(error, werkzeug.routing.RoutingException):
            util.log_exception('unhandled exception')

        if not isinstance(error, werkzeug.exceptions.HTTPException):
            error = exceptions.HTTPException(
                description=str(error),
            )

        return error.get_response(flask.request.environ)

    # We serve index.html and favicon.ico here. For the other static files,
    # Flask automatically adds a static view that takes a path relative to the
    # `flaskr/static` directory.

    @app.route("/")
    @app.route("/<path:path>")
    def index(path=""):
        """Serve index.html on `/` and unknown paths.
        """
        return flask.send_file("index.html")

    @app.route("/favicon.ico")
    def favicon(path=""):
        """Serve favicon.ico on `/favicon.ico`.
        """
        return flask.send_file("favicon.ico")

    @app.route("/service/<path:path>")
    def no_such_endpoint(path=""):
        """Throw an error on unknown `/service/` endpoints.
        """
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    serviceplatformen.check_config(app)
    return app
