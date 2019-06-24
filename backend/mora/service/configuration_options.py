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
from .. import settings
from .. import util

logger = logging.getLogger("mo_configuration")

blueprint = flask.Blueprint('configuration', __name__, static_url_path='',
                            url_prefix='/service')


if not (settings.USER_SETTINGS_DB_USER and settings.USER_SETTINGS_DB_NAME and
        settings.USER_SETTINGS_DB_HOST and settings.USER_SETTINGS_DB_PORT and
        settings.USER_SETTINGS_DB_PASSWORD):
    error_msgs = [
        'Configuration error of user settings connection information',
        'USER_SETTINGS_DB_USER: {}'.format(settings.USER_SETTINGS_DB_USER),
        'USER_SETTINGS_DB_NAME: {}'.format(settings.USER_SETTINGS_DB_NAME),
        'USER_SETTINGS_DB_HOST: {}'.format(settings.USER_SETTINGS_DB_HOST),
        'USER_SETTINGS_DB_PORT: {}'.format(settings.USER_SETTINGS_DB_PORT),
        'Length of USER_SETTINGS_DB_PASSWORD: {}'.format(
            len(settings.USER_SETTINGS_DB_PASSWORD)
        )
    ]
    for msg in error_msgs:
        logger.error(msg)
    raise Exception(error_msgs[0])


def _get_connection():
    logger.debug('Open connection to database')
    try:
        conn = psycopg2.connect(user=settings.USER_SETTINGS_DB_USER,
                                dbname=settings.USER_SETTINGS_DB_NAME,
                                host=settings.USER_SETTINGS_DB_HOST,
                                port=settings.USER_SETTINGS_DB_PORT,
                                password=settings.USER_SETTINGS_DB_PASSWORD)
    except psycopg2.OperationalError:
        logger.error('Database connection error')
        raise
    return conn


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
            if row[1] == 'True':
                value = True
            elif row[1] == 'False':
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
