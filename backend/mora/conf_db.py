# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import logging

import psycopg2
from psycopg2.extras import execute_values
from psycopg2.sql import SQL, Identifier

from mora import exceptions
from mora.settings import config

logger = logging.getLogger("mo_configuration")

# This is the default key-value configuration pairs. They are used to
# initialize the configuration database through and in health_check to
# verify that there exist default values for all expected keys.
_DEFAULT_CONF = (
    ('show_roles', 'True'),
    ('show_kle', 'False'),
    ('show_user_key', 'True'),
    ('show_location', 'True'),
    ('show_time_planning', 'False'),
    ('show_level', 'True'),
    ('show_primary_engagement', 'False'),
    ('show_primary_association', 'False'),
    ('show_org_unit_button', 'False'),
    ('inherit_manager', 'True'),
    ('read_only', 'False'),
    # Comma seperated UUID(s) of top-level facets to show on association view.
    ('association_dynamic_facets', ''),
)


_DBNAME = config["configuration"]["database"]["name"]
_DBNAME_BACKUP = _DBNAME + "_backup"
# The postgres default (empty) template for CREATE DATABASE.
_DBNAME_SYS_TEMPLATE = "template1"


def _get_connection(dbname):
    logger.debug('Open connection to database')
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=config["configuration"]["database"]["user"],
            password=config["configuration"]["database"]["password"],
            host=config["configuration"]["database"]["host"],
            port=config["configuration"]["database"]["port"],
            connect_timeout=5
        )
    except psycopg2.OperationalError:
        logger.error('Database connection error')
        raise
    return conn


def _cpdb(dbname_from, dbname_to):
    """Copy a pg database object.

    This creates a new database and uses `dbname_from` as a template for that
    database. It copys all structures and data.

    Requires CREATEDB or SUPERUSER privileges.

    """
    logger.debug("Copying database from %s to %s", dbname_from, dbname_to)
    with _get_connection(_DBNAME_SYS_TEMPLATE) as conn:
        conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        with conn.cursor() as curs:
            curs.execute(
                SQL("create database {} with template {};").format(
                    Identifier(dbname_to), Identifier(dbname_from)
                )
            )


def _dropdb(dbname):
    """Deletes a pg database object.

    Requires OWNER or SUPERUSER privileges.
    """
    logger.debug("Dropping database %s", dbname)
    with _get_connection(_DBNAME_SYS_TEMPLATE) as conn:
        conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        with conn.cursor() as curs:
            curs.execute(
                SQL("DROP DATABASE IF EXISTS {};").format(Identifier(dbname))
            )


def _createdb():
    """Create a new database and initialize table.

    Requires CREATEDB or SUPERUSER privileges.

    """
    _cpdb(_DBNAME_SYS_TEMPLATE, _DBNAME)
    create_db_table()


def _check_database(dbname):
    """Checks if a pg database object exists."""
    with _get_connection(_DBNAME_SYS_TEMPLATE) as conn, conn.cursor() as curs:
        curs.execute(
            "select datname from pg_catalog.pg_database where datname=%s",
            [dbname],
        )
        return bool(curs.fetchone())


def _insert_missing_defaults():
    """Check if the database already contains default values"""

    missing = _find_missing_default_keys()
    if missing:
        missing_values = filter(lambda x: x[0] in missing, _DEFAULT_CONF)
        logger.info("Inserting missing default configuration values [{}].".format(
            ", ".join(missing)))
        set_global_conf(missing_values)


def set_global_conf(conf):
    """Load a global configuration directly into the database. It does not
    check for duplicates.

    """
    DEFAULT_CONF_DATA_QUERY = SQL(
        "INSERT INTO orgunit_settings ( object, setting, value ) VALUES %s;"
    )

    with _get_connection(_DBNAME) as con, con.cursor() as cursor:
        execute_values(
            cursor, DEFAULT_CONF_DATA_QUERY, conf, "( Null, %s, %s)"
        )


def create_db_table():
    """Initialize the config database with a table and default values."""

    CREATE_CONF_QUERY = SQL(
        "CREATE TABLE IF NOT EXISTS orgunit_settings("
        "id serial PRIMARY KEY,"
        "object UUID,"
        "setting varchar(255) NOT NULL,"
        "value varchar(255) NOT NULL"
        ");"
    )

    logger.info("Initializing configuration database.")
    with _get_connection(_DBNAME) as con, con.cursor() as cursor:
        cursor.execute(CREATE_CONF_QUERY)

    _insert_missing_defaults()

    logger.info("Configuration database initialised.")


