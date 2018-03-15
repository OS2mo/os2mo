#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

'''Common utilities
----------------

'''

import abc
import collections
import copy
import enum
import datetime
import functools
import uuid
from typing import Callable, List, Tuple

import flask
import iso8601

from mora import util
from . import keys
from .. import lora

RELATION_TRANSLATIONS = {
    'engagement': keys.ENGAGEMENT_KEY.lower(),
    'association': keys.ASSOCIATION_KEY.lower(),
    'it': keys.ITSYSTEM_KEY.lower(),
    'role': keys.ROLE_KEY.lower(),
    'address': keys.ADDRESS_KEY.lower(),
    'manager': keys.MANAGER_KEY.lower(),
    'leave': keys.LEAVE_KEY.lower(),
}


class FieldTypes(enum.Enum):
    ZERO_TO_ONE = 0,
    ZERO_TO_MANY = 1,
    ADAPTED_ZERO_TO_MANY = 2,


class AbstractRelationDetail(abc.ABC):
    __slots__ = (
        'scope',
    )

    def __init__(self, scope):
        self.scope = scope

    @abc.abstractmethod
    def has(self, registration):
        pass

    @abc.abstractmethod
    def get(self, objid):
        pass

    @abc.abstractmethod
    def create(self, id: str, req: dict):
        pass

    @abc.abstractmethod
    def edit(self, id: str, req: dict):
        pass


FieldTuple = collections.namedtuple(
    'PropTuple',
    [
        'path',
        'type',
        'filter_fn'
    ]
)


def get_connector():
    args = flask.request.args

    loraparams = dict()

    if args.get('at'):
        loraparams['effective_date'] = iso8601.parse_date(args['at'])

    if args.get('validity'):
        loraparams['validity'] = args['validity']

    return lora.Connector(**loraparams)


class cache(collections.defaultdict):
    '''combination of functools.partial & defaultdict into one'''

    def __init__(self, func, *args, **kwargs):
        super().__init__(functools.partial(func, *args, **kwargs))

    def __missing__(self, key):
        v = self[key] = self.default_factory(key)
        return v


def inactivate_old_interval(old_from: str, old_to: str, new_from: str,
                            new_to: str, payload: dict,
                            path: tuple) -> dict:
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
        val = {
            'gyldighed': "Inaktiv",
            'virkning': _create_virkning(old_from, new_from)
        }
        payload = set_object_value(payload, path, [val])
    if new_to < old_to:
        val = {
            'gyldighed': "Inaktiv",
            'virkning': _create_virkning(new_to, old_to)
        }
        payload = set_object_value(payload, path, [val])
    return payload


def set_object_value(obj: dict, path: tuple, val: List[dict]):
    path_list = list(path)
    obj_copy = copy.deepcopy(obj)

    current_value = obj_copy
    while path_list:
        key = path_list.pop(0)
        if path_list:
            current_value = current_value.setdefault(key, {})
        else:
            if not current_value.get(key):
                current_value[key] = val
            else:
                current_value[key].extend(val)

    return obj_copy


def get_obj_value(obj, path: tuple, filter_fn: Callable = None):
    props = functools.reduce(lambda x, y: x.get(y, {}), path, obj)
    if filter_fn:
        return list(filter(filter_fn, props))
    else:
        return props


def get_field_value(field: FieldTuple, obj):
    return get_obj_value(obj, field.path, field.filter_fn)


FieldTuple.get = get_field_value


def get_effect_from(effect: dict) -> datetime.datetime:
    return util.parsedatetime(effect['virkning']['from'])


def get_effect_to(effect: dict) -> datetime.datetime:
    return util.parsedatetime(effect['virkning']['to'])


def get_effect_validity(effect):
    return {
        keys.FROM: util.to_iso_time(get_effect_from(effect)),
        keys.TO: util.to_iso_time(get_effect_to(effect)),
    }


