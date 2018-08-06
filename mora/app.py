#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os

import flask
import werkzeug

from . import cli
from . import exceptions
from . import service
from . import settings
from . import util
from .auth import auth, sso

basedir = os.path.dirname(__file__)
templatedir = os.path.join(basedir, 'templates')
distdir = os.path.join(basedir, '..', 'dist')

app = flask.Flask(__name__, root_path=distdir, template_folder=templatedir)
app.cli = cli.group

app.config.update({
    # Secret key used for default flask.session storage
    # TODO: Remove when/if we move to non cookie-based sessions
    'SECRET_KEY': settings.SECRET_KEY,
})

app.register_blueprint(auth.blueprint)

if settings.AUTH == 'sso':
    sso.init_app(app)

for blueprint in service.blueprints:
    app.register_blueprint(blueprint)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    """
    Handles errors in case an exception is raised.

    :param error: The error raised.
    :return: JSON describing the problem and the apropriate status code.
    """

    util.log_exception('unhandled exception')

    if not isinstance(error, werkzeug.exceptions.HTTPException):
        error = exceptions.HTTPException(
            description=str(error),
        )

    return error.get_response()


@app.route('/')
@app.route('/<path:path>')
def root(path=''):
    if path.split('/', 1)[0] == 'service':
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT)

    return flask.send_file('index.html')

