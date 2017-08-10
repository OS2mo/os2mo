#
# Copyright (c) 2017, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import base64
import datetime
import io
import xml.etree.ElementTree
import zlib

import iso8601
import flask
import requests

from . import settings
from . import util

IDP_TEMPLATES = {
    'adfs': 'adfs-soap-request.xml',
    'wso2': 'wso2-soap-request.xml',
}

XML_NAMESPACES = {
    'soapenv': 'http://www.w3.org/2003/05/soap-envelope',
    'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'dsig': 'http://www.w3.org/2000/09/xmldsig#',
    'canon': 'http://www.w3.org/2001/10/xml-exc-c14n#',
}


def _gzipstring(s):
    compressor = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                  zlib.DEFLATED, 16 + zlib.MAX_WBITS)

    return compressor.compress(s) + compressor.flush()


def _pack(s):
    return b'saml-gzipped ' + base64.standard_b64encode(_gzipstring(s))


def get_token(username, passwd, raw=False, insecure=None):
    '''Request a SAML authentication token from the given host and endpoint.

    Windows Server typically returns a 500 Internal Server Error on
    authentication errors; this function simply raises a
    httplib.HTTPError in these cases. In other cases, it returns a
    KeyError. WSO2 tends to yield more meaningful errors.

    '''

    for prefix, uri in XML_NAMESPACES.items():
        xml.etree.ElementTree.register_namespace(prefix, uri)

    if not settings.SAML_IDP_URL or not settings.SAML_IDP_TYPE:
        return None, 'N/A'

    if insecure is None:
        insecure = settings.SAML_IDP_INSECURE

    created = util.now()
    expires = created + datetime.timedelta(hours=1)
    template_name = IDP_TEMPLATES[settings.SAML_IDP_TYPE]

    t = flask.current_app.jinja_env.get_template(template_name)
    requestxml = t.render(
        username=username,
        password=passwd,
        endpoint=settings.SAML_ENTITY_ID,
        idp_url=settings.SAML_IDP_URL,
        created=created.isoformat(),
        expires=expires.isoformat(),
    )

    with requests.post(
            settings.SAML_IDP_URL,
            data=requestxml, verify=not insecure, headers={
                'Content-Type': 'application/soap+xml; charset=utf-8',
            },
            stream=True,
    ) as resp:
        ct = resp.headers.get('Content-Type', '').split(';')[0]

        if not resp.ok and ct != 'application/soap+xml':
            resp.raise_for_status()

        doc = xml.etree.ElementTree.parse(resp.raw)

    errormsg = doc.findtext('.//soapenv:Reason/soapenv:Text',
                            None, XML_NAMESPACES)

    if not resp.ok or errormsg:
        raise PermissionError(errormsg)

    tokens = doc.findall('.//saml:Assertion', XML_NAMESPACES)

    if len(tokens) != 1:
        raise ValueError(
            'one single token expected, but got {}'.format(len(tokens)),
        )

    doc._setroot(tokens[0])

    conditions = doc.find('.//saml:Conditions', XML_NAMESPACES)
    expiry = iso8601.parse_date(conditions.attrib['NotBefore'])

    with io.BytesIO() as buf:
        doc.write(buf)
        assertion = buf.getvalue()

    return expiry, assertion if raw else _pack(assertion)


__all__ = ('get_token')
