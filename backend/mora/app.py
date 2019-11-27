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

from mora import __version__
from mora.triggers.internal import amqp_trigger
from mora import health
from . import exceptions
from . import lora
from . import service
from . import settings
from . import util
from .auth import base
from .integrations import serviceplatformen
from . import triggers

basedir = os.path.dirname(__file__)
templatedir = os.path.join(basedir, 'templates')
distdir = os.path.join(basedir, '..', '..', 'frontend', 'dist')


def create_app(overrides: typing.Dict[str, typing.Any] = None):
    '''Create and return a Flask app instance for MORA.

    :param dict overrides: Settings to override prior to extension
                           instantiation.

    '''
    app = flask.Flask(__name__, root_path=distdir, template_folder=templatedir)

    app.config.update(settings.app_config)

    app.url_map.converters['uuid'] = util.StrUUIDConverter

    if overrides is not None:
        app.config.update(overrides)

    # Initialize SSO and Session
    flask_saml_sso.init_app(app)

    base.blueprint.before_request(flask_saml_sso.check_saml_authentication)
    app.register_blueprint(base.blueprint)
    app.register_blueprint(health.blueprint)

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

    @app.route("/version/")
    def version():
        lora_version = lora.get_version()
        return flask.jsonify({
            "mo_version": __version__,
            "lora_version": lora_version,
        })

    @app.before_first_request
    def register_triggers():
        """Register all triggers on the app object.

        The reason we cannot do this when creating the app object is
        that the amqp trigger tries to connect to rabbitmq when
        registrered. App objects are also created when we wait for
        rabbitmq in the docker entrypoint. A bit of a code smell/design
        flaw, that we do not know how to fix yet.
        """
        amqp_trigger.register()

    # We serve index.html and favicon.ico here. For the other static files,
    # Flask automatically adds a static view that takes a path relative to the
    # `flaskr/static` directory.

    @app.route("/")
    @app.route("/organisation/")
    @app.route("/organisation/<path:path>")
    @app.route("/medarbejder/")
    @app.route("/medarbejder/<path:path>")
    @app.route("/hjaelp/")
    @app.route("/organisationssammenkobling/")
    @app.route("/forespoergsler/")
    @app.route("/tidsmaskine/")
    def index(path=""):
        """Serve index.html on `/` and unknown paths.
        """
        return flask.send_file("index.html")

    @app.route("/favicon.ico")
    def favicon():
        """Serve favicon.ico on `/favicon.ico`.
        """
        return flask.send_file("favicon.ico")

    @app.route("/service/<path:path>")
    def no_such_endpoint(path=""):
        """Throw an error on unknown `/service/` endpoints.
        """
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    serviceplatformen.check_config(app)
    triggers.register(app)

    return app
