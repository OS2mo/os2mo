# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from fastapi import Request
from onelogin.saml2.idp_metadata_parser import OneLogin_Saml2_IdPMetadataParser

from mora.settings import app_config

logger = logging.getLogger(__name__)


def _generate_url_for(schema: str, host: str, endpoint: str, request: Request):
    return "{}://{}{}".format(schema, host, endpoint)


def _get_saml_sp_settings(request):
    config = app_config.copy()

    name_id_format = config.setdefault(
        "SAML_NAME_ID_FORMAT", "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
    )
    force_https = config.setdefault("SAML_FORCE_HTTPS", False)

    sp_domain = config.setdefault("SAML_SP_DOMAIN", None)

    cert_file = config.setdefault("SAML_CERT_FILE", None)
    key_file = config.setdefault("SAML_KEY_FILE", None)
    requests_signed = config.setdefault("SAML_REQUESTS_SIGNED", False)

    url_scheme = "https" if force_https else "http"
    entity_id = _generate_url_for(url_scheme, sp_domain, "/saml/metadata/", request)
    acs = _generate_url_for(url_scheme, sp_domain, "/saml/acs/", request)
    sls = _generate_url_for(url_scheme, sp_domain, "/samo/sls/", request)

    sp_settings = {
        "sp": {
            "entityId": entity_id,
            "assertionConsumerService": {
                "url": acs,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST",
            },
            "singleLogoutService": {
                "url": sls,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect",
            },
            "NameIDFormat": name_id_format,
        }
    }

    if requests_signed:
        try:
            with open(cert_file, "r") as cf:
                cert = cf.read()
        except OSError:
            logger.exception("Unable to read cert file {}".format(cert_file))
            raise

        try:
            with open(key_file, "r") as kf:
                key = kf.read()
        except OSError:
            logger.exception("Unable to read key file {}".format(key_file))
            raise

        sp_settings["sp"].update({"x509cert": cert, "privateKey": key})

    return sp_settings


def _get_saml_idp_settings():
    config = app_config.copy()

    saml_idp_metadata_file = config.setdefault("SAML_IDP_METADATA_FILE", None)
    saml_idp_metadata_url = config.setdefault("SAML_IDP_METADATA_URL", None)
    insecure = config.setdefault("SAML_IDP_INSECURE", False)

    if saml_idp_metadata_file:
        with open(saml_idp_metadata_file, "r") as idp:
            idp_settings = OneLogin_Saml2_IdPMetadataParser.parse(idp.read())
    else:
        idp_settings = OneLogin_Saml2_IdPMetadataParser.parse_remote(
            saml_idp_metadata_url, validate_cert=not insecure
        )

    return idp_settings


def _get_saml_security_settings():
    config = app_config.copy()

    signature_algorithm = config.setdefault(
        "SAML_SIGNATURE_ALGORITHM", "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
    )
    digest_algorithm = config.setdefault(
        "SAML_DIGEST_ALGORITHM", "http://www.w3.org/2001/04/xmlenc#sha256"
    )
    requests_signed = config.setdefault("SAML_REQUESTS_SIGNED", False)
    want_name_id = config.setdefault("SAML_WANT_NAME_ID", True)
    want_attribute_statement = config.setdefault("SAML_WANT_ATTRIBUTE_STATEMENT", False)
    requested_authn_context = config.setdefault("SAML_REQUESTED_AUTHN_CONTEXT", True)
    requested_authn_context_comparison = config.setdefault(
        "SAML_REQUESTED_AUTHN_CONTEXT_COMPARISON", "exact"
    )

    return {
        "security": {
            "authnRequestsSigned": requests_signed,
            "logoutRequestSigned": requests_signed,
            "signatureAlgorithm": signature_algorithm,
            "digestAlgorithm": digest_algorithm,
            "wantNameId": want_name_id,
            "wantAttributeStatement": want_attribute_statement,
            "requestedAuthnContext": requested_authn_context,
            "requestedAuthnContextComparison": requested_authn_context_comparison,
        }
    }


def get_saml_settings(request: Request, idp=True):
    """Generate the internal config file for OneLogin"""
    config = app_config.copy()
    strict = config.setdefault("SAML_STRICT", True)
    debug = config.setdefault("SAML_DEBUG", False)

    s = {"strict": strict, "debug": debug}

    if idp:
        s.update(_get_saml_idp_settings())
    s.update(_get_saml_security_settings())
    s.update(_get_saml_sp_settings(request))

    return s
