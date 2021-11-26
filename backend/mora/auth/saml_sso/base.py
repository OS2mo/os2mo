# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from fastapi import FastAPI
from fastapi import Request
from fastapi_sqlalchemy import DBSessionMiddleware
from sqlalchemy import create_engine

from . import session
from . import sso
from ...settings import app_config
from mora import exceptions


def init_app(app: FastAPI):
    """
    Perform initial setup of SSO and Session
    """
    enabled = app_config.setdefault("SAML_AUTH_ENABLE", True)
    uri = _get_db_uri()
    app.add_middleware(DBSessionMiddleware, db_url=uri)

    if enabled:
        app.include_router(sso.router, prefix="/saml", tags=["Auth"])


def _get_db_uri():
    """
    Ensure the database URI is set, optionally creating it from individual config params
    """
    uri = app_config.get("SQLALCHEMY_DATABASE_URI")
    if not uri:
        uri = "postgresql://{}:{}@{}:{}/{}".format(
            app_config.get("SESSIONS_DB_USER", "sessions"),
            app_config.get("SESSIONS_DB_PASSWORD", "sessions"),
            app_config.get("SESSIONS_DB_HOST", "localhost"),
            app_config.get("SESSIONS_DB_PORT", "5432"),
            app_config.get("SESSIONS_DB_NAME", "sessions"),
        )
    return uri


def create_sessions_table():
    engine = create_engine(_get_db_uri())
    session.Base.metadata.create_all(engine)


def check_saml_authentication(request: Request):
    """
    Helper function for determining if the active session is valid or not
    """

    # Check if session exists is valid
    if app_config["SAML_AUTH_ENABLE"] and not request.state.session.get(
        session.LOGGED_IN
    ):
        exceptions.ErrorCodes.E_UNAUTHORIZED()


def get_session_attributes(request: Request):
    """
    Helper function for easy access to the attributes stored in the session
    """
    return request.state.session.get(session.SAML_ATTRIBUTES)


def get_session_name_id(request: Request):
    """
    Helper function for easy access to the NameID in the session
    """
    return request.state.session.get(session.SAML_NAME_ID)
