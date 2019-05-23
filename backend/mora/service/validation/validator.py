#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections

import datetime
import functools
import typing

from ... import exceptions
from ... import lora
from ... import mapping
from ... import util


def forceable(fn):
    '''Decorator that allows optionally bypassing validation, using the
    ``force`` query argument.

    '''
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not util.get_args_flag('force'):
            return fn(*args, **kwargs)

    return wrapper


def _is_date_range_valid(parent: typing.Union[dict, str],
                         startdate: datetime.datetime,
                         enddate: datetime.datetime, lora_scope,
                         gyldighed_key: str) -> bool:
    """
    Determine if the given dates are within validity of the parent unit.

    :param parent: Ether the UUID of the parent unit, or a dict containing it.
    :param startdate: The candidate start date.
    :param enddate: The candidate end date.
    :param lora_scope: A scope object from a LoRa connector.
    :param gyldighed_key: The key of where to find the 'gyldighed' in the
        object in question
    :return: True if the date range is valid and false otherwise.
    """

    if startdate >= enddate:
        return False

    previous_end = None

    for start, end, effect in lora_scope.get_effects(
        parent,
        {
            'tilstande': (
                gyldighed_key,
            )
        }
    ):
        if previous_end is None:
            # initial case
            if startdate < start:
                # start is too late!
                return False
        elif start != previous_end:
            # non-consecutive chunk - so not valid for that time
            return False
        elif start >= enddate or end < startdate:
            previous_end = end
            continue

        vs = effect['tilstande'][gyldighed_key]

        if not vs or any(v['gyldighed'] != 'Aktiv' for v in vs):
            # not valid for the given time
            return False

        previous_end = end

    # verify that we've achieved full coverage - and return a bool
    return previous_end is not None and previous_end >= enddate


def _get_active_validity(reg: dict) -> typing.Mapping[str, str]:
    '''Approximate the bounds where this registration is active.

    Please note that this method doesn't check for intermediate chunks
    where the registration might be inactive, as that shouldn't happen in
    practice.

    '''

    return {
        'valid_from': util.to_iso_date(
            min(
                (
                    util.get_effect_from(state)
                    for state in util.get_states(reg)
                    if state.get('gyldighed') == 'Aktiv'
                ),
                default=util.NEGATIVE_INFINITY,
            ),
        ),
        'valid_to': util.to_iso_date(
            max(
                (
                    util.get_effect_to(state)
                    for state in util.get_states(reg)
                    if state.get('gyldighed') == 'Aktiv'
                ),
                default=util.POSITIVE_INFINITY,
            ),
            is_end=True,
        ),
    }


@forceable
def is_date_range_in_org_unit_range(org_unit_obj, valid_from, valid_to):
    # query for the full range of effects; otherwise,
    # _get_active_validity() won't return any useful data for time
    # intervals predating the creation of the unit
    scope = lora.Connector(
        virkningfra=util.to_lora_time(util.NEGATIVE_INFINITY),
        virkningtil=util.to_lora_time(util.POSITIVE_INFINITY)
    ).organisationenhed

    if org_unit_obj.get('allow_nonexistent'):
        org_unit_valid_from = org_unit_obj.get(mapping.VALID_FROM)
        org_unit_valid_to = org_unit_obj.get(mapping.VALID_TO)
        is_contained_in_range(
            org_unit_valid_from, org_unit_valid_to,
            valid_from, valid_to,
            exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE)
    else:
        org_unit_uuid = org_unit_obj.get(mapping.UUID)
        org_unit = scope.get(org_unit_uuid)
        if not org_unit:
            exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(
                org_unit_uuid=org_unit_uuid)

        gyldighed_key = "organisationenhedgyldighed"

        if not _is_date_range_valid(org_unit, valid_from, valid_to, scope,
                                    gyldighed_key):
            exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE(
                org_unit_uuid=org_unit_uuid,
                wanted_valid_from=util.to_iso_date(valid_from),
                wanted_valid_to=util.to_iso_date(valid_to, is_end=True),
                **_get_active_validity(org_unit),
            )


