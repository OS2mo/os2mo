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
import psycopg2
import flask
from .. import settings

blueprint = flask.Blueprint('configuration', __name__, static_url_path='',
                            url_prefix='/service')
conn = psycopg2.connect(settings.USER_SETTINGS_CONN_STRING)
cur = conn.cursor()

@blueprint.route('/ou/<uuid:unitid>/set_configuration', methods=['POST'])
def set_org_unit_configuration(unitid):
    """Set a configuration setting for an ou.

    .. :quickref: Unit; Create configuration setting.

    :statuscode 200: Setting created.
    :statuscode 404: No such unit found.
    :statuscode 409: Validation failed, see below.

    :param unitid: The UUID of the organisational unit to be terminated.

    :<json object conf: Configuration option

    **Example Request**:

    .. sourcecode:: json

      {
        "configuration": {
          "show_location": "True"
        }
      }

    :returns: True
    """

    query = ("SELECT setting, value FROM " +
             "orgunit_settings WHERE object = '{}'").format(unitid)

    cur.execute(query)
    rows = cur.fetchall()
    configuration = flask.request.data
    #configuration = flask.request.get_json()
    print(configuration)
    
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

    query = ("SELECT setting, value FROM " +
             "orgunit_settings WHERE object = '{}'").format(unitid)

    cur.execute(query)
    rows = cur.fetchall()
    return flask.jsonify(rows)
