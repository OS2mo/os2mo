#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import os
import traceback

import flask

from . import auth
from . import cli
from . import exceptions
from . import service
from . import util

basedir = os.path.dirname(__file__)
templatedir = os.path.join(basedir, 'templates')
distdir = os.path.join(basedir, '..', 'dist')

app = flask.Flask(__name__, root_path=distdir, template_folder=templatedir)
app.cli = cli.group

app.register_blueprint(auth.blueprint)

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

    return exceptions.HTTPException(
        description=str(error),
        error_key=exceptions.ErrorCodes.E_UNKNOWN,
        stacktrace=traceback.format_exc(),
    ).get_response()


@app.route('/')
@app.route('/<path:path>')
def root(path=''):
    if path.split('/', 1)[0] == 'service':
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT)

    return flask.send_file('index.html')
