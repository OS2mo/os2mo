# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from structlog import get_logger
from contextlib import contextmanager
from functools import lru_cache
from itertools import starmap
from pathlib import Path

from alembic.config import Config as AlembicConfig
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy_utils import UUIDType, create_database, database_exists, drop_database

from mora import exceptions, config

logger = get_logger()

SUBSTITUTE_ROLES = "substitute_roles"

Base = declarative_base()


class Config(Base):
    __tablename__ = "orgunit_settings"

    id = Column(Integer, primary_key=True)
    object = Column(UUIDType(binary=False))
    setting = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)


def _get_connection_url():
    settings = config.get_settings()
    dbname = settings.conf_db_name
    user = settings.conf_db_user
    password = settings.conf_db_password
    host = settings.conf_db_host
    port = settings.conf_db_port
    connection_url = "postgresql+psycopg2://"
    connection_url += str(user) + ":" + str(password)
    connection_url += "@" + str(host) + ":" + str(port)
    connection_url += "/" + str(dbname)
    return connection_url


def _get_engine():
    connection_url = _get_connection_url()
    logger.debug("Open connection to database")
    try:
        engine = create_engine(connection_url)
        return engine
    except Exception:
        logger.error("Database connection error")
        raise


@lru_cache(maxsize=None)
def _get_session_maker():
    engine = _get_engine()
    Session = sessionmaker(bind=engine)
    return Session


def _createdb(force: bool = True):
    """
    Create a new database and initialize table.
    Requires CREATEDB or SUPERUSER privileges.

    :param force: create even if database already exists
    :return: None

    """
    engine = _get_engine()
    if force or not database_exists(engine.url):
        create_database(engine.url)
    create_db_table()


def drop_db():
    """Drop the config database."""
    logger.info("Dropping configuration database.")
    drop_database(_get_connection_url())
    _get_session_maker.cache_clear()
    logger.info("Configuration database dropped.")


def create_db_table():
    """
    Initialize the config database.
    """
    logger.info("Initializing configuration database.")

    # Issue "CREATE TABLE" statements using SQLAlchemy
    engine = _get_engine()
    Base.metadata.create_all(engine)

    # Set up Alembic config
    base_path = Path("backend/mora/conf_db")
    ini = Path("alembic.ini")
    alembic_dir = Path("alembic")
    ini_path = base_path / ini
    alembic_path = base_path / alembic_dir
    alembic_cfg = AlembicConfig(file_=str(ini_path))
    alembic_cfg.set_main_option("script_location", str(alembic_path))

    # Tell Alembic that our DB schema is now up-to-date, so Alembic does not
    # try to upgrade the schema.
    # command.stamp(alembic_cfg, "head")

    logger.info("Configuration database initialised.")


@contextmanager
def _get_session():
    """Provide a transactional scope around a series of operations."""
    session_maker = _get_session_maker()
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception as exp:
        session.rollback()
        raise exp
    finally:
        session.close()


def get_configuration(unitid=None):
    def convert_bool(setting, value):
        lower_value = str(value).lower()
        if lower_value == "true":
            value = True
        elif lower_value == "false":
            value = False
        return setting, value

    with _get_session() as session:
        query = select([Config.setting, Config.value]).where(Config.object == unitid)
        result = session.execute(query)
        result = starmap(convert_bool, result)
        configuration = dict(result)
        logger.debug("get_configuration", unitid=unitid, configuration=configuration)
        return configuration


def set_configuration(configuration, unitid=None):
    logger.debug("set_configuration", unitid=unitid, configuration=configuration)
    configuration = configuration["org_units"]

    with _get_session() as session:
        for setting, value in configuration.items():
            # Check if setting exists
            result = session.query(Config).filter(
                Config.object == unitid, Config.setting == setting
            )
            if result.count() > 1:
                exceptions.ErrorCodes.E_INCONSISTENT_SETTINGS(
                    "Inconsistent settings for {}".format(unitid)
                )
            result = result.first()
            if result:
                result.value = value
            else:
                entry = Config(object=unitid, setting=setting, value=value)
                session.add(entry)
        return True


def health_check():
    """Return a tuple (healthy, msg) where healthy is a boolean and msg
    is the potential error message.

    The configuration database is healthy iff a connection can be
    established.

    That the database contains all expected default values is now an invariant.

    This is intended to be used whenever an app object is created.
    """
    try:
        # Check that a connection can be made
        get_configuration()
    except Exception as e:
        error_msg = "Configuration database connection error: %s"
        return False, error_msg.format(str(e))
    return True, "Success"
