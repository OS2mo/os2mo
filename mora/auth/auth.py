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

from . import tokens
from .. import exceptions
from .. import settings
from .. import util

__all__ = (
    'SAMLAuth',
    'login',
    'logout',
)

COOKIE_NAME = 'MO-Token'

basedir = os.path.dirname(__file__)

blueprint = flask.Blueprint('authentication', __name__,
                            url_prefix='/service', root_path=basedir)


class SAMLAuth(requests.auth.AuthBase):
    def __init__(self, assertion=None):
        self.assertion = assertion

    def __call__(self, r):
        if self.assertion:
            assertion = self.assertion
        elif flask.session.get(COOKIE_NAME):
            assertion = flask.session[COOKIE_NAME]
        else:
            assertion = None

        if assertion:
            r.headers['Authorization'] = assertion

        return r


@blueprint.route('/user', methods=['GET'])
def get_user():
    '''Get the currently logged in user

    .. :quickref: Authentication; Get user

    :return: The username of the user who is currently logged in.
    '''

    username = flask.session.get('username') or 'N/A'

    return flask.jsonify(username)


@blueprint.route('/user/login', methods=['POST'])
def login():
    '''Attempt a login as the given user name. The internals of this login
    will be kept from the JavaScript by using httpOnly cookies.

    .. :quickref: Authentication; Log in

    :statuscode 200: The login succeeded.
    :statuscode 401: The login failed.

    :<json string username: AD username and domain
                            (format: <username>@<addomain>)
    :<json string password: The password of the user.
    :<json boolean rememberme: Whether to persist the login ---
        currently ignored.

    :>json string user: The name of the user.
    '''

    # TODO: remember me?
    json_payload = flask.request.get_json()

    username = json_payload.get("username")
    password = json_payload.get("password")

    try:
        assertion = tokens.get_token(username, password)
    except requests.exceptions.ConnectionError as e:
        util.log_exception(e)

        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_CONNECTION_FAILED)

    flask.session['username'] = username

    if assertion:
        flask.session[COOKIE_NAME] = assertion

    return flask.make_response()


@blueprint.route('/logout', methods=['POST'])
def logout():
    '''Attempt to log out

    .. :quickref: Authentication; Log out

    :return: Nothing.

    :statuscode 200: The logout succeeded --- which it almost always does.
    '''

    flask.session.clear()
    return flask.make_response()


@blueprint.route('/login', methods=['GET'])
def get_login():
    """
    Direct user towards appropriate login page, given the chosen auth method
    """
    redirect = flask.request.args.get('redirect')
    if settings.AUTH and not flask.session.get(COOKIE_NAME):
        if settings.AUTH == 'sso':
            return flask.redirect(flask.url_for('login', next=redirect))
        elif settings.AUTH == 'token':
            return flask.redirect('/login?redirect={}'.format(redirect))
    return flask.send_file('index.html')
