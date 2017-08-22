#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import flask
import requests.auth

from . import tokens

ASSERTIONS = dict()

__all__ = (
    'SAMLAuth',
    'login',
    'logout',
)

COOKIE_NAME = 'MO-Token'


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


def login(username):
    # TODO: remember me?
    password = flask.request.get_json()['password']

    try:
        assertion = tokens.get_token(username, password)
    except requests.exceptions.ConnectionError as e:
        flask.current_app.logger.exception(
            'AN ERROR OCCURRED in %r',
            flask.request.full_path,
        )

        raise PermissionError('connection failed')

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


def logout():
    response = flask.make_response()
    response.delete_cookie(COOKIE_NAME)

    return response