def ensure_bounds(valid_from: datetime.datetime,
                  valid_to: datetime.datetime,
                  props: List[FieldTuple],
                  obj: dict,
                  payload: dict):

    for field in props:
        props = get_obj_value(obj, field.path, field.filter_fn)
        if not props:
            continue

        updated_props = []  # type: List[FieldTuple]
        if field.type == FieldTypes.ADAPTED_ZERO_TO_MANY:
            # If adapted zero-to-many, move first and last, and merge
            sorted_props = sorted(props, key=get_effect_from)
            first = sorted_props[0]
            last = sorted_props[-1]

            # Check bounds on first
            if valid_from < get_effect_from(first):
                first['virkning']['from'] = util.to_lora_time(valid_from)
                updated_props = sorted_props
            if get_effect_to(last) < valid_to:
                last['virkning']['to'] = util.to_lora_time(valid_to)
                updated_props = sorted_props

        elif field.type == FieldTypes.ZERO_TO_MANY:
            # Don't touch virkninger on zero-to-many
            updated_props = props
        else:
            # Zero-to-one. Move first and last. LoRa does the merging.
            sorted_props = sorted(props, key=get_effect_from)
            first = sorted_props[0]
            last = sorted_props[-1]

            if valid_from < get_effect_from(first):
                first['virkning']['from'] = util.to_lora_time(valid_from)
                updated_props.append(first)
            if get_effect_to(last) < valid_to:
                last['virkning']['to'] = util.to_lora_time(valid_to)
                if not updated_props or last is not first:
                    updated_props.append(last)

        if updated_props:
            payload = set_object_value(payload, field.path, updated_props)
    return payload


def update_payload(valid_from: datetime.datetime,
                   valid_to: datetime.datetime,
                   relevant_fields: List[Tuple[FieldTuple, dict]],
                   obj: dict,
                   payload: dict):
    for field in relevant_fields:
        field_tuple, val = field
        val['virkning'] = _create_virkning(valid_from, valid_to)

        # Get original properties
        props = get_obj_value(obj, field_tuple.path, field_tuple.filter_fn)

        if field_tuple.type == FieldTypes.ADAPTED_ZERO_TO_MANY:
            # 'Fake' zero-to-one relation. Merge into existing list.
            updated_props = _merge_obj_effects(props, val)
        elif field_tuple.type == FieldTypes.ZERO_TO_MANY:
            # Actual zero-to-many relation. Just append.
            updated_props = props + [val]
        else:
            # Zero-to-one relation - LoRa does the merging for us,
            # so disregard existing props
            updated_props = [val]

        payload = set_object_value(payload, field_tuple.path, updated_props)

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
    new_from = get_effect_from(new)
    new_to = get_effect_to(new)

    for orig in sorted_orig:
        orig_from = get_effect_from(orig)
        orig_to = get_effect_to(orig)

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


def _create_virkning(valid_from: str, valid_to: str) -> dict:
    """
    Create virkning object

    :param valid_from: The "from" date.
    :param valid_to: The "to" date.
    :return: The virkning object.
    """
    return {
        'from': util.to_lora_time(valid_from),
        'to': util.to_lora_time(valid_to),
    }


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
                d.setdefault('virkning', virkning.copy())
    return lora_obj


def inactivate_org_funktion_payload(enddate, note):
    obj_path = ('tilstande', 'organisationfunktiongyldighed')
    val_inactive = {
        'gyldighed': 'Inaktiv',
        'virkning': _create_virkning(enddate, 'infinity')
    }

    payload = set_object_value({'note': note}, obj_path, [val_inactive])

    return payload


def create_organisationsfunktion_payload(
    funktionsnavn: str,
    valid_from: str,
    valid_to: str,
    brugervendtnoegle: str,
    tilknyttedebrugere: List[str],
    tilknyttedeorganisationer: List[str],
    tilknyttedeenheder: List[str] = None,
    funktionstype: str = None,
    opgaver: List[dict] = None,
    adresser: List[str] = None
) -> dict:
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
        org_funk['relationer']['opgaver'] = opgaver

    if adresser:
        org_funk['relationer']['adresser'] = adresser

    org_funk = _set_virkning(org_funk, virkning)

    return org_funk


def create_organisationsenhed_payload(
    enhedsnavn: str,
    valid_from: str,
    valid_to: str,
    brugervendtnoegle: str,
    tilhoerer: str,
    enhedstype: str,
    overordnet: str,
    adresser: List[dict] = None,
) -> dict:

    virkning = _create_virkning(valid_from, valid_to)

    org_unit = {
        'note': 'Oprettet i MO',
        'attributter': {
            'organisationenhedegenskaber': [
                {
                    'enhedsnavn': enhedsnavn,
                    'brugervendtnoegle': brugervendtnoegle
                },
            ],
        },
        'tilstande': {
            'organisationenhedgyldighed': [
                {
                    'gyldighed': 'Aktiv',
                },
            ],
        },
        'relationer': {
            'tilhoerer': [
                {
                    'uuid': tilhoerer
                }
            ],
            'enhedstype': [
                {
                    'uuid': enhedstype
                }
            ],
            'overordnet': [
                {
                    'uuid': overordnet
                }
            ],
        }
    }

    if adresser:
        org_unit['relationer']['adresser'] = adresser

    org_unit = _set_virkning(org_unit, virkning)

    return org_unit


