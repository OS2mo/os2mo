#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import json
import os

import flask

from . import api
from . import auth
from . import cli

basedir = os.path.dirname(__file__)
staticdir = os.path.join(basedir, 'static')

app = flask.Flask(__name__, static_url_path='')

cli.load_cli(app)
app.register_blueprint(api.blueprint)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    """
    Handles errors in case an exception is raised.

    :param error: The error raised.
    :return: JSON describing the problem and the apropriate status code.
    """
    data = flask.request.get_json()

    if data:
        if 'password' in data:
            data['password'] = 'X' * 8

        flask.current_app.logger.exception(
            'AN ERROR OCCURRED in %r:\n%s',
            flask.request.full_path,
            json.dumps(data, indent=2),
        )
    else:
        flask.current_app.logger.exception(
            'AN ERROR OCCURRED in %r',
            flask.request.full_path,
        )

    if isinstance(error, ValueError):
        status_code = 400
    elif isinstance(error, (KeyError, IndexError)):
        status_code = 404
    elif isinstance(error, PermissionError):
        status_code = 401
    else:
        status_code = 500

    return flask.jsonify({
        'status': status_code,
        'message': (
            error.args[0]
            if error.args and len(error.args) == 1
            else error.args
        )
    }), status_code


@app.route('/')
def root():
    return flask.send_from_directory(staticdir, 'index.html')


@app.route('/scripts/<path:path>')
def send_scripts(path):
    return flask.send_from_directory(staticdir, os.path.join('scripts', path))


@app.route('/styles/<path:path>')
def send_styles(path):
    return flask.send_from_directory(staticdir, os.path.join('styles', path))


@app.route('/service/user/<user>/login', methods=['POST'])
def login(user):
    return auth.login(user)


@app.route('/service/user/<user>/logout', methods=['POST'])
def logout(user):
    return auth.logout()


@app.route('/acl/', methods=['POST', 'GET'])
def acl():
    return flask.jsonify([])
