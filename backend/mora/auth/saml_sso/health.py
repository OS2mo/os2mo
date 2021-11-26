# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import logging

from fastapi_sqlalchemy import db
from requests import RequestException
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from mora.auth.saml_sso import settings
from mora.auth.saml_sso.session import SessionModel

logger = logging.getLogger(__name__)


def session_database_health():
    """Verify whether the session database can be reached"""
    try:
        with db():
            db.session.query(SessionModel).first()
    except (AttributeError, SQLAlchemyError) as e:
        logger.exception("Sessions database error {}".format(e))
        return False
    return True


def idp_health():
    """Verify whether the IdP can be reached"""
    try:
        settings._get_saml_idp_settings()
    except (ValueError, RequestException, OSError, HTTPException) as e:
        logger.exception("Auth IdP error: {}".format(e))
        return False
    return True
