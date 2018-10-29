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

import flask_saml_sso

__all__ = (
    'get_user',
)

basedir = os.path.dirname(__file__)

blueprint = flask.Blueprint('authentication', __name__,
                            url_prefix='/service', root_path=basedir)


@flask_saml_sso.requires_auth
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
