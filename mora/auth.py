#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import functools

try:
    import secrets
except ImportError:
    from .compat import secrets

import flask

USER_TOKENS = dict()

# Yes, this is insecure, but it'll do for a demo
USER_PASSWORDS = {
    'admin': 'hnBZvxr7tToR',
}

__all__ = (
    'requires_auth',
    'get_user',
    'login',
    'logout',
)


def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = flask.request.headers.get('X-AUTH-TOKEN')
        if token and token in USER_TOKENS:
            return f(*args, **kwargs)
        else:
            return '', 401
    return decorated


def login(username, password):
    if USER_PASSWORDS.get(username) == password:
        token = secrets.token_urlsafe()

        USER_TOKENS[token] = username

        return {
            "user": username,
            "token": token,
            "role": [],
        }
    else:
        return None


def logout(user, token):
    try:
        return USER_TOKENS.pop(token) == user
    except KeyError:
        return False
