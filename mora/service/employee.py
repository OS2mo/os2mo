#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''
Employees
---------

This section describes how to interact with employees.

'''


import copy
import functools
from typing import List, Tuple

import flask

import mora.mapping.engagement as engagement
from mora.service.common import PropTuple, PropTypes
from . import common
from .. import lora, util
from ..converters import reading, writing

blueprint = flask.Blueprint('employee', __name__, static_url_path='',
                            url_prefix='/service')

ENGAGEMENT_KEY = 'Engagement'
ASSOCIATION_KEY = 'Tilknytning'

@blueprint.route('/o/<uuid:orgid>/e/')
@util.restrictargs('at', 'start', 'limit', 'query')
def list_employees(orgid):
    '''Query employees in an organisation.

    .. :quickref: Employee; List & search

    :param uuid orgid: UUID of the organisation to search.

    :queryparam date at: Current time in ISO-8601 format.
    :queryparam int start: Index of first unit for paging.
    :queryparam int limit: Maximum items
    :queryparam string query: Filter by employees matching this string.
        Please note that this only applies to attributes of the user, not the
        relations or engagements they have.

    :<jsonarr string name: Human-readable name.
    :<jsonarr string uuid: Machine-friendly UUID.

    :status 200: Always.

    **Example Response**:

    .. sourcecode:: json

      [
        {
          "name": "Hans Bruger",
          "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3"
        },
        {
          "name": "Joe User",
          "uuid": "cd2dcfad-6d34-4553-9fee-a7023139a9e8"
        }
      ]

    '''

    # TODO: share code with list_orgunits?

    c = common.get_connector()

    args = flask.request.args

    kwargs = dict(
        limit=int(args.get('limit', 0)) or 20,
        start=int(args.get('start', 0)) or 0,
        tilhoerer=str(orgid),

        # this makes the search go slow :(
        gyldighed='Aktiv',
    )

    if 'query' in args:
        kwargs.update(vilkaarligattr='%{}%'.format(args['query']))

    return flask.jsonify([
        {
            'name': bruger['attributter']['brugeregenskaber'][0]['brugernavn'],
            'uuid': brugerid,
        }
        for brugerid, bruger in c.bruger.get_all(**kwargs)
    ])


@blueprint.route('/e/<uuid:id>/')
@util.restrictargs('at')
def get_employee(id, raw=False):
    '''Retrieve an employee.

    .. :quickref: Employee; Get

    :queryparam date at: Current time in ISO-8601 format.

    :<json string name: Human-readable name.
    :<json string uuid: Machine-friendly UUID.
    :<json string cpr_no: CPR number of for the corresponding person.

    :status 200: Whenever the user ID is valid and corresponds to an
        existing user.
    :status 404: Otherwise.

    **Example Response**:

    .. sourcecode:: json

      {
        "cpr_no": "1011101010",
        "name": "Hans Bruger",
        "uuid": "9917e91c-e3ee-41bf-9a60-b024c23b5fe3"
      }

    '''
    c = common.get_connector()

    user = c.bruger.get(id)

    r = {
        'uuid': id,

        'name':
        user['attributter']
        ['brugeregenskaber'][0]
        ['brugernavn'],

        'cpr_no':
        user['relationer']
        ['tilknyttedepersoner'][0]
        ['urn'].rsplit(':', 1)[-1],
    }

    if raw:
        return r
    else:
        return flask.jsonify(r)

@blueprint.route('/e/<uuid:employee_uuid>/create', methods=['POST'])
def create_employee(employee_uuid):
    """Creates new mapping relations

    .. :quickref: Employee; Create

    :statuscode 200: Creation succeeded.

    :param employee_uuid: The UUID of the mapping.

    **Example Request**:

    Request payload contains a list of creation objects, each differentiated
    by the attribute 'type'. Each of these object types are detailed below:

    **Engagement**:

    :<jsonarr string type: **"engagement"**
    :<jsonarr string org_unit_uuid: The UUID of the associated org unit
    :<jsonarr string org_uuid: The UUID of the associated organisation
    :<jsonarr string job_title_uuid: The UUID of the job title of the engagment
    :<jsonarr string engagement_type_uuid: The UUID of the engagement type
    :<jsonarr string valid_from: The date from which the role should be valid,
        in ISO 8601.
    :<jsonarr string valid_to: The date which the role should be valid to,
        in ISO 8601.

    .. sourcecode:: json

      [
        {
          "type": "engagement",
          "org_unit_uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec",
          "org_uuid": "f494ad89-039d-478e-91f2-a63566554bd6",
          "job_title_uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
          "engagement_type_uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
          "valid_from": "2016-01-01T00:00:00+00:00",
          "valid_to": "2018-01-01T00:00:00+00:00",
        }
      ]

    **Association**:

    :<jsonarr string type: **"association"**
    :<jsonarr string org_unit_uuid: The UUID of the associated org unit
    :<jsonarr string org_uuid: The UUID of the associated organisation
    :<jsonarr string job_title_uuid: The UUID of the job title of the
        association
    :<jsonarr string association_type_uuid: The UUID of the association type
    :<jsonarr string valid_from: The date from which the role should be valid,
        in ISO 8601.
    :<jsonarr string valid_to: The date which the role should be valid to,
        in ISO 8601.

    .. sourcecode:: json

      [
        {
          "type": "association",
          "org_unit_uuid": "a30f5f68-9c0d-44e9-afc9-04e58f52dfec",
          "org_uuid": "f494ad89-039d-478e-91f2-a63566554bd6",
          "job_title_uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8",
          "association_type_uuid": "62ec821f-4179-4758-bfdf-134529d186e9",
          "valid_from": "2016-01-01T00:00:00+00:00",
          "valid_to": "2018-01-01T00:00:00+00:00",
        }
      ]

    **IT**:

    **Leader**:

    **Role**:

    """

    handlers = {
        'engagement': create_engagement,
        'association': create_association,
        # 'it': create_it,
        # 'role': create_role,
        'contact': writing.create_contact,
        # 'leader': create_leader,
        # 'absence': create_absence,
    }

    reqs = flask.request.get_json()
    for req in reqs:
        role_type = req.get('type')
        handler = handlers.get(role_type)

        # TODO: Find a better way to handle this, probably
        if not req.get('valid_to'):
            req['valid_to'] = 'infinity'

        if not handler:
            return flask.jsonify('Unknown role type'), 400

        # TODO: Find a better way to handle this...
        if not req.get('valid_to'):
            req['valid_to'] = 'infinity'

        handler(str(employee_uuid), req)

    # TODO:
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/edit', methods=['POST'])
def edit_employee(employee_uuid):
    """Edits an mapping

    .. :quickref: Employee; Edit mapping

    :statuscode 200: The edit succeeded.

    **Example Request**:

    Request payload contains a list of edit objects, each differentiated
    by the attribute 'type'. Each of these object types are detailed below:

    **Engagement**:

    :param employee_uuid: The UUID of the mapping to be moved.

    :<json string type: **"engagement"**
    :<json string uuid: The UUID of the engagement,
    :<json object overwrite: An **optional** object containing the original
        state of the engagement to be overwritten. If supplied, the change
        will modify the existing registration on the engagement object.
        Detailed below. Note, this object is only optional for *engagement*.
    :<json object data: An object containing the changes to be made to the
        engagement. Detailed below.

    The **overwrite** and **data** objects follow the same structure.
    Every field in **overwrite** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string valid_from: The from date, in ISO 8601.
    :<jsonarr string valid_to: The to date, in ISO 8601.
    :<jsonarr string org_unit_uuid: The UUID of the associated org unit
    :<jsonarr string job_title_uuid: The UUID of the job title of the
        engagement
    :<jsonarr string engagement_type_uuid: The UUID of the engagement type

    .. sourcecode:: json

      {
        "type": "engagement",
        "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
        "overwrite": {
          "valid_from": "2016-01-01T00:00:00+00:00",
          "valid_to": "2018-01-01T00:00:00+00:00",
          "job_title_uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b",
          "engagement_type_uuid": "743a6448-2b0b-48cf-8a2e-bf938a6181ee",
          "org_unit_uuid": "04f73c63-1e01-4529-af2b-dee36f7c83cb"
        },
        "data": {
          "valid_from": "2016-01-01T00:00:00+00:00",
          "valid_to": "2019-01-01T00:00:00+00:00",
          "job_title_uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b",
        }
      }

    **Association**:

    :param employee_uuid: The UUID of the mapping to be moved.

    :<json string type: **"association"**
    :<json string uuid: The UUID of the association,
    :<json object overwrite: An object containing the original state
        of the association to be overwritten. If supplied, the change will
        modify the existing registration on the engagement object.
        Detailed below.
    :<json object data: An object containing the changes to be made to the
        engagement. Detailed below.

    The **overwrite** and **data** objects follow the same structure.
    Every field in **overwrite** is required, whereas **data** only needs
    to contain the fields that need to change along with the validity dates.

    :<jsonarr string valid_from: The from date, in ISO 8601.
    :<jsonarr string valid_to: The to date, in ISO 8601.
    :<jsonarr string org_unit_uuid: The UUID of the associated org unit
    :<jsonarr string job_title_uuid: The UUID of the job title of the
        engagement
    :<jsonarr string engagement_type_uuid: The UUID of the engagement type

    .. sourcecode:: json

      {
        "type": "engagement",
        "uuid": "de9e7513-1934-481f-b8c8-45336387e9cb",
        "overwrite": {
          "valid_from": "2016-01-01T00:00:00+00:00",
          "valid_to": "2018-01-01T00:00:00+00:00",
          "job_title_uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b",
          "engagement_type_uuid": "743a6448-2b0b-48cf-8a2e-bf938a6181ee",
          "org_unit_uuid": "04f73c63-1e01-4529-af2b-dee36f7c83cb"
        },
        "data": {
          "valid_from": "2016-01-01T00:00:00+00:00",
          "valid_to": "2019-01-01T00:00:00+00:00",
          "job_title_uuid": "5b56432c-f289-4d81-a328-b878ea0a4e1b",
        }
      }
    """

    handlers = {
        'engagement': edit_engagement
        # 'association': edit_association,
        # 'it': edit_it,
        # 'contact': edit_contact,
        # 'leader': edit_leader,
    }

    reqs = flask.request.get_json()

    for req in reqs:
        role_type = req.get('type')
        handler = handlers.get(role_type)

        # TODO: Find a better way to handle this, probably
        if not req.get('data').get('valid_to'):
            req['data']['valid_to'] = 'infinity'

        if not handler:
            return flask.jsonify('Unknown role type'), 400

        handler(str(employee_uuid), req)

    # TODO: Figure out the response
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/terminate', methods=['POST'])
def terminate_employee(employee_uuid):
    """Terminates an mapping and all of his roles from a specified date.

    .. :quickref: Employee; Terminate

    :statuscode 200: The termination succeeded.

    :param employee_uuid: The UUID of the mapping to be terminated.

    :<json string valid_from: The date on which the termination should happen,
                              in ISO 8601.

    **Example Request**:

    .. sourcecode:: json

      {
        "valid_from": "2016-01-01T00:00:00+00:00"
      }
    """
    date = flask.request.get_json().get('valid_from')

    engagements = reading.get_engagements(userid=employee_uuid,
                                          effective_date=date)
    for engagement in engagements:
        engagement_uuid = engagement.get('uuid')
        terminate_engagement(engagement_uuid, date)

    # TODO: Terminate Tilknytning
    # TODO: Terminate IT
    # TODO: Terminate Kontakt
    # TODO: Terminate Rolle
    # TODO: Terminate Leder
    # TODO: Terminate Orlov

    # TODO:
    return flask.jsonify(employee_uuid), 200


def create_engagement(employee_uuid, req):
    # TODO: Validation

    org_unit_uuid = req.get('org_unit_uuid')
    org_uuid = req.get('org_uuid')
    job_title_uuid = req.get('job_title_uuid')
    engagement_type_uuid = req.get('engagement_type_uuid')
    valid_from = req.get('valid_from')
    valid_to = req.get('valid_to')

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, ENGAGEMENT_KEY)

    engagement = create_organisationsfunktion_payload(
        funktionsnavn=ENGAGEMENT_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=engagement_type_uuid,
        opgaver=[job_title_uuid]
    )

    lora.Connector().organisationfunktion.create(engagement)


def create_association(employee_uuid, req):
    # TODO: Validation

    org_unit_uuid = req.get('org_unit_uuid')
    org_uuid = req.get('org_uuid')
    job_title_uuid = req.get('job_title_uuid')
    association_type_uuid = req.get('association_type_uuid')
    valid_from = req.get('valid_from')
    valid_to = req.get('valid_to')

    bvn = "{} {} {}".format(employee_uuid, org_unit_uuid, ASSOCIATION_KEY)

    association = create_organisationsfunktion_payload(
        funktionsnavn=ASSOCIATION_KEY,
        valid_from=valid_from,
        valid_to=valid_to,
        brugervendtnoegle=bvn,
        tilknyttedebrugere=[employee_uuid],
        tilknyttedeorganisationer=[org_uuid],
        tilknyttedeenheder=[org_unit_uuid],
        funktionstype=association_type_uuid,
        opgaver=[job_title_uuid]
    )

    lora.Connector().organisationfunktion.create(association)


def create_organisationsfunktion_payload(
    funktionsnavn: str,
    valid_from: str,
    valid_to: str,
    brugervendtnoegle: str,
    tilknyttedebrugere: List[str],
    tilknyttedeorganisationer: List[str],
    tilknyttedeenheder: List[str] = None,
    funktionstype: str = None,
    opgaver: List[str] = None) -> dict:
    virkning = _create_virkning(valid_from, valid_to)

    org_funk = {
        'note': 'Oprettet i MO',
        'attributter': {
            'organisationfunktionegenskaber': [
                {
                    'funktionsnavn': funktionsnavn,
                    'brugervendtnoegle': brugervendtnoegle
                },
            ],
        },
        'tilstande': {
            'organisationfunktiongyldighed': [
                {
                    'gyldighed': 'Aktiv',
                },
            ],
        },
        'relationer': {
            'tilknyttedebrugere': [
                {
                    'uuid': uuid
                } for uuid in tilknyttedebrugere
            ],
            'tilknyttedeorganisationer': [
                {
                    'uuid': uuid
                } for uuid in tilknyttedeorganisationer
            ]
        }
    }

    if tilknyttedeenheder:
        org_funk['relationer']['tilknyttedeenheder'] = [{
            'uuid': uuid
        } for uuid in tilknyttedeenheder]

    if funktionstype:
        org_funk['relationer']['organisatoriskfunktionstype'] = [{
            'uuid': funktionstype
        }]

    if opgaver:
        org_funk['relationer']['opgaver'] = [{
            'uuid': uuid
        } for uuid in opgaver]

    org_funk = _set_virkning(org_funk, virkning)

    return org_funk


def edit_engagement(employee_uuid, req):
    engagement_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=engagement_uuid)

    data = req.get('data')
    new_from = data.get('valid_from')
    new_to = data.get('valid_to')

    payload = dict()
    payload['note'] = 'Rediger engagement'

    # overwrite = req.get('overwrite')
    # if overwrite:
    #     # We are performing an update
    #     old_from = overwrite.get('valid_from')
    #     old_to = overwrite.get('valid_to')
    #     payload = _inactivate_old_interval(
    #         old_from, old_to, new_from, new_to, payload,
    #         ['tilstande', 'organisationfunktiongyldighed']
    #     )

    update_fields = list()

    # Always update gyldighed
    update_fields.append((
        engagement.gyldighed,
        {'gyldighed': "Aktiv"}
    ))

    if 'job_title_uuid' in data.keys():
        update_fields.append((
            engagement.job_title,
            {'uuid': data.get('job_title_uuid')}
        ))

    if 'engagement_type_uuid' in data.keys():
        update_fields.append((
            engagement.engagement_type,
            {'uuid': data.get('engagement_type_uuid')},
        ))

    if 'org_unit_uuid' in data.keys():
        update_fields.append((
            engagement.org_unit,
            {'uuid': data.get('org_unit_uuid')},
        ))

    payload = update_payload(new_from, new_to, update_fields, original, payload)

    bounds_props = list(set(map(lambda x: x[0], update_fields)).difference(
        engagement.props))
    payload = ensure_bounds(new_from, new_to, bounds_props, original, payload)

    c.organisationfunktion.update(payload, engagement_uuid)


def edit_association(employee_uuid, req):
    pass


def update_payload(valid_from: str,
                   valid_to: str,
                   relevant_props_tuples: List[Tuple[PropTuple, dict]],
                   obj: dict,
                   payload: dict):
    remainder = copy.deepcopy(obj)

    for prop_tuple in relevant_props_tuples:
        field = prop_tuple[0]
        val = prop_tuple[1]
        val.setdefault('virkning', {})
        val['virkning']['from'] = valid_from
        val['virkning']['to'] = valid_to

        # Split original object in relevant values, and remainder
        props, remainder = split_object(remainder, field.path, field.filter_fn)

        if field.type == PropTypes.ADAPTED_ZERO_TO_MANY:
            # 'Fake' zero-to-one relation. Merge into existing list.
            updated_props = _merge_obj_effects(props, val)
        elif field.type == PropTypes.ZERO_TO_MANY:
            # Actual zero-to-many relation. Just append.
            updated_props = props + [val]
        else:
            # Zero-to-one relation - LoRa does the merging for us,
            # so disregard existing props
            updated_props = [val]

        update = set_object_value({}, field.path, updated_props)

        # Add to existing update object
        payload = merge_objs(payload, update)

    return payload


def ensure_bounds(valid_from: str,
                  valid_to: str,
                  props: List[PropTuple],
                  obj: dict,
                  payload: dict):
    remainder = copy.deepcopy(obj)

    for field in props:
        props, remainder = split_object(remainder, field.path, field.filter_fn)
        if not props:
            continue
        if field.type == PropTypes.ADAPTED_ZERO_TO_MANY:
            # If adapted zero-to-many, move first and last, and merge
            updated_props = sorted(props, key=lambda x: x['virkning']['from'])
            first = updated_props[0]
            last = updated_props[-1]
            # Check bounds on first
            if valid_from < first['virkning']['from']:
                first['virkning']['from'] = valid_from
            if last['virkning']['to'] < valid_to:
                last['virkning']['to'] = valid_to

        elif field.type == PropTypes.ZERO_TO_MANY:
            # Don't touch virkninger on zero-to-many
            updated_props = props

        else:
            # Zero-to-one. Move first and last. LoRa does the merging.
            sorted_props = sorted(props, key=lambda x: x['virkning']['from'])
            first = sorted_props[0]
            last = sorted_props[-1]
            if valid_from < first['virkning']['from']:
                first['virkning']['from'] = valid_from
            if valid_to < last['virkning']['to']:
                last['virkning']['to'] = valid_to
            updated_props = [first]
            if last is not first:
                updated_props.append(last)

        update = set_object_value({}, field.path, updated_props)

        # Add to existing update object
        payload = merge_objs(payload, update)

    return payload


def merge_objs(a, b):
    for key in b:
        if key in a:
            if isinstance(a[key], dict):
                merge_objs(a[key], b[key])
            elif isinstance(a[key], list):
                a[key].extend(b[key])
        else:
            a[key] = b[key]
    return a


def split_object(obj, path, filter_fn):
    """
    Splits object based on a path and a filter function
    Returns a list of properties from 'path' on object, satisfying 'filter_fn'
    and a modified version of obj, no longer containing said properties.

    :param obj: The object to split
    :param path: The path containing properties to extract
    :param filter_fn: A function used to filter relevant values
    """
    remainder, remainder_props = ensure_path_and_get_value(obj, path)
    relevant_props = []
    new_remainder_props = []

    for prop in remainder_props:
        if filter_fn(prop):
            relevant_props.append(prop)
        else:
            new_remainder_props.append(prop)
    set_object_value(remainder, path, new_remainder_props)

    return relevant_props, remainder


def ensure_path_and_get_value(obj, path: tuple):
    path_list = list(path)
    obj_copy = copy.deepcopy(obj)

    current_value = obj_copy
    while path_list:
        key = path_list.pop(0)
        if path_list:
            current_value = current_value.setdefault(key, {})
        else:
            current_value = current_value.setdefault(key, [])

    return obj_copy, current_value


def set_object_value(obj, path: tuple, val):
    path_list = list(path)
    obj_copy = copy.deepcopy(obj)

    current_value = obj_copy
    while path_list:
        key = path_list.pop(0)
        if path_list:
            current_value = current_value.setdefault(key, {})
        else:
            current_value[key] = val

    return obj_copy


def terminate_engagement(engagement_uuid, enddate):
    """
    Terminate the given engagement at the given date

    :param engagement_uuid: An engagement UUID
    :param enddate: The date of termination
    """
    c = lora.Connector(effective_date=enddate)

    orgfunk = c.organisationfunktion.get(engagement_uuid)

    # Create inactivation object
    startdate = [
        g['virkning']['from'] for g in
        orgfunk['tilstande']['organisationfunktiongyldighed']
        if g['gyldighed'] == 'Aktiv'
    ][0]

    payload = inactivate_org_funktion(startdate, enddate, "Afslut engagement")
    c.organisationfunktion.update(payload, engagement_uuid)


def inactivate_org_funktion(startdate, enddate, note):
    obj_path = ['tilstande', 'organisationfunktiongyldighed']
    props_active = {'gyldighed': 'Aktiv'}
    props_inactive = {'gyldighed': 'Inaktiv'}

    payload = _create_payload(startdate, enddate, obj_path, props_active,
                              note)
    payload = _create_payload(enddate, 'infinity', obj_path, props_inactive,
                              note, payload)

    return payload


def _create_virkning(From: str, to: str, from_included=True,
                     to_included=False) -> dict:
    """
    Create virkning from frontend request.

    :param From: The "from" date.
    :param to: The "to" date.
    :param from_included: Specify if the from-date should be included or not.
    :param to_included: Specify if the to-date should be included or not.
    :return: The virkning object.
    """
    return {
        'from': util.to_lora_time(From),
        'to': util.to_lora_time(to),
        'from_included': from_included if not From == '-infinity' else False,
        'to_included': to_included if not to == 'infinity' else False
    }


def _create_payload(From: str, to: str, obj_path: list,
                    props: dict, note: str, payload: dict = None,
                    original: dict = None) -> dict:
    """
    Generate payload to send to LoRa when updating or writing new data. See
    the example below.

    :param From: The "from" date.
    :param to: The "to" date.
    :param obj_path: List with "path" to object to add.
    :param props: Properties to add.
    :param note: Note to add to the payload.
    :param payload: An already existing payload that should have extra
        properties added.
    :param original: An optional, existing object containing properties on
        "obj_path" which should be merged with props, in case of adding props
        to a zero-to-many relation.
    :return: The resulting payload (see example below).

    :Example:

    >>> _create_payload(
            '01-01-2017', '01-01-2018',
            ['tilstande', 'organisationenhedgyldighed'],
            {'gyldighed': 'Aktiv'}, 'Ret gyldighed'
        )
        {
            'tilstande': {
                'organisationenhedgyldighed': [
                    {
                        'gyldighed': 'Aktiv',
                        'virkning': {
                            'to': '2018-01-01T00:00:00+01:00',
                            'from_included': True,
                            'from': '2017-01-01T00:00:00+01:00',
                            'to_included': False
                        }
                    }
                ]
            },
            'note': 'Ret gyldighed'
        }
    """

    obj_path_copy = obj_path.copy()
    props_copy = props.copy()

    if payload:
        payload['note'] = note
    else:
        payload = {
            'note': note,
        }

    current_value = payload
    while obj_path_copy:
        key = obj_path_copy.pop(0)
        if obj_path_copy:
            if key not in current_value.keys():
                current_value[key] = {}
            current_value = current_value[key]
        else:
            props_copy['virkning'] = _create_virkning(From, to)
            if key in _zero_to_many_rels() and original:
                if key in current_value.keys():
                    merge_obj = payload
                else:
                    merge_obj = original
                orig_list = functools.reduce(lambda x, y: x.get(y),
                                             obj_path, merge_obj)
                current_value[key] = _merge_obj_effects(orig_list, props_copy)
            elif key in current_value.keys():
                current_value[key].append(props_copy)
            else:
                current_value[key] = [props_copy]

    return payload


def _merge_obj_effects(orig_objs: List[dict], new: dict) -> List[dict]:
    """
    Performs LoRa-like merging of a relation object, with a current list of
    relation objects, with regards to virkningstider,
    producing a merged list of relation to be inserted into LoRa, similar to
    how LoRa performs merging of zero-to-one relations.

    We assume that the list of objects satisfy the same contraints as a list
    of objects from a zero-to-one relation, i.e. no overlapping time periods

    :param orig_objs: A list of objects with virkningstider
    :param new: A new object with virkningstid, to be merged
                into the original list.
    :return: A list of merged objects
    """
    # TODO: Implement merging of two lists?

    sorted_orig = sorted(orig_objs, key=lambda x: x['virkning']['from'])

    result = [new]
    new_from = util.parsedatetime(new['virkning']['from'])
    new_to = util.parsedatetime(new['virkning']['to'])

    for orig in sorted_orig:
        orig_from = util.parsedatetime(orig['virkning']['from'])
        orig_to = util.parsedatetime(orig['virkning']['to'])

        if new_to <= orig_from or orig_to <= new_from:
            # Not affected, add orig as-is
            result.append(orig)
            continue

        if new_from <= orig_from:
            if orig_to <= new_to:
                # Orig is completely contained in new, ignore
                continue
            else:
                # New end overlaps orig beginning
                new_rel = copy.deepcopy(orig)
                new_rel['virkning']['from'] = util.to_lora_time(new_to)
                result.append(new_rel)
        elif new_from < orig_to:
            # New beginning overlaps with orig end
            new_obj_before = copy.deepcopy(orig)
            new_obj_before['virkning']['to'] = util.to_lora_time(new_from)
            result.append(new_obj_before)
            if new_to < orig_to:
                # New is contained in orig
                new_obj_after = copy.deepcopy(orig)
                new_obj_after['virkning']['from'] = util.to_lora_time(new_to)
                result.append(new_obj_after)

    return sorted(result, key=lambda x: x['virkning']['from'])


def _zero_to_many_rels() -> List[str]:
    # TODO: Load and cache from LoRa
    return [
        "adresser",
        "opgaver",
        "tilknyttedebrugere",
        "tilknyttedeenheder",
        "tilknyttedeorganisationer",
        "tilknyttedeitsystemer",
        "tilknyttedeinteressefaellesskaber",
        "tilknyttedepersoner"
    ]


def _set_virkning(lora_obj: dict, virkning: dict, overwrite=False) -> dict:
    """
    Adds virkning to the "leafs" of the given LoRa JSON (tree) object.

    :param lora_obj: A LoRa object with or without virkning.
    :param virkning: The virkning to set in the LoRa object
    :param overwrite: Whether any original virknings should be overwritten
    :return: The LoRa object with the new virkning

    """
    for k, v in lora_obj.items():
        if isinstance(v, dict):
            _set_virkning(v, virkning, overwrite)
        elif isinstance(v, list):
            for d in v:
                if overwrite:
                    d['virkning'] = virkning.copy()
                else:
                    d.setdefault('virkning', virkning.copy())
    return lora_obj
