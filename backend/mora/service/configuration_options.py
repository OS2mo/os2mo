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
from .. import util
from .. import service  # noqa


logger = logging.getLogger("mo_configuration")

blueprint = flask.Blueprint('configuration', __name__, static_url_path='',
                            url_prefix='/service')

TRIGGER_NAMES = {"trigger-before", "trigger-after"}


def _get_connection(config=None):
    if not config:
        config = flask.current_app.config
    logger.debug('Open connection to Configuration database')
    try:
        conn = psycopg2.connect(user=config.get("CONF_DB_USER"),
                                dbname=config.get("CONF_DB_NAME"),
                                host=config.get("CONF_DB_HOST"),
                                port=config.get("CONF_DB_PORT"),
                                password=config.get("CONF_DB_PASSWORD"))
    except psycopg2.OperationalError:
        logger.error('Configuration database connection error')
        raise
    return conn


def check_config(app):
    errors = []
    config = app.config
    if not (config.get("CONF_DB_USER") and config.get("CONF_DB_NAME") and
            config.get("CONF_DB_HOST") and config.get("CONF_DB_PORT") and
            config.get("CONF_DB_PASSWORD")):
        errors.extend([
            'Configuration error of user settings connection information',
            'CONF_DB_USER: {}'.format(config.get("CONF_DB_USER")),
            'CONF_DB_NAME: {}'.format(config.get("CONF_DB_NAME")),
            'CONF_DB_HOST: {}'.format(config.get("CONF_DB_HOST")),
            'CONF_DB_PORT: {}'.format(config.get("CONF_DB_PORT")),
            'Length of CONF_DB_PASSWORD: {}'.format(
                len(config.get("CONF_DB_PASSWORD", "")))
        ])
    try:
        conn = _get_connection(config)
    except Exception:
        errors.append("Configuration database could not be opened")
        conn = None

    if conn:
        # check all triggers can be found from text and report those that can't
        query_suffix = " OR ".join(["setting like %s" for i in TRIGGER_NAMES])
        where_values = ["%s://%%" % n for n in TRIGGER_NAMES]
        cur = conn.cursor()
        query = ("SELECT object, setting, value FROM orgunit_settings WHERE " +
                 query_suffix)
        cur.execute(query, where_values)
        rows = cur.fetchall()
        for row in rows:
            row = {"object": row[0], "setting": row[1], "value": row[2]}
            try:
                triggers_from_string(row["value"])
            except Exception:
                errors.append("trigger validation error for %r" % row)
    if errors:
        [logger.error(x) for x in errors]
        raise Exception("Configuration settings had errors "
                        "please check log output from startup")

    return not errors


def triggers_from_string(trigger_string):
    triggers = []
    trigger_strings = [
        i.strip() for i in trigger_string.split(",") if i.strip()
    ]
    for s in trigger_strings:
        identifiers = s.split(".")
        t = globals().get(identifiers.pop(0), None)
        while t and len(identifiers):
            t = getattr(t, identifiers.pop(0), None)
        if not t:
            logger.error("trigger not found: %s", s)
            raise Exception("trigger not found: %s" % s)
        else:
            triggers.append(t)
    return triggers


def get_triggers(trigger_name, uuid, url_rule):

    if trigger_name not in TRIGGER_NAMES:
        logger.error("trigger name not allowed: %s", trigger_name)
        raise Exception("trigger name not allowed: %s" % trigger_name)

    trigger_mask = "{}://{}".format(trigger_name, url_rule)

    # local else global triggers
    configuration = get_configuration(uuid)
    if trigger_mask not in configuration:
        configuration = get_configuration()
    if trigger_mask not in configuration:
        return []
    else:
        return triggers_from_string(configuration[trigger_mask])


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

    orgunit_conf = configuration['org_units']

    # check if there are any triggers and whether they can be resolved
    for key, value in orgunit_conf.items():
        for tn in TRIGGER_NAMES:
            if key.startswith("%s://" % tn):
                triggers_from_string(value)

    conn = _get_connection()
    try:
        cur = conn.cursor()

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


def del_configuration(configuration, unitid=None):
    logger.debug('Delete: Unit: {}, configuration: {}'.format(unitid,
                                                              configuration))
    if unitid:
        query_suffix = ' = %s'
    else:
        query_suffix = ' IS %s'

    orgunit_conf = configuration['org_units']
    # in order to be somewhat symmetrical, this only deletes
    # settings with exactly the specified iobject, setting and value
    conn = _get_connection()
    try:
        cur = conn.cursor()

        for key, value in orgunit_conf.items():
            query = ('DELETE FROM orgunit_settings WHERE setting =' +
                     '%s and value = %s and object' + query_suffix)
            cur.execute(query, (key, value, unitid))
        conn.commit()

    finally:
        conn.close()
    return True


@blueprint.route('/ou/<uuid:unitid>/configuration', methods=['DELETE'])
@util.restrictargs()
def del_org_unit_configuration(unitid):
    """Delete a configuration setting for an ou.

    .. :quickref: Unit; Delete configuration setting.

    :statuscode 201: Setting deleted

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
    return flask.jsonify(del_configuration(configuration, unitid))


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
    """Set or modify a global configuration setting.

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


@blueprint.route('/configuration', methods=['DELETE'])
@util.restrictargs('at')
def del_global_configuration():
    """Delete a global configuration setting.

    .. :quickref: Delete a global configuration setting.

    :statuscode 201: Setting deleted

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
    return flask.jsonify(del_configuration(configuration))


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


# Triggers were implemented before they were actually needed,
# so here two examples on how they are going to be used
#
# This is a trigger-example on module-level in service/orgunit
#
#    def ensure_vacant_manager(service_request):
#        logger.warning("inserting vacant manager skipped because...")
#
# The 'service_request' parameter is simply a OrgUnitRequestHandler instance
# The same function coule be a method in OrgUnitRequestHandler,
# in which case it would look like this:
#
#    def ensure_manager_vacancy(self):
#        logger.warning("inserting manager vacancy also skipped because...")
#
#
# triggers-before will typically be in the 'prepare-request part'
# triggers-after will typically be in the submit part of the handler
#
# in this file a
#     from .. import service
# would then enable one to define a trigger in the options like
#
# "trigger-after:///service/ou/create":"service.orgunit.ensure_vacant_manager"
#
# provided the function
#
#    def ensure_vacant_manager(service_request):
#        logger.warning("inserting vacant manager skipped because...")
#
# was defined in sercvice/orgunit.py
