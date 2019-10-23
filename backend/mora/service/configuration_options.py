#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
import psycopg2
import flask
import logging
from mora import exceptions
from mora.settings import config
from .. import util

logger = logging.getLogger("mo_configuration")

blueprint = flask.Blueprint('configuration', __name__, static_url_path='',
                            url_prefix='/service')


# This is the default key-value configuration pairs. They are used to
# initialize the configuration database through the cli and in health_check to
# verify that there exist default values for all expected keys.
default = (
    ('show_roles', 'True'),
    ('show_user_key', 'True'),
    ('show_location', 'True'),
    ('show_time_planning', 'True'),
)


if not all(c in config["configuration"]["database"] for c in (
        "name", "user", "password", "host", "port")):
    error_msgs = [
        'Configuration error of user settings connection information',
        'CONF_DB_USER: {}'.format(config["configuration"]["database"]["user"]),
        'CONF_DB_NAME: {}'.format(config["configuration"]["database"]["name"]),
        'CONF_DB_HOST: {}'.format(config["configuration"]["database"]["host"]),
        'CONF_DB_PORT: {}'.format(config["configuration"]["database"]["port"]),
        'Length of CONF_DB_PASSWORD: {}'.format(
            len(config["configuration"]["database"]["password"])
        )
    ]
    for msg in error_msgs:
        logger.error(msg)
    raise Exception(error_msgs[0])


def _get_connection():
    logger.debug('Open connection to database')
    try:
        conn = psycopg2.connect(
            dbname=config["configuration"]["database"]["name"],
            user=config["configuration"]["database"]["user"],
            password=config["configuration"]["database"]["password"],
            host=config["configuration"]["database"]["host"],
            port=config["configuration"]["database"]["port"],
        )
    except psycopg2.OperationalError:
        logger.error('Database connection error')
        raise
    return conn


def health_check():
    """Return a tuple (healthy, msg) where healthy is a boolean and msg
    is the potential error message.

    The configuration database is healthy iff a connection can be
    established and the database contains all expected default values.

    This is intended to be used whenever an app object is created.
    """
    try:
        conn = _get_connection()
    except psycopg2.Error as e:
        error_msg = "Configuration database connnection error: %s"
        return False, error_msg % e.pgerror

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
    for key, __ in default:
        if key not in settings_in_db:
            missing.add(key)
    if missing:
        error_msg = ("Configuration database is missing default"
                     " settings for keys: %s." % ", ".join(missing))
        return False, error_msg

    return True, "Success"


def get_configuration(unitid=None):
    if unitid:
        query_suffix = " = %s"
    else:
        query_suffix = " IS %s"

    configuration = {}
    conn = _get_connection()
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

    conn = _get_connection()
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


@blueprint.route('/ou/<uuid:unitid>/configuration', methods=['POST'])
@util.restrictargs()
def set_org_unit_configuration(unitid):
    """Set a configuration setting for an ou.

    .. :quickref: Unit; Create configuration setting.

    :statuscode 201: Setting created.

    :param unitid: The UUID of the organisational unit to be configured.

    :<json object conf: Configuration option

    .. sourcecode:: json

      {
        "org_units": {
          "show_location": "True"
        }
      }

    :returns: True
    """
    configuration = flask.request.get_json()
    return flask.jsonify(set_configuration(configuration, unitid))


@blueprint.route('/ou/<uuid:unitid>/configuration', methods=['GET'])
@util.restrictargs()
def get_org_unit_configuration(unitid):
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.

    :param unitid: The UUID of the organisational unit.

    :returns: Configuration settings for unit
    """
    configuration = get_configuration(unitid)
    return flask.jsonify(configuration)


@blueprint.route('/configuration', methods=['POST'])
@util.restrictargs('at')
def set_global_configuration():
    """Set or modify a gloal configuration setting.

    .. :quickref: Set or modify a global configuration setting.

    :statuscode 201: Setting created.

    :<json object conf: Configuration option

    .. sourcecode:: json

      {
        "org_units": {
          "show_roles": "False"
        }
      }

    :returns: True
    """
    configuration = flask.request.get_json()
    return flask.jsonify(set_configuration(configuration))


@blueprint.route('/configuration', methods=['GET'])
@util.restrictargs('at')
def get_global_configuration():
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.
    :statuscode 404: No such unit found.

    :returns: Global configuration settings
    """

    configuration = get_configuration()
    return flask.jsonify(configuration)