@forceable
def is_distinct_responsibility(
    fields: typing.List[typing.Tuple[mapping.FieldTuple, typing.Mapping]],
):
    uuid_counts = collections.Counter(
        value['uuid']
        for field, value in fields
        if field == mapping.RESPONSIBILITY_FIELD
    )
    duplicates = sorted(v for v, c in uuid_counts.items() if c > 1)

    if duplicates:
        exceptions.ErrorCodes.V_DUPLICATED_RESPONSIBILITY(
            duplicates=duplicates,
        )


@forceable
def is_date_range_in_employee_range(employee_obj: dict,
                                    valid_from: datetime.datetime,
                                    valid_to: datetime.datetime):
    scope = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    ).bruger
    # If this is a not-yet created user, emulate check
    if employee_obj.get('allow_nonexistent'):
        employee_valid_from = employee_obj.get(mapping.VALID_FROM)
        employee_valid_to = employee_obj.get(mapping.VALID_TO)
        is_contained_in_range(employee_valid_from, employee_valid_to,
                              valid_from, valid_to,
                              exceptions.ErrorCodes.V_DATE_OUTSIDE_EMPL_RANGE)
    else:
        employee_uuid = employee_obj.get(mapping.UUID)
        employee = scope.get(employee_uuid)

        if not employee:
            exceptions.ErrorCodes.E_USER_NOT_FOUND(employee_uuid=employee_uuid)

        gyldighed_key = "brugergyldighed"

        if not _is_date_range_valid(employee, valid_from, valid_to, scope,
                                    gyldighed_key):
            exceptions.ErrorCodes.V_DATE_OUTSIDE_EMPL_RANGE(
                employee_uuid=employee_uuid,
                **_get_active_validity(employee),
            )


@forceable
def is_contained_in_range(candidate_from, candidate_to, valid_from, valid_to,
                          exception):
    if valid_from < candidate_from or candidate_to < valid_to:
        exception(
            valid_from=util.to_iso_date(candidate_from),
            valid_to=util.to_iso_date(candidate_to),
            wanted_valid_from=util.to_iso_date(valid_from),
            wanted_valid_to=util.to_iso_date(valid_to)
        )


@forceable
def is_candidate_parent_valid(unitid: str, parent: str,
                              from_date: datetime.datetime) -> bool:
    """
    For moving an org unit. Check if the candidate parent is in the subtree of
    the org unit itself. Note: it is (and should be) allowed to move an org
    unit to its own parent - since it can be moved back and forth on different
    dates.

    :param unitid: The UUID of the org unit we are trying to move.
    :param parent: The UUID of the new candidate parent org unit.
    :param from_date: The date on which the move takes place
    """
    # Do not allow moving of the root org unit
    c = lora.Connector(virkningfra='-infinity', virkningtil='infinity')

    org_unit_relations = c.organisationenhed.get(
        uuid=unitid
    )['relationer']
    orgid = org_unit_relations['tilhoerer'][0]['uuid']

    if org_unit_relations['overordnet'][0]['uuid'] == orgid:
        exceptions.ErrorCodes.V_CANNOT_MOVE_ROOT_ORG_UNIT()

    if parent == orgid:
        exceptions.ErrorCodes.V_CANNOT_MOVE_UNIT_TO_ROOT_LEVEL()

    # Use for checking that the candidate parent is not the units own subtree
    seen = {unitid}

    c = lora.Connector(effective_date=from_date)

    while True:
        # this captures moving to a child as well as moving into a loop
        if parent in seen:
            exceptions.ErrorCodes.V_ORG_UNIT_MOVE_TO_CHILD(
                org_unit_uuid=parent,
            )

        seen.add(parent)

        parentobj = c.organisationenhed.get(uuid=parent)

        if not parentobj:
            exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(
                org_unit_uuid=parent,
            )

        # ensure the parent is active
        if not util.is_reg_valid(parentobj):
            exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE(
                org_unit_uuid=parent,
            )

        parentorg = parentobj['relationer']['tilhoerer'][0]['uuid']

        # ensure it's in the same organisation
        if parentorg != orgid:
            exceptions.ErrorCodes.V_UNIT_OUTSIDE_ORG(
                org_unit_uuid=parent,
                current_org_uuid=orgid,
                target_org_uuid=parentorg,
            )

        # now switch to the next parent
        parent = parentobj['relationer']['overordnet'][0]['uuid']

        # after iterating at least once, have we hit a proper root node?
        # if so, we're done!
        if parent == orgid:
            break


