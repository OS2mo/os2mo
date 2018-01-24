#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


'''
Engagements
---------

This section describes how to interact with engagements.

'''


import copy
import functools
from typing import List

import flask

from ..converters import reading, writing
from .. import lora, util

blueprint = flask.Blueprint('employee', __name__, static_url_path='',
                            url_prefix='/service')


@blueprint.route('/e/<uuid:employee_uuid>/create', methods=['POST'])
def create_employee_role(employee_uuid):
    """Creates new roles for the given employee.

    .. :quickref: Employee; Create

    :statuscode 200: Creation succeeded.

    **Example Request**:

    Request payload contains a list of creation objects, each differentiated
    by the attribute 'type'. Each of these object types are detailed below:



    **Engagement**:

    :param employee_uuid: The UUID of the employee to be moved.

    :<jsonarr string type: engagement
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

    **IT**:

    **Leader**:

    **Role**:

    """

    handlers = {
        'engagement': create_engagement,
        # 'association': create_association,
        # 'it': create_it,
        'contact': writing.create_contact,
        # 'leader': create_leader,
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

        handler(str(employee_uuid), req)

    # TODO:
    return flask.jsonify(employee_uuid), 200


@blueprint.route('/e/<uuid:employee_uuid>/edit', methods=['POST'])
def edit_employee_role(employee_uuid):
    """Edits an employee

    .. :quickref: Employee; Edit employee

    :statuscode 200: The edit succeeded.

    **Example Request**:

    Request payload contains a list of edit objects, each differentiated
    by the attribute 'type'. Each of these object types are detailed below:

    **Engagement**:

    :param employee_uuid: The UUID of the employee to be moved.

    :<json string type: engagement,
    :<json string uuid: The UUID of the engagement,
    :<json object overwrite: An optional object containing the original state
        of the engagement to be overwritten. If supplied, the change will
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
    """Terminates an employee and all of his roles from a specified date.

    .. :quickref: Employee; Terminate

    :statuscode 200: The termination succeeded.

    :param employee_uuid: The UUID of the employee to be terminated.

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

    engagement = create_engagement_payload(
        employee_uuid, req
    )

    lora.Connector().organisationfunktion.create(engagement)


def create_engagement_payload(employee_uuid, req) -> dict:

    org_unit_uuid = req.get('org_unit_uuid')
    org_uuid = req.get('org_uuid')
    job_title_uuid = req.get('job_title_uuid')
    engagement_type_uuid = req.get('engagement_type_uuid')
    valid_from = req.get('valid_from')
    valid_to = req.get('valid_to')
    virkning = _create_virkning(valid_from, valid_to)

    org_funk = {
        'note': 'Oprettet i MO',
        'attributter': {
            'organisationfunktionegenskaber': [
                {
                    'funktionsnavn': 'Engagement',
                    'brugervendtnoegle': "{} {}".format(employee_uuid,
                                                        org_unit_uuid)
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
            'organisatoriskfunktionstype': [
                {
                    'uuid': engagement_type_uuid
                }
            ],
            'tilknyttedebrugere': [
                {
                    'uuid': employee_uuid
                }
            ],
            'tilknyttedeorganisationer': [
                {
                    'uuid': org_uuid
                }
            ],
            'tilknyttedeenheder': [
                {
                    'uuid': org_unit_uuid
                }
            ],
            'opgaver': [
                {
                    'uuid': job_title_uuid
                }
            ]
        }
    }

    org_funk = _set_virkning(org_funk, virkning)

    return org_funk


def edit_engagement(employee_uuid, req):
    engagement_uuid = req.get('uuid')
    # Get the current org-funktion which the user wants to change
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')
    original = c.organisationfunktion.get(uuid=engagement_uuid)
    payload = edit_engagement_payload(req, original)
    c.organisationfunktion.update(payload, engagement_uuid)


def edit_engagement_payload(req, original):

    payload = {}

    data = req.get('data')
    new_from = data.get('valid_from')
    new_to = data.get('valid_to')

    note = 'Rediger engagement'

    overwrite = req.get('overwrite')
    if overwrite:
        # We are performing an update
        old_from = overwrite.get('valid_from')
        old_to = overwrite.get('valid_to')
        payload = _inactivate_old_interval(
            old_from, old_to, new_from, new_to, payload,
            ['tilstande', 'organisationfunktiongyldighed']
        )

    # Always update gyldighed
    fields = [
        (['tilstande', 'organisationfunktiongyldighed'],
         {'gyldighed': "Aktiv"}),
    ]

    if 'job_title_uuid' in data.keys():
        fields.append(
            (['relationer', 'opgaver'],
             {'uuid': data.get('job_title_uuid')}),
        )

    if 'engagement_type_uuid' in data.keys():
        fields.append(
            (['relationer', 'organisatoriskfunktionstype'],
             {'uuid': data.get('engagement_type_uuid')}),
        )

    if 'org_unit_uuid' in data.keys():
        fields.append(
            (['relationer', 'tilknyttedeenheder'],
             {'uuid': data.get('org_unit_uuid')}),
        )

    payload = update_org_funktion_payload(new_from, new_to, note,
                                          fields, original, payload)

    return payload


def update_org_funktion_payload(from_time, to_time, note, fields, original,
                                payload):
    for field in fields:
        payload = _create_payload(
            from_time, to_time,
            field[0],
            field[1],
            note,
            payload,
            original)

    paths = [field[0] for field in fields]

    payload = _ensure_object_effect_bounds(
        from_time, to_time,
        original, payload,
        get_remaining_org_funk_fields(paths)
    )

    return payload


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


def _ensure_object_effect_bounds(lower_bound: str, upper_bound: str,
                                 original: dict, payload: dict,
                                 paths: List[List[str]]) -> dict:
    """
    Given an original object and a set of time bounds from a prospective
    update, ensure that ranges on object validities are sane, when the
    update is performed. Operates under the assumption that we do not have
    any overlapping intervals in validity ranges

    :param lower_bound: The lower bound, in ISO-8601
    :param upper_bound: The upper bound, in ISO-8601
    :param original: The original object, as it exists in LoRa
    :param payload: An existing payload to add the updates to
    :param paths: A list of paths to be checked on the original object
    :return: The payload with the additional updates applied, if relevant
    """

    note = payload.get('note')

    for path in paths:
        # Get list of original relevant properties, sorted by start_date
        orig_list = functools.reduce(lambda x, y: x.get(y, {}), path, original)
        if not orig_list:
            continue
        sorted_rel = sorted(orig_list, key=lambda x: x['virkning']['from'])
        first = sorted_rel[0]
        last = sorted_rel[-1]

        # Handle lower bound
        if lower_bound < first['virkning']['from']:
            props = copy.deepcopy(first)
            del props['virkning']
            payload = _create_payload(
                lower_bound,
                first['virkning']['to'],
                path,
                props,
                note,
                payload,
                original
            )

        # Handle upper bound
        if last['virkning']['to'] < upper_bound:
            props = copy.deepcopy(last)
            del props['virkning']
            payload = _create_payload(
                last['virkning']['from'],
                upper_bound,
                path,
                props,
                note,
                payload,
                original
            )

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


def _inactivate_old_interval(old_from: str, old_to: str, new_from: str,
                             new_to: str, payload: dict,
                             path: List[str]) -> dict:
    """
    Create 'inactivation' updates based on two sets of from/to dates
    :param old_from: The old 'from' time, in ISO-8601
    :param old_to: The old 'to' time, in ISO-8601
    :param new_from: The new 'from' time, in ISO-8601
    :param new_to: The new 'to' time, in ISO-8601
    :param payload: An existing payload to add the updates to
    :param path: The path to where the object's 'gyldighed' is located
    :return: The payload with the inactivation updates added, if relevant
    """
    if old_from < new_from:
        payload = _create_payload(
            old_from,
            new_from,
            path,
            {
                'gyldighed': "Inaktiv"
            },
            payload.get('note'),
            payload
        )
    if new_to < old_to:
        payload = _create_payload(
            new_to,
            old_to,
            path,
            {
                'gyldighed': "Inaktiv"
            },
            payload.get('note'),
            payload
        )
    return payload


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


def get_remaining_org_funk_fields(obj_paths: List[List[str]]):
    # TODO: Maybe fetch this information dynamically from LoRa?
    fields = {
        ('attributter', 'organisationfunktionegenskaber'),
        ('tilstande', 'organisationfunktiongyldighed'),
        ('relationer', 'organisatoriskfunktionstype'),
        ('relationer', 'opgaver'),
        ('relationer', 'tilknyttedebrugere'),
        ('relationer', 'tilknyttedeenheder'),
        ('relationer', 'tilknyttedeorganisationer'),
    }

    tupled_set = {tuple(x) for x in obj_paths}
    diff = fields.difference(tupled_set)

    return [list(x) for x in diff]


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
