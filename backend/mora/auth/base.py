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
import base64
import os
import zlib

import flask
import requests.auth

__all__ = (
    'SAMLAuth',
    'get_user',
    'pack'
)

TOKEN_KEY = 'MO-Token'

basedir = os.path.dirname(__file__)

blueprint = flask.Blueprint('authentication', __name__,
                            url_prefix='/service', root_path=basedir)


class SAMLAuth(requests.auth.AuthBase):
    def __init__(self, assertion=None):
        self.assertion = assertion

    def __call__(self, r):
        if self.assertion:
            assertion = self.assertion
        elif flask.session:
            assertion = flask.session.get(TOKEN_KEY)
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

    username_attr = flask.current_app.config['SAML_USERNAME_ATTR']
    try:
        username = flask.session.get('samlUserdata').get(username_attr)[0]
    except (AttributeError, IndexError):
        username = None

    return flask.jsonify(username)


def _gzipstring(s):
    compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                  zlib.DEFLATED, 16 + zlib.MAX_WBITS)

    return compressor.compress(s) + compressor.flush()


def pack(s):
    return b'saml-gzipped ' + base64.standard_b64encode(_gzipstring(s))
