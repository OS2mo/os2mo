#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Authentication
--------------

This section describes how to authenticate with MO. The API is work in
progress.

'''

import os

import flask
import requests.auth

from . import exceptions
from . import tokens

__all__ = (
    'SAMLAuth',
    'login',
    'logout',
)

COOKIE_NAME = 'MO-Token'

basedir = os.path.dirname(__file__)

blueprint = flask.Blueprint('authentication', __name__, url_prefix='/mo',
                            root_path=basedir)


class SAMLAuth(requests.auth.AuthBase):
    def __init__(self, assertion=None):
        self.assertion = assertion

    def __call__(self, r):
        if self.assertion:
            assertion = self.assertion
        elif flask.request:
            assertion = flask.request.cookies.get(COOKIE_NAME)
        else:
            assertion = None

        if assertion:
            r.headers['Authorization'] = assertion

        return r


@blueprint.route('/service/user/<username>/login', methods=['POST'])
def login(username):
    '''Attempt a login as the given user name. The internals of this login
    will be kept from the JavaScript by using httpOnly cookies.

    .. :quickref: Authentication; Log in

    :statuscode 200: The login succeeded.
    :statuscode 401: The login failed.

    :param username: The user ID to login as.

    :<json string password: The password of the user.
    :<json boolean rememberme: Whether to persist the login ---
        currently ignored.

    :>json string user: The name of the user.
    :>json string token: Retained for compatibility with original UI.
    :>json string role: Retained for compatibility with original UI.
    '''

    # TODO: remember me?
    password = flask.request.get_json()['password']

    try:
        assertion = tokens.get_token(username, password)
    except requests.exceptions.ConnectionError as e:
        flask.current_app.logger.exception(
            'AN ERROR OCCURRED in %r',
            flask.request.full_path,
        )

        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_CONNECTION_FAILED)

    resp = flask.jsonify({
        "user": username,
        "token": 'N/A',
        "role": [],
    })

    if assertion:
        resp.set_cookie(
            COOKIE_NAME, assertion,
            secure=flask.request.is_secure,
            httponly=True,
        )
    else:
        resp.delete_cookie(COOKIE_NAME)

    return resp


@blueprint.route('/service/user/<user>/logout', methods=['POST'])
def logout(user=None):
    '''Attempt to log out as the given user name.

    .. :quickref: Authentication; Log out

    :param username: The user ID to logout as.
    :return: Nothing.

    :statuscode 200: The logout succeeded --- which it almost always does.
    '''

    response = flask.make_response()
    response.delete_cookie(COOKIE_NAME)

    return response


@blueprint.route('/acl/', methods=['POST', 'GET'])
def acl():
    '''Obtain the access control lists of the user --- of which we have
    none.

    .. :quickref: Authentication; Deprecated.

    :deprecated: Retained for compatibility with original UI.

    '''

    return flask.jsonify([])
