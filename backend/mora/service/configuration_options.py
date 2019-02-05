#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# import sqlite3
import psycopg2
import flask
from mora import exceptions
from .. import settings
from .. import util


blueprint = flask.Blueprint('configuration', __name__, static_url_path='',
                            url_prefix='/service')


def _get_connection():
    conn = psycopg2.connect(user=settings.USER_SETTINGS_DB_USER,
                            dbname=settings.USER_SETTINGS_DB_NAME,
                            host=settings.USER_SETTINGS_DB_HOST,
                            port=settings.USER_SETTINGS_DB_PORT,
                            password=settings.USER_SETTINGS_DB_PASSWORD)
    return conn


@blueprint.route('/ou/<uuid:unitid>/configuration', methods=['POST'])
@util.restrictargs()
def set_org_unit_configuration(unitid):
    """Set a configuration setting for an ou.

    .. :quickref: Unit; Create configuration setting.

    :statuscode 201: Setting created.
    :statuscode 404: No such unit found.

    :param unitid: The UUID of the organisational unit to be terminated.

    :<json object conf: Configuration option

    .. sourcecode:: json

      {
        "org_units": {
          "show_location": "True"
        }
      }

    :returns: True
    """
    conn = _get_connection()
    cur = conn.cursor()

    configuration = flask.request.get_json()
    orgunit_conf = configuration['org_units']

    for key, value in orgunit_conf.items():
        query = ("SELECT id FROM orgunit_settings WHERE setting = %s " +
                 "AND object=%s")
        cur.execute(query, (key, unitid))
        rows = cur.fetchall()
        if not rows:
            query = ("INSERT INTO orgunit_settings (object, setting, " +
                     "value) VALUES (%s, %s, %s)")
            cur.execute(query, (unitid, key, value))
        elif len(rows) == 1:
            query = "UPDATE orgunit_settings SET value=%s WHERE id=%s"
            cur.execute(query, (value, rows[0][0]))
        else:
            exceptions.ErrorCodes.E_INCONSISTENT_SETTINGS(
                'Inconsistent settings for {}'.format(unitid)
            )
        conn.commit()
    return flask.jsonify(True)


@blueprint.route('/ou/<uuid:unitid>/configuration', methods=['GET'])
@util.restrictargs()
def get_org_unit_configuration(unitid):
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.
    :statuscode 404: No such unit found.

    :param unitid: The UUID of the organisational unit to be terminated.

    :returns: Configuration settings for unit
    """
    return_dict = {}
    conn = _get_connection()
    cur = conn.cursor()

    query = "SELECT setting, value FROM orgunit_settings WHERE object = %s"

    cur.execute(query, (unitid,))
    rows = cur.fetchall()
    for row in rows:
        return_dict[row[0]] = row[1]
    return flask.jsonify(return_dict)


@blueprint.route('/o/configuration', methods=['POST'])
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
    conn = _get_connection()
    cur = conn.cursor()

    configuration = flask.request.get_json()
    orgunit_conf = configuration['org_units']

    for key, value in orgunit_conf.items():
        query = ("SELECT id FROM orgunit_settings WHERE setting = %s " +
                 "AND object IS NULL")
        cur.execute(query, (key,))
        rows = cur.fetchall()

        if len(rows) == 0:
            query = ("INSERT INTO orgunit_settings (object, setting, " +
                     "value) values (NULL, '%s', '%s')")
            cur.execute(query, (key, value))
        elif len(rows) == 1:
            query = "UPDATE orgunit_settings SET value=%s WHERE id=%s"
            cur.execute(query, (value, rows[0][0]))
        else:
            exceptions.ErrorCodes.E_INCONSISTENT_SETTINGS(
                'Inconsistent global settings'
            )
        conn.commit()
    return flask.jsonify(True)


@blueprint.route('/o/configuration', methods=['GET'])
@util.restrictargs('at')
def get_global_configuration():
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.
    :statuscode 404: No such unit found.

    :returns: Global configuration settings
    """
    return_dict = {}
    conn = _get_connection()
    cur = conn.cursor()

    query = "SELECT setting, value FROM orgunit_settings WHERE object IS NULL"
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        return_dict[row[0]] = row[1]
    return flask.jsonify(return_dict)