def _find_missing_default_keys():
    conn = _get_connection(_DBNAME)

    # all settings that have a global (uuid = null) value
    query = """
        select setting
          from orgunit_settings
         where object is not distinct from null;"""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        settings_in_db = set(key for (key,) in cursor.fetchall())
    finally:
        conn.close()

    missing = set()
    for key, __ in _DEFAULT_CONF:
        if key not in settings_in_db:
            missing.add(key)

    return missing


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
            error_msg = ("Configuration database is missing default"
                         " settings for keys: %s." % ", ".join(missing))
            return False, error_msg
    except psycopg2.OperationalError as e:
        error_msg = "Configuration database connection error: %s"
        return False, error_msg % e.pgerror

    return True, "Success"


def testdb_setup():
    """Move the database specified in settings to a backup location and reset
    the database specified in the settings. This makes the database ready for
    testing while still preserving potential data written to the database. Use
    `testdb_teardown()` to reverse this.

    Requires CREATEDB and OWNER or SUPERUSER privileges.

    """
    logger.info("Setting up test database: %s", _DBNAME)
    if _check_database(_DBNAME_BACKUP):
        raise Exception(
            "The backup location used for the database while running tests is "
            "not empty. You have to make sure no data is lost and manually "
            "remove the database: %s" % _DBNAME_BACKUP
        )

    _cpdb(_DBNAME, _DBNAME_BACKUP)

    testdb_reset()


def testdb_reset():
    """Reset the database specified in settings from the template. Requires the
    template database to be created.

    Requires CREATEDB and OWNER or SUPERUSER privileges.

    """

    logger.info("Resetting test database: %s", _DBNAME)
    _dropdb(_DBNAME)
    _createdb()


def testdb_teardown():
    """Move the database at the backup location back to database location
    specified in the settings. Remove the changes made by `testdb_setup()`.

    Requires CREATEDB and OWNER or SUPERUSER privileges.

    """
    logger.info("Removing test database: %s", _DBNAME)
    _dropdb(_DBNAME)
    _cpdb(_DBNAME_BACKUP, _DBNAME)
    _dropdb(_DBNAME_BACKUP)


def get_configuration(unitid=None):
    if unitid:
        query_suffix = " = %s"
    else:
        query_suffix = " IS %s"

    configuration = {}
    conn = _get_connection(_DBNAME)
    query = ("SELECT setting, value FROM orgunit_settings WHERE object" +
             query_suffix)
    try:
        cur = conn.cursor()
        cur.execute(query, (unitid,))
        rows = cur.fetchall()
        for row in rows:
            setting = row[0]
            if str(row[1]).lower() == 'true':
                value = True
            elif str(row[1]).lower() == 'false':
                value = False
            else:
                value = row[1]
            configuration[setting] = value
    finally:
        conn.close()
    logger.debug('Read: Unit: {}, configuration: {}'.format(unitid,
                                                            configuration))
    return configuration


def set_configuration(configuration, unitid=None):
    logger.debug('Write: Unit: {}, configuration: {}'.format(unitid,
                                                             configuration))
    if unitid:
        query_suffix = ' = %s'
    else:
        query_suffix = ' IS %s'

    conn = _get_connection(_DBNAME)
    try:
        cur = conn.cursor()
        orgunit_conf = configuration['org_units']

        for key, value in orgunit_conf.items():
            query = ('SELECT id FROM orgunit_settings WHERE setting =' +
                     '%s and object' + query_suffix)
            cur.execute(query, (key, unitid))
            rows = cur.fetchall()
            if not rows:
                query = ("INSERT INTO orgunit_settings (object, setting, " +
                         "value) VALUES (%s, %s, %s)")
                cur.execute(query, (unitid, key, value))
            elif len(rows) == 1:
                query = 'UPDATE orgunit_settings SET value=%s WHERE id = %s'
                cur.execute(query, (value, rows[0][0]))
            else:
                exceptions.ErrorCodes.E_INCONSISTENT_SETTINGS(
                    'Inconsistent settings for {}'.format(unitid)
                )
            conn.commit()
    finally:
        conn.close()
    return True
