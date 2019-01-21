#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''
Organisational units
--------------------

This section describes how to interact with organisational units.

For more information regarding reading relations involving organisational
units, refer to :http:get:`/service/(any:type)/(uuid:id)/details/`

'''
import sqlite3
import flask
from .. import settings

blueprint = flask.Blueprint('configuration', __name__, static_url_path='',
                            url_prefix='/service')


@blueprint.route('/ou/<uuid:unitid>/set_configuration', methods=['POST'])
def set_org_unit_configuration(unitid):
    """Set a configuration setting for an ou.

    .. :quickref: Unit; Create configuration setting.

    :statuscode 201: Setting created.
    :statuscode 404: No such unit found.

    :param unitid: The UUID of the organisational unit to be terminated.

    :<json object conf: Configuration option

    .. sourcecode:: json

      {
        "configuration": {
          "show_location": "True"
        }
      }

    :returns: True
    """
    configuration = flask.request.get_json()
    orgunit_conf = configuration['org_units']

    with sqlite3.connect(settings.USER_SETTINGS_DB_FILE,
                         check_same_thread=False) as conn:
        cur = conn.cursor()
    
        for key, value in orgunit_conf.items():
            query = ("SELECT id FROM orgunit_settings WHERE setting = ? " +
                     "AND object=?")
            cur.execute(query, (key, unitid))
            rows = cur.fetchall()
            if len(rows) == 0:
                query = ("INSERT INTO orgunit_settings (object, setting, value) " +
                         "values (?, ?, ?)")
                cur.execute(query, (unitid, key, value))
            elif len(rows) == 1:
                query = "UPDATE orgunit_settings set value=? where id=?"
                cur.execute(query, (value, rows[0][0]))
            else:
                raise('Non-consistent settings for {}'.format(unitid))
    return flask.jsonify(True)


@blueprint.route('/ou/<uuid:unitid>/get_configuration', methods=['GET'])
def get_org_unit_configuration(unitid):
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.
    :statuscode 404: No such unit found.

    :param unitid: The UUID of the organisational unit to be terminated.

    :returns: Configuration settings for unit
    """
    return_dict = {}

    with sqlite3.connect(settings.USER_SETTINGS_DB_FILE,
                         check_same_thread=False) as conn:
        cur = conn.cursor()
        query = "SELECT setting, value FROM orgunit_settings WHERE object = ?"

        cur.execute(query, (unitid,))
        rows = cur.fetchall()
        for row in rows:
            return_dict[row[0]] = row[1]
    return flask.jsonify(return_dict)


@blueprint.route('/o/set_configuration', methods=['POST'])
def set_global_configuration():
    """Set or modify a gloal configuration setting.

    .. :quickref: Set or modify a global configuration setting.

    :statuscode 201: Setting created.

    :<json object conf: Configuration option

    .. sourcecode:: json

      {
        "configuration": {
          "show_roles": "False"
        }
      }

    :returns: True
    """
    configuration = flask.request.get_json()
    orgunit_conf = configuration['org_units']
    with sqlite3.connect(settings.USER_SETTINGS_DB_FILE,
                         check_same_thread=False) as conn:
        cur = conn.cursor()

        for key, value in orgunit_conf.items():
            query = ("SELECT id FROM orgunit_settings WHERE setting = ? " +
                     "AND object is Null")
            cur.execute(query, (key,))
            rows = cur.fetchall()

            if len(rows) == 0:
                query = ("INSERT INTO orgunit_settings (object, setting, value) " +
                         "values (Null, '?', '?')")
                cur.execute(query, (key, value))
            elif len(rows) == 1:
                query = "UPDATE orgunit_settings set value=? where id=?"
                cur.execute(query, (value, rows[0][0]))
            else:
                raise('Non-consistent global settings')
    return flask.jsonify(True)


@blueprint.route('/o/get_configuration', methods=['GET'])
def get_global_configuration():
    """Read configuration settings for an ou.

    .. :quickref: Unit; Read configuration setting.

    :statuscode 200: Setting returned.
    :statuscode 404: No such unit found.

    :returns: Global configuration settings
    """
    return_dict = {}

    with sqlite3.connect(settings.USER_SETTINGS_DB_FILE,
                         check_same_thread=False) as conn:
        cur = conn.cursor()
        query = ("SELECT setting, value FROM " +
                 "orgunit_settings WHERE object is Null")
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            return_dict[row[0]] = row[1]
    return flask.jsonify(return_dict)
