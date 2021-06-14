# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from urllib import parse

import contextlib
import logging
import os
from fastapi import APIRouter, Request
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.response import OneLogin_Saml2_Response
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.xml_utils import OneLogin_Saml2_XML
from starlette.responses import RedirectResponse, Response

from . import session
from . import settings
from ...settings import app_config

logger = logging.getLogger(__name__)

basedir = os.path.dirname(__file__)

router = APIRouter()

METADATA_CACHE = {}


async def _prepare_fastapi_request(request: Request):
    """Construct OneLogin-friendly request object from FastAPI request"""
    # If server is behind proxies or balancers use the HTTP_X_FORWARDED fields
    force_https = app_config.setdefault("SAML_FORCE_HTTPS", False)
    lowercase_urlencoding = app_config.setdefault("SAML_LOWERCASE_URLENCODING", True)

    https = "on" if request.url.scheme == "https" or force_https else "off"
    return {
        "https": https,
        "http_host": request.url.hostname,
        "server_port": request.url.port,
        "script_name": request.url.path,
        "get_data": request.query_params,
        "lowercase_urlencoding": lowercase_urlencoding,
        "post_data": await request.form(),
    }


async def _get_saml_auth(request: Request, key, idp_enabled):

    global METADATA_CACHE
    saml_settings = METADATA_CACHE.get(key)
    if not saml_settings:
        settings_dict = settings.get_saml_settings(request, idp=idp_enabled)
        saml_settings = OneLogin_Saml2_Settings(
            settings_dict, sp_validation_only=not idp_enabled
        )
        METADATA_CACHE[key] = saml_settings
        logger.debug("SAML Metadata Settings ({}): \n{}".format(key, settings_dict))

    req = await _prepare_fastapi_request(request)

    return OneLogin_Saml2_Auth(req, saml_settings)


def _get_metadata_auth(request: Request):
    return _get_saml_auth(request, "metadata", idp_enabled=False)


def _get_full_auth(request: Request):
    return _get_saml_auth(request, "full", idp_enabled=True)


@router.get("/api-token/")
async def api_token(request: Request):
    """
    Create a new Service user session with associated API token based on
    the rights of the current logged in user.

    If no user is currently logged in, redirect to SSO flow and return here
    """
    logger.debug("API-token called")

    if not request.state.session.get(session.LOGGED_IN):
        qargs = parse.urlencode({"next": request.url_for("sso.api_token")})
        redirect_url = "{}?{}".format(request.url_for("sso.sso"), qargs)

        logger.info("User not logged in, redirecting to {}".format(redirect_url))
        return RedirectResponse(redirect_url)

    session_dict = session.create_session_dict(
        session.SessionType.Service, request.state.session.get(session.SAML_ATTRIBUTES)
    )
    sid = request.state.session_interface.insert_new_session(session_dict)

    return sid


@router.get("/metadata/")
async def metadata(request: Request, response: Response):
    """
    SAML metadata endpoint

    Exposes XML configuration of the Service Provider
    """
    logger.debug("Metadata called")

    auth = await _get_metadata_auth(request)

    settings = auth.get_settings()
    sp_metadata = settings.get_sp_metadata()
    errors = settings.validate_metadata(sp_metadata)

    if errors:
        error_reason = auth.get_last_error_reason()
        if error_reason:
            errors.append(auth.get_last_error_reason())
        logger.error("Metadata Errors: {}".format(errors))
        response.code = 401
        return errors

    logger.debug("XML: \n{}".format(sp_metadata))

    response.headers["Content-Type"] = "text/xml"
    return Response(content=sp_metadata, media_type="application/xml")


@router.get("/sso/")
async def sso(request: Request):
    """
    Initiate SAML single sign-on

    Redirects user to IdP login page specified in metadata
    """
    logger.debug("SSO called")

    auth = await _get_full_auth(request)

    url = str(request.url)[: -len(request.url.path)]
    return_to = request.query_params.get("next", url)
    login = auth.login(return_to=return_to)

    logger.debug("RelayState: {}".format(return_to))
    logger.debug("SSO Request XML: \n{}".format(auth.get_last_request_xml()))

    logger.info('Redirecting to "{}" to initiate login'.format(login))
    return RedirectResponse(login)


