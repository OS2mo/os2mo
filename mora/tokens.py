#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import base64
import datetime
import requests
import zlib

from lxml import etree
import flask

from . import settings
from . import util

IDP_TEMPLATES = {
    'adfs': 'adfs-soap-request.xml',
    'wso2': 'wso2-soap-request.xml',
}


def _gzipstring(s):
    compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                  zlib.DEFLATED, 16 + zlib.MAX_WBITS)

    return compressor.compress(s) + compressor.flush()


def get_token(username, passwd, pretty_print=False,
              insecure=None):
    '''Request a SAML authentication token from the given host and endpoint.

    Windows Server typically returns a 500 Internal Server Error on
    authentication errors; this function simply raises a
    httplib.HTTPError in these cases. In other cases, it returns a
    KeyError. WSO2 tends to yield more meaningful errors.

    '''

    if not settings.SAML_IDP_URL or not settings.SAML_IDP_TYPE:
        return 'N/A'

    if insecure is None:
        insecure = settings.SAML_IDP_INSECURE

    created = util.now()
    expires = created + datetime.timedelta(hours=1)
    template_name = IDP_TEMPLATES[settings.SAML_IDP_TYPE]

    t = flask.current_app.jinja_env.get_template(template_name)
    xml = t.render(
        username=username,
        password=passwd,
        endpoint=settings.SAML_ENTITY_ID,
        idp_url=settings.SAML_IDP_URL,
        created=created.isoformat(),
        expires=expires.isoformat(),
    )

    resp = requests.post(
        settings.SAML_IDP_URL,
        data=xml, verify=not insecure, headers={
            'Content-Type': 'application/soap+xml; charset=utf-8',
        },
    )

    if not resp.ok:
        # do something?
        ct = resp.headers.get('Content-Type', '').split(';')[0]

        if resp.status_code == 500 and ct == 'application/soap+xml':
            doc = etree.fromstring(resp.content)

            raise PermissionError(' '.join(doc.itertext('{*}Text')))

        resp.raise_for_status()

    doc = etree.fromstring(resp.content)

    if doc.find('./{*}Body/{*}Fault') is not None:
        raise PermissionError(' '.join(doc.itertext('{*}Text')))

    tokens = doc.findall('.//{*}RequestedSecurityToken/{*}Assertion')

    if len(tokens) == 0:
        raise ValueError('no tokens found - is the endpoint correct?')
    if len(tokens) > 1:
        raise ValueError('too many tokens found')

    assert len(tokens) == 1

    if pretty_print:
        return etree.tostring(tokens[0], pretty_print=pretty_print)
    else:
        text = \
            base64.standard_b64encode(_gzipstring(etree.tostring(tokens[0])))

        return b'saml-gzipped ' + text


__all__ = ('get_token')
