#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import collections
import datetime
import typing

from . import exceptions
from . import lora
from . import util

from .service import common
from .service import keys
from .service import mapping


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
        'valid_from': util.to_iso_time(
            min(
                (
                    common.get_effect_from(state)
                    for state in common.get_states(reg)
                    if state.get('gyldighed') == 'Aktiv'
                ),
                default=util.NEGATIVE_INFINITY,
            ),
        ),
        'valid_to': util.to_iso_time(
            max(
                (
                    common.get_effect_to(state)
                    for state in common.get_states(reg)
                    if state.get('gyldighed') == 'Aktiv'
                ),
                default=util.POSITIVE_INFINITY,
            ),
        ),
    }


def is_date_range_in_org_unit_range(org_unit_uuid, valid_from, valid_to):
    scope = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    ).organisationenhed
    org_unit = scope.get(org_unit_uuid)

    gyldighed_key = "organisationenhedgyldighed"

    if not _is_date_range_valid(org_unit, valid_from, valid_to, scope,
                                gyldighed_key):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE,
            org_unit_uuid=org_unit_uuid,
            **_get_active_validity(org_unit),
        )


def is_distinct_responsibility(
    fields: typing.List[typing.Tuple[common.FieldTuple, typing.Mapping]],
):
    uuid_counts = collections.Counter(
        value['uuid']
        for field, value in fields
        if field == mapping.RESPONSIBILITY_FIELD
    )
    duplicates = sorted(v for v, c in uuid_counts.items() if c > 1)

    if duplicates:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_DUPLICATED_RESPONSIBILITY,
            duplicates=duplicates
        )


def is_date_range_in_employee_range(employee_uuid, valid_from, valid_to):
    scope = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    ).bruger
    employee = scope.get(employee_uuid)

    gyldighed_key = "brugergyldighed"

    if not _is_date_range_valid(employee, valid_from, valid_to, scope,
                                gyldighed_key):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_DATE_OUTSIDE_EMPL_RANGE,
            employee_uuid=employee_uuid,
            **_get_active_validity(employee),
        )


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
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_CANNOT_MOVE_ROOT_ORG_UNIT)

    # Use for checking that the candidate parent is not the units own subtree
    seen = {unitid}

    c = lora.Connector(effective_date=from_date)

    while True:
        # this captures moving to a child as well as moving into a loop
        if parent in seen:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.V_ORG_UNIT_MOVE_TO_CHILD,
                org_unit_uuid=parent,
            )

        seen.add(parent)

        parentobj = c.organisationenhed.get(uuid=parent)

        if not parentobj:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND,
                org_unit_uuid=parent,
            )

        # ensure the parent is active
        if not common.is_reg_valid(parentobj):
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE,
                org_unit_uuid=parent,
            )

        parentorg = parentobj['relationer']['tilhoerer'][0]['uuid']

        # ensure it's in the same organisation
        if parentorg != orgid:
            raise exceptions.HTTPException(
                exceptions.ErrorCodes.V_UNIT_OUTSIDE_ORG,
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


def is_org_unit_termination_date_valid(unitid: str, end_date: datetime):
    """
    Check if the inactivation date is valid.

    :param unitid: The UUID of the org unit.
    :param end_date: The candidate end-date.
    :return: True if the inactivation date is valid and false otherwise.
    """
    c = lora.Connector(virkningfra=end_date, virkningtil='infinity')

    if not c.organisationenhed.get(unitid):
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND)

    # Find a org unit effect that's active, and that has a start date before
    #  our termination date
    effects = [
        (start, end, effect)
        for start, end, effect in
        c.organisationenhed.get_effects(
            unitid,
            {
                'tilstande': (
                    'organisationenhedgyldighed',
                ),
            },
            {}
        )
        if effect['tilstande']
                 ['organisationenhedgyldighed'][0]
                 ['gyldighed'] == 'Aktiv' and
        start < end_date
    ]

    if not effects:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_TERMINATE_UNIT_BEFORE_START_DATE,
        )


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
                               funktionsnavn=keys.ASSOCIATION_KEY)
    if r:
        existing = r[-1]
        if association_uuid and existing == association_uuid:
            return

        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_MORE_THAN_ONE_ASSOCIATION,
            existing=existing
        )


def does_employee_have_active_engagement(employee_uuid, valid_from, valid_to):
    c = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to)
    )
    r = c.organisationfunktion(tilknyttedebrugere=employee_uuid,
                               funktionsnavn=keys.ENGAGEMENT_KEY)

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
        if effect['tilstande']
                 ['organisationfunktiongyldighed'][0]
                 ['gyldighed'] == 'Aktiv' and
        start <= valid_from and
        valid_to <= end
    ]

    if not valid_effects:
        raise exceptions.HTTPException(
            exceptions.ErrorCodes.V_NO_ACTIVE_ENGAGEMENT,
            employee=employee_uuid
        )