@forceable
def does_employee_have_existing_association(employee_uuid, org_unit_uuid,
                                            valid_from, association_uuid=None):
    """
    Check if an employee already has an active association for a given org
    unit on a given date

    :param employee_uuid: UUID of the employee
    :param org_unit_uuid: UUID of the org unit
    :param valid_from: The date to check
    :param association_uuid: An optional uuid of an organisation
        being edited to be exempt from validation.
    :return:
    """
    c = lora.Connector(effective_date=valid_from)

    r = c.organisationfunktion(tilknyttedeenheder=org_unit_uuid,
                               tilknyttedebrugere=employee_uuid,
                               gyldighed='Aktiv',
                               funktionsnavn=mapping.ASSOCIATION_KEY)

    if association_uuid is not None and association_uuid in r:
        return

    if r:
        exceptions.ErrorCodes.V_MORE_THAN_ONE_ASSOCIATION(existing=r)


@forceable
def does_employee_have_active_engagement(employee_uuid, valid_from, valid_to):
    c = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    )
    r = c.organisationfunktion(tilknyttedebrugere=employee_uuid,
                               gyldighed='Aktiv',
                               funktionsnavn=mapping.ENGAGEMENT_KEY)

    valid_effects = [
        (start, end, effect)
        for funkid in r
        for start, end, effect in
        c.organisationfunktion.get_effects(
            funkid,
            {
                'tilstande': (
                    'organisationfunktiongyldighed',
                ),
            },
            {}
        )
        if util.is_reg_valid(effect) and
        start <= valid_from and
        valid_to <= end
    ]

    if not valid_effects:
        exceptions.ErrorCodes.V_NO_ACTIVE_ENGAGEMENT(employee=employee_uuid)


@forceable
def does_employee_have_existing_primary_function(function_key,
                                                 new_from, new_to,
                                                 employee_uuid,
                                                 allowed=None):
    c = lora.Connector(
        virkningfra=util.to_lora_time(new_from),
        virkningtil=util.to_lora_time(new_to)
    )

    preëxisting = c.organisationfunktion(
        funktionsnavn=function_key,
        gyldighed='Aktiv',
        primær='true',
        tilknyttedebrugere=employee_uuid,
    )

    if allowed is not None and allowed in preëxisting:
        preëxisting.remove(allowed)

    if preëxisting:
        exceptions.ErrorCodes.V_MORE_THAN_ONE_PRIMARY(
            preexisting=sorted(preëxisting),
        )


@forceable
def is_edit_from_date_before_today(from_date: datetime.datetime):
    """Check if a given edit date is before today. If so, raise exception"""
    today = datetime.datetime.combine(
        datetime.date.today(),
        datetime.time(0, 0, 0, 0, from_date.tzinfo)
    )
    if from_date < today:
        raise exceptions.ErrorCodes.V_CHANGING_THE_PAST(
            date=util.to_iso_time(from_date)
        )


@forceable
def does_employee_with_cpr_already_exist(cpr, valid_from, valid_to, org_uuid,
                                         allowed_user_id=None):
    """
    Check whether we're able to find an existing user with the given CPR,
    and raise a validation error accordingly
    """
    c = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    )

    user_ids = c.bruger.fetch(
        tilknyttedepersoner="urn:dk:cpr:person:{}".format(cpr),
        tilhoerer=org_uuid
    )

    if user_ids and allowed_user_id not in user_ids:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_EXISTING_CPR,
            cpr=cpr,
        )
