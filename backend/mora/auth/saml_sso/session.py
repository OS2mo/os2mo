# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import enum

import datetime
import logging
import pickle
import uuid
from fastapi_sqlalchemy import db
from flask_session.sessions import SqlAlchemySession
from functools import partial
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.ext.declarative import declarative_base
from starlette.requests import Request

from mora.settings import app_config

LOGGED_IN = "loggedIn"
SAML_SESSION_INDEX = "samlSessionIndex"
SAML_NAME_ID = "samlNameId"
SAML_ATTRIBUTES = "samlAttributes"
SAML_SESSION_TYPE = "samlSessionType"

logger = logging.getLogger(__name__)

Base = declarative_base()


class SessionType(enum.Enum):
    User = 1
    Service = 2


def create_session_dict(session_type: SessionType, attributes: dict):
    session_dict = {
        SAML_SESSION_TYPE: session_type,
        SAML_ATTRIBUTES: attributes,
        LOGGED_IN: True,
    }
    logger.info("Creating session: {}".format(session_dict))

    return session_dict


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True)
    data = Column(LargeBinary)
    expiry = Column(DateTime)

    def __init__(self, session_id, data, expiry):
        self.session_id = session_id
        self.data = data
        self.expiry = expiry

    def __repr__(self):
        return "<Session data %s>" % self.data


class SessionInterface:
    def __init__(self):
        self.session_class = partial(SqlAlchemySession, permanent=True)
        self.key_prefix = "session:"

    def open_session(self, request: Request):
        session_id = request.headers.get("session") or request.cookies.get("session")
        if not session_id:
            session_id = str(uuid.uuid4())
        store_id = self.key_prefix + session_id

        with db():
            saved_session = (
                db.session.query(SessionModel).filter_by(session_id=store_id).first()
            )
            if saved_session and saved_session.expiry <= datetime.datetime.utcnow():
                # Delete expired session
                db.session.delete(saved_session)
                db.session.commit()
                saved_session = None
            if saved_session:
                data = pickle.loads(saved_session.data)
                return self.session_class(data, sid=session_id)
            else:
                return self.session_class(sid=session_id)

    def insert_new_session(self, data):
        """
        Insert new Service session, corresponding to creating an API token
        """

        sid = str(uuid.uuid4())
        store_id = self.key_prefix + sid

        expires = self.get_expiration_time(api_token=True)

        session_obj = self.session_class(data, sid=sid, permanent=True)

        new_session = SessionModel(store_id, pickle.dumps(dict(session_obj)), expires)

        with db():
            db.session.add(new_session)
            db.session.commit()

        return sid

    def save_session(self, session: SqlAlchemySession, response):
        store_id = self.key_prefix + session.sid

        expires = self.get_expiration_time()

        val = pickle.dumps(dict(session))
        with db():
            saved_session = (
                db.session.query(SessionModel).filter_by(session_id=store_id).first()
            )

            if saved_session:
                saved_session.data = val
                saved_session.expiry = expires
                db.session.commit()
            else:
                new_session = SessionModel(store_id, val, expires)
                db.session.add(new_session)
                db.session.commit()

        response.set_cookie(key="session", value=session.sid)

    def get_expiration_time(self, api_token=False):
        if api_token:
            lifetime = app_config.get("SAML_SERVICE_SESSION_LIFETIME")
        else:
            lifetime = app_config.get("PERMANENT_SESSION_LIFETIME")
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=lifetime)
