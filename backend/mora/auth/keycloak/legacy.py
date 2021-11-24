# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from functools import lru_cache
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from structlog import get_logger

from mora import config

logger = get_logger()

Base = declarative_base()


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


def _get_connection_url():
    settings = config.get_settings()
    dbname = settings.session_db_name
    user = settings.session_db_user
    password = settings.session_db_password
    host = settings.session_db_host
    port = settings.session_db_port
    connection_url = "postgresql+psycopg2://"
    connection_url += str(user) + ":" + str(password)
    connection_url += "@" + str(host) + ":" + str(port)
    connection_url += "/" + str(dbname)
    return connection_url


@lru_cache()
def _get_engine():
    connection_url = _get_connection_url()
    logger.debug("Open connection to database")
    try:
        engine = create_engine(connection_url, pool_size=30, max_overflow=60)
        return engine
    except Exception:
        logger.error("Database connection error")
        raise


def validate_session(session_id: str) -> bool:
    """Validate the existence of a session from legacy session table"""
    store_id = f"session:{session_id}"
    engine = _get_engine()
    with Session(engine) as session:
        result = session.query(SessionModel).filter(SessionModel.session_id == store_id)
    return result.count() > 0