@router.post("/acs/")
async def acs(request: Request, response: Response):
    """
    Assertion Consumer Service endpoint

    Called by IdP with SAML assertion when authentication has been performed
    """
    logger.debug("ACS called")

    auth = await _get_full_auth(request)

    with _allow_duplicate_attribute_names():
        auth.process_response()
    errors = auth.get_errors()

    logger.debug("ACS Response XML: \n{}".format(auth.get_last_response_xml()))
    logger.debug("User attributes: {}".format(auth.get_attributes()))

    if errors:
        error_reason = auth.get_last_error_reason()
        if error_reason:
            errors.append(auth.get_last_error_reason())
        logger.error("ACS Errors: {}".format(errors))
        response.code = 401
        return errors

    request.state.session.update(
        session.create_session_dict(session.SessionType.User, auth.get_attributes())
    )
    # Set SSO specific IdP metadata
    request.state.session[session.SAML_NAME_ID] = auth.get_nameid()
    request.state.session[session.SAML_SESSION_INDEX] = auth.get_session_index()

    logger.debug("Name ID: {}".format(auth.get_nameid()))
    logger.debug("SAML Session Index: {}".format(auth.get_session_index()))

    form = await request.form()

    if "RelayState" in form:
        redirect_to = auth.redirect_to(form["RelayState"])
    else:
        redirect_to = "/"

    logger.info('Redirecting back to "{}" after login'.format(redirect_to))
    return RedirectResponse(redirect_to, status_code=303)


@router.get("/slo/")
async def slo(request: Request):
    """
    Initiate SAML single logout

    Redirects user to IdP SLO specified in metadata
    """
    logger.debug("SLO called")

    auth = await _get_full_auth(request)

    name_id = request.state.session.get(session.SAML_NAME_ID)
    session_index = request.state.session.get(session.SAML_SESSION_INDEX)

    logger.debug("Name ID: {}".format(name_id))
    logger.debug("SAML Session Index: {}".format(session_index))

    # If session originates from IdP
    if name_id and session_index:
        logout = auth.logout(name_id=name_id, session_index=session_index)
        logger.debug("SLO Request XML: \n{}".format(auth.get_last_request_xml()))
        redirect_to = logout
    else:
        request.state.session.clear()
        redirect_to = "/"

    logger.info('Redirecting to "{}" to initiate logout'.format(redirect_to))
    return RedirectResponse(redirect_to)


@router.get("/sls/")
async def sls(request: Request, response: Response):
    """
    Single Logout Service

    Consumes LogoutResponse from IdP when logout has been performed, and
    sends user back to landing page
    """
    logger.debug("SLS called")

    auth = await _get_full_auth(request)

    # Process the SLO message received from IdP
    url = auth.process_slo(delete_session_cb=lambda: request.state.session.clear())
    logger.debug("SLS Response XML: \n{}".format(auth.get_last_response_xml()))

    errors = auth.get_errors()
    if errors:
        error_reason = auth.get_last_error_reason()
        if error_reason:
            errors.append(auth.get_last_error_reason())
        logger.error("SLS Errors: {}".format(errors))
        response.code = 401
        return errors
    if url is not None:
        redirect_to = url
    else:
        redirect_to = "/"

    logger.info('Redirecting back to "{}" after logout'.format(redirect_to))
    return RedirectResponse(redirect_to)


@contextlib.contextmanager
def _allow_duplicate_attribute_names():  # pragma: no cover
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
            "/saml:AttributeStatement/saml:Attribute"
        )
        for attribute_node in attribute_nodes:
            attr_name = attribute_node.get("Name")
            # XXX: Fix for duplicate attribute keys
            # if attr_name in attributes.keys():
            #     raise OneLogin_Saml2_ValidationError(
            #         'Found an Attribute element with duplicated Name',
            #         OneLogin_Saml2_ValidationError.DUPLICATED_ATTRIBUTE_NAME_FOUND
            #     )

            values = []
            for attr in attribute_node.iterchildren(
                "{%s}AttributeValue" % OneLogin_Saml2_Constants.NSMAP["saml"]
            ):
                attr_text = OneLogin_Saml2_XML.element_text(attr)
                if attr_text:
                    attr_text = attr_text.strip()
                    if attr_text:
                        values.append(attr_text)

                # Parse any nested NameID children
                for nameid in attr.iterchildren(
                    "{%s}NameID" % OneLogin_Saml2_Constants.NSMAP["saml"]
                ):
                    values.append(
                        {
                            "NameID": {
                                "Format": nameid.get("Format"),
                                "NameQualifier": nameid.get("NameQualifier"),
                                "value": nameid.text,
                            }
                        }
                    )
            # XXX: Fix for duplicate attribute keys
            attributes[attr_name] = attributes.setdefault(attr_name, []) + values
        return attributes

    orig_fn = OneLogin_Saml2_Response.get_attributes
    OneLogin_Saml2_Response.get_attributes = _get_attributes_patched
    yield
    OneLogin_Saml2_Response.get_attributes = orig_fn
