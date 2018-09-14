#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import functools
import os
from urllib import parse

import flask
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from . import base

basedir = os.path.dirname(__file__)

blueprint = flask.Blueprint('sso', __name__, static_url_path='',
                            url_prefix='/saml')


def get_saml_settings(app):
    config = app.config

    insecure = config['SAML_IDP_INSECURE']
    cert_file = config['SAML_CERT_FILE']
    key_file = config['SAML_KEY_FILE']
    requests_signed = config['SAML_REQUESTS_SIGNED']
    saml_idp_metadata_url = config['SAML_IDP_METADATA_URL']

    remote = OneLogin_Saml2_IdPMetadataParser.parse_remote(
        saml_idp_metadata_url,
        validate_cert=not insecure
    )

    s = {
        "strict": True,
        "debug": True,
        "sp": {
            "entityId": flask.url_for('sso.metadata', _external=True),
            "assertionConsumerService": {
                "url": flask.url_for('sso.acs', _external=True),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "singleLogoutService": {
                "url": flask.url_for('sso.sls', _external=True),
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
        },
        "security": {
            "authnRequestsSigned": requests_signed,
            "logoutRequestSigned": requests_signed
        }
    }

    s.setdefault('sp', {}).update(remote.get('sp'))
    s.setdefault('idp', {}).update(remote.get('idp'))

    if requests_signed:
        with open(cert_file, 'r') as cf:
            cert = cf.read()
        with open(key_file, 'r') as kf:
            key = kf.read()

        s['sp'].update({
            "x509cert": cert,
            "privateKey": key
        })

    return s


def prepare_flask_request():
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    url_data = parse.urlparse(flask.request.url)
    return {
        'https': 'on' if flask.request.scheme == 'https' else 'off',
        'http_host': flask.request.host,
        'server_port': url_data.port,
        'script_name': flask.request.path,
        'get_data': flask.request.args.copy(),
        'post_data': flask.request.form.copy()
    }


def init_saml_auth(func):
    @functools.wraps(func)
    def wrapper():
        app = flask.current_app
        config = app.extensions.get('saml')
        if not config:
            config = get_saml_settings(app)
            app.extensions['saml'] = config
        req = prepare_flask_request()
        auth = OneLogin_Saml2_Auth(req, config)
        return func(auth)
    return wrapper


@blueprint.route('/metadata/')
@init_saml_auth
def metadata(auth):
    settings = auth.get_settings()
    sp_metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(sp_metadata)

    if len(errors) == 0:
        resp = flask.make_response(sp_metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
        return resp
    else:
        return flask.jsonify(errors)


@blueprint.route('/sso/')
@init_saml_auth
def sso(auth):
    return_to = flask.request.args.get(
        'next', flask.url_for('root', _external=True))
    login = auth.login(return_to=return_to)
    return flask.redirect(login)


@blueprint.route('/acs/', methods=['POST'])
@init_saml_auth
def acs(auth):
    auth.process_response()
    errors = auth.get_errors()

    if len(errors) == 0:
        # TODO: Kill this when LoRa has better auth
        res = OneLogin_Saml2_Utils.b64decode(
            flask.request.form['SAMLResponse'])
        flask.session[base.TOKEN_KEY] = base.pack(res)

        flask.session['samlUserdata'] = auth.get_attributes()
        flask.session['samlNameId'] = auth.get_nameid()
        flask.session['samlSessionIndex'] = auth.get_session_index()

        if 'RelayState' in flask.request.form:
            return flask.redirect(auth.redirect_to(
                flask.request.form['RelayState'])
            )
        else:
            return flask.redirect('/')
    else:
        return flask.jsonify(errors)


@blueprint.route('/slo/')
@init_saml_auth
def slo(auth):
    name_id = None
    session_index = None
    if 'samlNameId' in flask.session:
        name_id = flask.session['samlNameId']
    if 'samlSessionIndex' in flask.session:
        session_index = flask.session['samlSessionIndex']
    return flask.redirect(auth.logout(
        name_id=name_id, session_index=session_index))


@blueprint.route('/sls/')
@init_saml_auth
def sls(auth):
    url = auth.process_slo(delete_session_cb=delete_session_callback)
    errors = auth.get_errors()
    if len(errors) == 0:
        if url is not None:
            return flask.redirect(url)
        return flask.redirect('/')
    else:
        return flask.jsonify(errors)


def delete_session_callback():
    flask.session.clear()
