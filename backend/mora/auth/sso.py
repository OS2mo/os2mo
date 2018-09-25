#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import base64
import contextlib
import functools
import os
from urllib import parse

import flask
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser
from onelogin.saml2.response import OneLogin_Saml2_Response
from onelogin.saml2.xml_utils import OneLogin_Saml2_XML

from mora.exceptions import HTTPException, ErrorCodes
from . import base

basedir = os.path.dirname(__file__)

blueprint = flask.Blueprint('sso', __name__, static_url_path='',
                            url_prefix='/saml')


def _get_saml_settings(app):
    """Generate the internal config file for OneLogin"""
    insecure = app.config['SAML_IDP_INSECURE']
    cert_file = app.config['SAML_CERT_FILE']
    key_file = app.config['SAML_KEY_FILE']
    requests_signed = app.config['SAML_REQUESTS_SIGNED']
    saml_idp_metadata_url = app.config['SAML_IDP_METADATA_URL']
    saml_idp_metadata_file = app.config['SAML_IDP_METADATA_FILE']

    if saml_idp_metadata_file:
        with open(saml_idp_metadata_file, 'r') as idp:
            remote = OneLogin_Saml2_IdPMetadataParser.parse(idp.read())
    else:
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


def _prepare_flask_request():
    """Construct OneLogin-friendly request object from Flask request"""
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


def _prepare_saml_auth(func):
    """Decorator to create and initialize the OneLogin SAML2 Auth client"""
    @functools.wraps(func)
    def wrapper():
        app = flask.current_app
        config = app.extensions.get('saml')
        if not config:
            config = _get_saml_settings(app)
            app.extensions['saml'] = config
        req = _prepare_flask_request()
        auth = OneLogin_Saml2_Auth(req, config)
        return func(auth)
    return wrapper


@blueprint.route('/metadata/')
@_prepare_saml_auth
def metadata(auth):
    """
    SAML metadata endpoint

    Exposes XML configuration of the Service Provider
    """
    settings = auth.get_settings()
    sp_metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(sp_metadata)

    if errors:
        raise HTTPException(
            ErrorCodes.E_SAML_AUTH_ERROR,
            message=", ".join(errors))
    resp = flask.make_response(sp_metadata, 200)
    resp.headers['Content-Type'] = 'text/xml'
    return resp


@blueprint.route('/sso/')
@_prepare_saml_auth
def sso(auth):
    """
    Initiate SAML single sign-on

    Redirects user to IdP login page specified in metadata
    """
    return_to = flask.request.args.get(
        'next', flask.url_for('root', _external=True))
    login = auth.login(return_to=return_to)
    return flask.redirect(login)


@blueprint.route('/acs/', methods=['POST'])
@_prepare_saml_auth
def acs(auth):
    """
    Assertion Consumer Service endpoint

    Called by IdP with SAML assertion when authentication has been performed
    """
    with _allow_duplicate_attribute_names():
        auth.process_response()
    errors = auth.get_errors()

    if errors:
        raise HTTPException(
            ErrorCodes.E_SAML_AUTH_ERROR,
            message=", ".join(errors))
    # TODO: Kill this when LoRa has better auth
    res = base64.b64decode(flask.request.form['SAMLResponse'])
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


@blueprint.route('/slo/')
@_prepare_saml_auth
def slo(auth):
    """
    Initiate SAML single logout

    Redirects user to IdP SLO specified in metadata
    """
    name_id = flask.session.get('samlNameId')
    session_index = flask.session.get('samlSessionIndex')
    logout = auth.logout(name_id=name_id, session_index=session_index)
    return flask.redirect(logout)


@blueprint.route('/sls/')
@_prepare_saml_auth
def sls(auth):
    """
    Single Logout Service

    Consumes LogoutResponse from IdP when logout has been performed, and
    sends user back to landing page
    """
    url = auth.process_slo(delete_session_cb=lambda: flask.session.clear())
    errors = auth.get_errors()
    if errors:
        raise HTTPException(
            ErrorCodes.E_SAML_AUTH_ERROR,
            message=", ".join(errors))
    if url is not None:
        return flask.redirect(url)
    return flask.redirect('/')


@contextlib.contextmanager
def _allow_duplicate_attribute_names():
    """
    Patches get_attributes on OneLogin Response object to handle duplicate
    attribute names
    see: https://github.com/onelogin/python3-saml/issues/39
    """
    def _get_attributes_patched(self):
        """
        Gets the Attributes from the AttributeStatement element.
        EncryptedAttributes are not supported

        XXX: Fix for duplicate attribute keys
        see: https://github.com/onelogin/python3-saml/issues/39
        """
        attributes = {}
        attribute_nodes = self._OneLogin_Saml2_Response__query_assertion(
            '/saml:AttributeStatement/saml:Attribute')
        for attribute_node in attribute_nodes:
            attr_name = attribute_node.get('Name')
            # XXX: Fix for duplicate attribute keys
            # if attr_name in attributes.keys():
            #     raise OneLogin_Saml2_ValidationError(
            #         'Found an Attribute element with duplicated Name',
            #         OneLogin_Saml2_ValidationError.DUPLICATED_ATTRIBUTE_NAME_FOUND
            #     )

            values = []
            for attr in attribute_node.iterchildren(
                    '{%s}AttributeValue' % OneLogin_Saml2_Constants.NSMAP[
                        'saml']):
                attr_text = OneLogin_Saml2_XML.element_text(attr)
                if attr_text:
                    attr_text = attr_text.strip()
                    if attr_text:
                        values.append(attr_text)

                # Parse any nested NameID children
                for nameid in attr.iterchildren(
                        '{%s}NameID' % OneLogin_Saml2_Constants.NSMAP[
                            'saml']):
                    values.append({
                        'NameID': {
                            'Format': nameid.get('Format'),
                            'NameQualifier': nameid.get('NameQualifier'),
                            'value': nameid.text
                        }
                    })
            # XXX: Fix for duplicate attribute keys
            attributes[attr_name] = attributes.setdefault(
                attr_name, []) + values
        return attributes

    app = flask.current_app
    if app.config['SAML_DUPLICATE_ATTRIBUTES']:
        orig_fn = OneLogin_Saml2_Response.get_attributes
        OneLogin_Saml2_Response.get_attributes = _get_attributes_patched
        yield
        OneLogin_Saml2_Response.get_attributes = orig_fn
    else:
        yield
