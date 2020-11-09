# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging
from itertools import starmap
from operator import itemgetter
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

from mora import exceptions
from mora.settings import config
from sqlalchemy_utils import UUIDType, create_database, database_exists

logger = logging.getLogger("mo_configuration")


Base = declarative_base()


class Config(Base):
    __tablename__ = "orgunit_settings"

    id = Column(Integer, primary_key=True)
    object = Column(UUIDType(binary=False))
    setting = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)


# This is the default key-value configuration pairs. They are used to
# initialize the configuration database through and in health_check to
# verify that there exist default values for all expected keys.
_DEFAULT_CONF = (
    ("show_roles", "True"),
    ("show_kle", "False"),
    ("show_user_key", "True"),
    ("show_location", "True"),
    ("show_time_planning", "False"),
    ("show_level", "True"),
    ("show_primary_engagement", "False"),
    ("show_primary_association", "False"),
    ("show_org_unit_button", "False"),
    ("inherit_manager", "True"),
    ("read_only", "False"),
    # Comma seperated UUID(s) of top-level facets to show on association view.
    ("association_dynamic_facets", ""),
)


def _get_engine():
    connection_url = config["configuration"]["database"].get("connection_url")
    if connection_url is None:
        dbname = config["configuration"]["database"]["name"]
        user = config["configuration"]["database"]["user"]
        password = config["configuration"]["database"]["password"]
        host = config["configuration"]["database"]["host"]
        port = config["configuration"]["database"]["port"]
        connection_url = (
            "postgresql+psycopg2://" +
            str(user) + ":" + str(password) + "@" +
            str(host) + ":" + str(port) + "/" + str(dbname)
        )
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


def _createdb(force=True):
    """Create a new database and initialize table.

    Requires CREATEDB or SUPERUSER privileges.
    """
    engine = _get_engine()
    if force or not database_exists(engine.url):
        create_database(engine.url)
    create_db_table()


def _find_missing_default_keys():
    with _get_session() as session:
        # all settings that have a global (uuid = null) value
        query = select([Config.setting]).where(Config.object == None)  # noqa: E711
        result = session.execute(query)
        result = map(itemgetter(0), result)
        settings_in_db = set(result)

        default = set(map(itemgetter(0), _DEFAULT_CONF))
        missing = default - settings_in_db

        return missing


def _insert_missing_defaults():
    """Check if the database already contains default values"""

    missing = _find_missing_default_keys()
    if missing:
        missing_values = filter(lambda x: x[0] in missing, _DEFAULT_CONF)
        logger.info(
            "Inserting missing default configuration values [{}].".format(
                ", ".join(missing)
            )
        )
        set_configuration({"org_units": dict(missing_values)})


def drop_db_table():
    """Drop the config database."""
    logger.info("Dropping configuration database.")
    engine = _get_engine()
    Base.metadata.drop_all(engine)
    logger.info("Configuration database dropped.")


def create_db_table(insert_missing=True):
    """Initialize the config database.

    Optionally load default values too.
    """
    logger.info("Initializing configuration database.")
    engine = _get_engine()
    Base.metadata.create_all(engine)
    if insert_missing:
        _insert_missing_defaults()
    logger.info("Configuration database initialised.")


def get_configuration(unitid=None):
    def convert_bool(setting, value):
        lower_value = str(value).lower()
        if lower_value == "true":
            value = True
        elif lower_value == "false":
            value = False
        return setting, value

    with _get_session() as session:
        query = select([Config.setting, Config.value]).where(
            Config.object == unitid
        )
        result = session.execute(query)
        result = starmap(convert_bool, result)
        configuration = dict(result)
        logger.debug(
            "Read: Unit: {}, configuration: {}".format(unitid, configuration)
        )
        return configuration


def set_configuration(configuration, unitid=None):
    logger.debug(
        "Write: Unit: {}, configuration: {}".format(unitid, configuration)
    )
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
    established and the database contains all expected default values.

    This is intended to be used whenever an app object is created.
    """
    try:
        missing = _find_missing_default_keys()
        if missing:
            error_msg = (
                "Configuration database is missing default"
                " settings for keys: %s." % ", ".join(missing)
            )
            return False, error_msg
    except Exception as e:
        error_msg = "Configuration database connection error: %s"
        return False, error_msg.format(str(e))
    return True, "Success"
