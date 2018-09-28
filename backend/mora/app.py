
#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import typing

import flask
import werkzeug
import flask_session

from . import exceptions
from . import service
from . import settings
from . import util
from .auth import base, sso

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

    if overrides is not None:
        app.config.update(overrides)

    flask_session.Session(app)

    app.register_blueprint(base.blueprint)
    app.register_blueprint(sso.blueprint)

    for blueprint in service.blueprints:
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

    @app.route('/')
    @app.route('/<path:path>')
    def root(path=''):
        if path.split('/', 1)[0] == 'service':
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT)

        return flask.send_file('index.html')

    return app


# create a default instance for backwards compatibility
app = create_app()