def get_valid_from(obj, fallback=None) -> datetime.datetime:
    sentinel = object()
    validity = obj.get(keys.VALIDITY, sentinel)

    if validity and validity is not sentinel:
        valid_from = validity.get(keys.FROM, sentinel)
        if valid_from is None:
            return util.negative_infinity
        elif valid_from is not sentinel:
            return util.from_iso_time(valid_from)

    if fallback is not None:
        return get_valid_from(fallback)
    else:
        return util.negative_infinity


def get_valid_to(obj, fallback=None) -> datetime.datetime:
    sentinel = object()
    validity = obj.get(keys.VALIDITY, sentinel)
    if validity and validity is not sentinel:
        valid_to = validity.get(keys.TO, sentinel)
        if valid_to is None:
            return util.positive_infinity
        elif valid_to is not sentinel:
            return util.from_iso_time(valid_to)

    if fallback is not None:
        return get_valid_to(fallback)
    else:
        return util.positive_infinity


def get_validity_effect(entry, fallback=None):
    if keys.VALIDITY not in entry and fallback is None:
        return None

    return {
        keys.FROM: util.to_lora_time(get_valid_from(entry, fallback)),
        keys.TO: util.to_lora_time(get_valid_to(entry, fallback)),
    }


def replace_relation_value(relations: List[dict],
                           old_entry: dict,
                           new_entry: dict=None) -> List[dict]:
    old_from = get_effect_from(old_entry)
    old_to = get_effect_to(old_entry)

    old_urn = old_entry.get('urn')
    old_uuid = old_entry.get('uuid')
    old_type = old_entry.get('objekttype')

    for i, rel in enumerate(relations):
        if (
            get_effect_from(rel) == old_from and
            get_effect_to(rel) == old_to and
            rel.get('urn') == old_urn and
            rel.get('uuid') == old_uuid and
            rel.get('objekttype') == old_type
        ):
            new_rels = copy.deepcopy(relations)

            if new_entry:
                new_rels[i] = new_entry
            else:
                del new_rels[i]

            return new_rels

    else:
        raise ValueError('original entry not found!')


def is_reg_valid(reg):
    """
    Check if a given registration is valid
    i.e. that the registration contains a 'gyldighed' that is 'Aktiv'

    :param reg: A registration object
    """

    return any(
        gyldighed_obj.get('gyldighed') == 'Aktiv'
        for tilstand in reg.get('tilstande', {}).values()
        for gyldighed_obj in tilstand
    )


def add_bruger_history_entry(employee_uuid, note: str):
    """
    Add a history entry to a given employee.
    The idea is to write an update to the employee whenever an object
    associated to him is created or changed, as to easily be able to get an
    overview of the history of the modifications to both the employee
    but also the employee's associated objects.

    We have to make some sort of 'meaningful' change to data to be
    able to update the 'note' field - which for now amounts to just
    updating the virkning notetekst of gyldighed with a garbage value

    :param employee_uuid: The UUID of the employee
    :param note: A note to be associated with the entry
    """
    c = lora.Connector()
    employee_obj = c.bruger.get(employee_uuid)

    path = ('tilstande', 'brugergyldighed')
    gyldighed = get_obj_value(employee_obj, path)[-1]
    gyldighed['virkning']['notetekst'] = str(uuid.uuid4())

    payload = {
        'note': note
    }

    payload = set_object_value(payload, path, [gyldighed])
    c.bruger.update(payload, employee_uuid)


def convert_reg_to_history(reg):
    return {
        'user_ref': reg['brugerref'],
        'from': util.to_frontend_time(
            reg['fratidspunkt']['tidsstempeldatotid'],
        ),
        'to': util.to_frontend_time(
            reg['tiltidspunkt']['tidsstempeldatotid'],
        ),
        'life_cycle_code': reg['livscykluskode'],
        'action': reg.get('note')
    }
