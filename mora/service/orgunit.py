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

'''

import enum
import operator
import uuid

import flask
import werkzeug

from . import common
from . import keys
from . import mapping
from . import org
from .. import lora
from .. import util

blueprint = flask.Blueprint('orgunit', __name__, static_url_path='',
                            url_prefix='/service')


@enum.unique
class UnitDetails(enum.Enum):
    # name & userkey only
    MINIMAL = 0

    # with organisation
    ORG = 1

    # with child count
    NCHILDREN = 2

    # with children and parent
    FULL = 3


def get_one_orgunit(c, unitid, unit=None,
                    details=UnitDetails.NCHILDREN, validity=None) -> dict:
    '''Internal API for returning one organisation unit.

    '''

    if not unit:
        unit = c.organisationenhed.get(unitid)

        if not unit or not common.is_reg_valid(unit):
            return None

    attrs = unit['attributter']['organisationenhedegenskaber'][0]
    rels = unit['relationer']

    r = {
        'name': attrs['enhedsnavn'],
        'user_key': attrs['brugervendtnoegle'],
        'uuid': unitid,
    }

    if validity is not None:
        r[keys.VALIDITY] = validity

    if details is UnitDetails.ORG:
        r[keys.ORG] = org.get_one_organisation(c, rels['tilhoerer'][0]['uuid'])

    elif details is UnitDetails.NCHILDREN:
        children = c.organisationenhed(overordnet=unitid, gyldighed='Aktiv')

        r['child_count'] = len(children)

    elif details is UnitDetails.FULL:
        r['parent'] = get_one_orgunit(c, rels['overordnet'][0]['uuid'],
                                      details=UnitDetails.MINIMAL)

        r['children'] = [
            get_one_orgunit(c, childid, child)
            for childid, child in
            c.organisationenhed.get_all(overordnet=unitid, gyldighed='Aktiv')
        ]
        r['children'].sort(key=operator.itemgetter('name'))

    return r


@blueprint.route('/<any(o,ou):type>/<uuid:parentid>/children')
@util.restrictargs('at')
def get_children(type, parentid):
    '''Obtain the list of nested units within an organisation or an
    organisational unit.

    .. :quickref: Unit; Children

    :param type: 'o' if the parent is an organistion, and 'ou' if it's a unit.
    :param uuid parentid: The UUID of the parent.

    :queryparam date at: Current time in ISO-8601 format.

    :<jsonarr string name: Human-readable name of the unit.
    :<jsonarr string user_key: Short, unique key identifying the unit.
    :<jsonarr uuid uuid: Machine-friendly UUID of the unit.
    :<jsonarr int child_count: Number of org. units nested immediately beneath
                               the organisation.

    :status 200: Whenever the organisation or unit exists and is readable.
    :status 404: When no such organisation or unit exists, or the
                 parent was of the wrong type.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Humanistisk fakultet",
          "user_key": "hum",
          "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
          "child_count": 2
        },
        {
          "name": "Samfundsvidenskabelige fakultet",
          "user_key": "samf",
          "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0",
          "child_count": 0
        }
      ]

    '''
    c = common.get_connector()

    if type == 'o':
        scope = c.organisation
    else:
        assert type == 'ou'
        scope = c.organisationenhed

    obj = scope.get(parentid)

    if not obj or not obj.get('attributter'):
        raise werkzeug.exceptions.NotFound

    children = [
        get_one_orgunit(c, childid, child)
        for childid, child in
        c.organisationenhed.get_all(overordnet=parentid,
                                    gyldighed='Aktiv')
    ]

    children.sort(key=operator.itemgetter('name'))

    return flask.jsonify(children)


@blueprint.route('/ou/<uuid:unitid>/')
@util.restrictargs('at', 'validity')
def get_orgunit(unitid):
    '''Retrieve an organisational unit.

    .. :quickref: Unit; Get

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam string validity: Only show *past*, *present* or
        *future* values -- which the default being to show *present*
        values.

    :<jsonarr string name: Human-readable name.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string user_key: Short, unique key identifying the unit.
    :<jsonarr object org: The organisation that this unit belongs to, as
        yielded by :http:get:`/service/o/`.
    :<jsonarr object validity: The validity of this entry.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Afdeling for Fortidshistorik",
          "org": {
            "name": "Aarhus Universitet",
            "user_key": "AU",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62"
          },
          "user_key": "frem",
          "uuid": "04c78fc2-72d2-4d02-b55f-807af19eac48",
          "validity": {
            "from": "2018-01-01T00:00:00+01:00",
            "to": "2019-01-01T00:00:00+01:00"
          }
        }
      ]

    '''
    c = common.get_connector()

    return flask.jsonify([
        get_one_orgunit(
            c, unitid, details=UnitDetails.ORG,
            validity={
                keys.FROM: util.to_iso_time(start),
                keys.TO: util.to_iso_time(end),
            },
        )
        for start, end, effect in c.organisationenhed.get_effects(
            unitid,
            {
                'attributter': (
                    'organisationenhedegenskaber',
                ),
                'relationer': (
                    'enhedstype',
                    'overordnet',
                    'tilhoerer',
                ),
                'tilstande': (
                    'organisationenhedgyldighed',
                ),
            },
        )
        if c.is_effect_relevant({'from': start, 'to': end})
    ])


@blueprint.route('/ou/<uuid:unitid>/tree')
@util.restrictargs('at')
def get_orgunit_tree(unitid):
    '''Retrieve information about an organisational unit, including parent
    and children.

    .. :quickref: Unit; Tree

    :queryparam date at: Current time in ISO-8601 format.

    :<json string name: Human-readable name.
    :<json string uuid: Machine-friendly UUID.
    :<json string user_key: Short, unique key identifying the unit.
    :<json array children: Array of child units, as output by
        :http:get:`/service/ou/(uuid:unitid)/`.
    :<json object parent: Parent unit, as output by
        :http:get:`/service/ou/(uuid:unitid)/` or ``null`` if this the
        top-most unit.

    :status 404: If the organisational unit isn't found.
    :status 200: Otherwise.

    **Example Response**:

    .. sourcecode:: json

      {
        "children": [
          {
            "child_count": 0,
            "name": "Filosofisk Institut",
            "user_key": "fil",
            "uuid": "85715fc7-925d-401b-822d-467eb4b163b6"
          },
          {
            "child_count": 1,
            "name": "Historisk Institut",
            "user_key": "hist",
            "uuid": "da77153e-30f3-4dc2-a611-ee912a28d8aa"
          }
        ],
        "name": "Humanistisk fakultet",
        "parent": {
          "name": "Overordnet Enhed",
          "user_key": "root",
          "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3"
        },
        "user_key": "hum",
        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e"
      }

    '''
    c = common.get_connector()

    r = get_one_orgunit(c, unitid, details=UnitDetails.FULL)

    if r:
        return flask.jsonify(r)
    else:
        raise werkzeug.exceptions.NotFound('no such unit')


@blueprint.route('/o/<uuid:orgid>/ou/')
@util.restrictargs('at', 'start', 'limit', 'query')
def list_orgunits(orgid):
    '''Query organisational units in an organisation.

    .. :quickref: Unit; List & search

    :param uuid orgid: UUID of the organisation to search.

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by units matching this string.

    :<jsonarr string name: Human-readable name.
    :<jsonarr string uuid: Machine-friendly UUID.
    :<jsonarr string user_key: Short, unique key identifying the unit.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Samfundsvidenskabelige fakultet",
          "user_key": "samf",
          "uuid": "b688513d-11f7-4efc-b679-ab082a2055d0"
        }
      ]

    '''
    c = common.get_connector()

    args = flask.request.args

    kwargs = dict(
        limit=int(args.get('limit', 0)) or 20,
        start=int(args.get('start', 0)) or 0,
    )

    if 'query' in args:
        kwargs.update(vilkaarligattr='%{}%'.format(args['query']))

    return flask.jsonify([
        get_one_orgunit(c, unitid, unit, details=UnitDetails.MINIMAL)
        for unitid, unit in c.organisationenhed.get_all(
            tilhoerer=str(orgid),
            gyldighed='Aktiv',
            **kwargs,
        )
    ])


@blueprint.route('/ou/create', methods=['POST'])
def create_org_unit():
    """Creates new organisational unit

    .. :quickref: Unit; Create

    :statuscode 200: Creation succeeded.

    **Example Request**:

    Request payload contains a list of creation objects, each differentiated
    by the attribute 'type'. Each of these object types are detailed below:

    :<json string name: The name of the org unit
    :<json string parent: The parent org unit
    :<json string org_unit_type: The type of org unit
    :<json list addresses: A list of address objects.
    :<json object validity: The validity of the created object.

    Validity objects are defined as such:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "name": "Name",
        "parent": {
          "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
        },
        "org_unit_type": {
          "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
        },
        "valid_from": "2016-01-01T00:00:00+00:00",
        "valid_to": "2018-01-01T00:00:00+00:00"
      }

    """

    c = lora.Connector()

    req = flask.request.get_json()

    name = req.get(keys.NAME)
    parent_uuid = req.get(keys.PARENT).get('uuid')
    organisationenhed_get = c.organisationenhed.get(parent_uuid)
    org_uuid = organisationenhed_get['relationer']['tilhoerer'][0]['uuid']
    org_unit_type_uuid = req.get(keys.ORG_UNIT_TYPE).get('uuid')
    # addresses = req.get(keys.ADDRESSES)
    valid_from = common.get_valid_from(req)
    valid_to = common.get_valid_to(req)

    # TODO
    bvn = "{} {}".format(name, uuid.uuid4())

    # TODO: Process address objects

    org_unit = common.create_organisationsenhed_payload(
        valid_from=valid_from,
        valid_to=valid_to,
        enhedsnavn=name,
        brugervendtnoegle=bvn,
        tilhoerer=org_uuid,
        enhedstype=org_unit_type_uuid,
        overordnet=parent_uuid,
        # adresser=addresses,
    )

    unitid = c.organisationenhed.create(org_unit)

    return flask.jsonify(unitid)


@blueprint.route('/ou/<uuid:unitid>/edit', methods=['POST'])
def edit_org_unit(unitid):
    """Edits an organisational unit

    .. :quickref: Unit; Edit

    :statuscode 200: The edit succeeded.

    **Example Request**:

    :param unitid: The UUID of the organisational unit.

    :<json object original: An **optional** object containing the original
        state of the org unit to be overwritten. If supplied, the change will
        modify the existing registration on the org unit object.
        Detailed below.
    :<json object data: An object containing the changes to be made to the
        org unit. Detailed below.

    The **original** and **data** objects follow the same structure.
    Every field in **original** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string name: The name of the org unit
    :<jsonarr string parent: The parent org unit
    :<jsonarr string org_unit_type: The type of org unit
    :<jsonarr object validity: The validities of the changes.

    Validity objects are defined as such:

    :<jsonarr string from: The from date, in ISO 8601.
    :<jsonarr string to: The to date, in ISO 8601.

    .. sourcecode:: json

      {
        "original": {
          "name": "Pandekagehuset",
          "parent": {
            "uuid": "62ec821f-4179-4758-bfdf-134529d186e9"
          },
          "org_unit_type": {
            "uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"
          },
          "validity": {
            "from": "2016-01-01T00:00:00+00:00",
            "to": null
          }
        },
        "data": {
          "name": "Vaffelhuset",
          "validity": {
            "from": "2016-01-01T00:00:00+00:00",
          }
        }
      }
    """

    req = flask.request.get_json()

    # Get the current org-unit which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationenhed.get(uuid=unitid)

    data = req.get('data')
    new_from = common.get_valid_from(data)
    new_to = common.get_valid_to(data)

    payload = dict()
    payload['note'] = 'Rediger organisationsenhed'

    original_data = req.get('original')
    if original_data:
        # We are performing an update
        old_from = common.get_valid_from(original_data)
        old_to = common.get_valid_to(original_data)
        payload = common.inactivate_old_interval(
            old_from, old_to, new_from, new_to, payload,
            ('tilstande', 'organisationenhedgyldighed')
        )

    update_fields = list()

    # Always update gyldighed
    update_fields.append((
        mapping.ORG_UNIT_GYLDIGHED_FIELD,
        {'gyldighed': "Aktiv"}
    ))

    if keys.NAME in data.keys():
        update_fields.append((
            mapping.ORG_UNIT_EGENSKABER_FIELD,
            {'enhedsnavn': data[keys.NAME]}
        ))

    if keys.ORG_UNIT_TYPE in data.keys():
        update_fields.append((
            mapping.ORG_UNIT_TYPE_FIELD,
            {'uuid': data[keys.ORG_UNIT_TYPE]['uuid']}
        ))

    if keys.PARENT in data.keys():
        update_fields.append((
            mapping.PARENT_FIELD,
            {'uuid': data[keys.PARENT]['uuid']}
        ))

    payload = common.update_payload(new_from, new_to, update_fields, original,
                                    payload)

    bounds_fields = list(
        mapping.ORG_UNIT_FIELDS.difference({x[0] for x in update_fields}))
    payload = common.ensure_bounds(new_from, new_to, bounds_fields, original,
                                   payload)

    c.organisationenhed.update(payload, unitid)

    return flask.jsonify(unitid)


@blueprint.route('/ou/<uuid:unitid>/terminate', methods=['POST'])
def terminate_org_unit(unitid):
    """Terminates an organisational unit from a specified date.

    .. :quickref: Unit; Terminate

    :statuscode 200: The termination succeeded.

    :param unitid: The UUID of the organisational unit to be terminated.

    :<json object validity: The date on which the termination should happen,
        in ISO 8601.

    **Example Request**:

    .. sourcecode:: json

      {
        "validity": {
          "from": "2016-01-01T00:00:00+00:00"
        }
      }
    """
    date = common.get_valid_from(flask.request.get_json())

    obj_path = ('tilstande', 'organisationenhedgyldighed')
    val_inactive = {
        'gyldighed': 'Inaktiv',
        'virkning': common._create_virkning(date, 'infinity')
    }

    payload = common.set_object_value(dict(), obj_path, [val_inactive])
    payload['note'] = 'Afslut enhed'

    lora.Connector().organisationenhed.update(payload, unitid)

    return flask.jsonify(unitid)

    # TODO: Afkort adresser?


@blueprint.route('/ou/<uuid:unitid>/history/', methods=['GET'])
def get_org_unit_history(unitid):
    """
    Get the history of an org unit
    :param unitid: The UUID of the org unit

    **Example response**:

    :<jsonarr string from: When the change is active from
    :<jsonarr string to: When the change is active to
    :<jsonarr string action: The action performed
    :<jsonarr string life_cycle_code: The type of action performed
    :<jsonarr string user_ref: A reference to the user who made the change

    .. sourcecode:: json

      [
        {
          "from": "2018-02-21T13:25:24.391793+01:00",
          "to": "infinity",
          "action": "Afslut enhed",
          "life_cycle_code": "Rettet",
          "user_ref": "42c432e8-9c4a-11e6-9f62-873cf34a735f"
        },
        {
          "from": "2018-02-21T13:25:24.343010+01:00",
          "to": "2018-02-21T13:25:24.391793+01:00",
          "action": "Rediger organisationsenhed",
          "life_cycle_code": "Rettet",
          "user_ref": "42c432e8-9c4a-11e6-9f62-873cf34a735f"
        },
        {
          "from": "2018-02-21T13:25:24.271516+01:00",
          "to": "2018-02-21T13:25:24.343010+01:00",
          "action": "Rediger organisationsenhed",
          "life_cycle_code": "Rettet",
          "user_ref": "42c432e8-9c4a-11e6-9f62-873cf34a735f"
        },
        {
          "from": "2018-02-21T13:25:24.214514+01:00",
          "to": "2018-02-21T13:25:24.271516+01:00",
          "action": "Oprettet i MO",
          "life_cycle_code": "Opstaaet",
          "user_ref": "42c432e8-9c4a-11e6-9f62-873cf34a735f"
        }
      ]

    """

    c = lora.Connector()
    unit_registrations = c.organisationenhed.get(uuid=unitid,
                                                 registreretfra='-infinity',
                                                 registrerettil='infinity')

    history_entries = list(map(common.convert_reg_to_history,
                               unit_registrations))

    return flask.jsonify(history_entries)
