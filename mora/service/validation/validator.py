# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import collections
import datetime
import functools
import typing
from asyncio import create_task
from asyncio import gather
from uuid import UUID

from more_itertools import pairwise

from ... import exceptions
from ... import lora
from ... import mapping
from ... import util
from ...lora import LoraObjectType


def forceable(fn):
    """
    Decorator that allows optionally bypassing validation, using the
    ``force`` query argument.

    """

    if asyncio.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            if not util.get_args_flag("force"):
                return await fn(*args, **kwargs)

    else:

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not util.get_args_flag("force"):
                return fn(*args, **kwargs)

    return wrapper


async def _is_date_range_valid(
    obj: dict | str,
    valid_from: datetime.datetime,
    valid_to: datetime.datetime,
    lora_scope: lora.Scope,
    gyldighed_key: str,
) -> bool:
    """
    Determine if the given dates are within validity of the parent unit.

    :param obj: Ether the UUID of an object found in the attached scope,
        or a dict containing it.
    :param valid_from: The candidate start date.
    :param valid_to: The candidate end date.
    :param lora_scope: A scope object from a LoRa connector.
    :param gyldighed_key: The key of where to find the 'gyldighed' in the
        object in question
    :return: True if the date range is valid and false otherwise.
    """

    if valid_from >= valid_to:
        return False

    effects = await lora_scope.get_effects(obj, {"tilstande": (gyldighed_key,)})

    def get_valid_effects(effects):
        def overlap_filter_fn(effect):
            start, end, _ = effect
            return not (end < valid_from or valid_to < start)

        def validity_filter_fn(effect):
            _, _, effect_obj = effect
            vs = effect_obj["tilstande"][gyldighed_key]
            return vs and all(v["gyldighed"] == "Aktiv" for v in vs)

        def get_start(effect):
            start, _, _ = effect
            return start

        # Find valid effects that overlap the validity period in question
        overlapping = filter(overlap_filter_fn, effects)
        valid_effects = filter(validity_filter_fn, overlapping)
        sorted_effects = sorted(valid_effects, key=get_start)
        return list(sorted_effects)

    valid_effects = get_valid_effects(effects)

    if not valid_effects:
        return False

    # Check that the valid effects actually cover the entire validity
    if not (valid_effects[0][0] <= valid_from and valid_to <= valid_effects[-1][1]):
        return False

    # Check that the valid effects form a continuous block
    if len(valid_effects) == 1:
        return True

    effect_pairs = pairwise(valid_effects)

    def check_pair(pair):
        (_, end_left, _), (start_right, _, _) = pair
        return end_left == start_right

    return all(map(check_pair, effect_pairs))


def _get_active_validity(reg: dict) -> typing.Mapping[str, str]:
    """Approximate the bounds where this registration is active.

    Please note that this method doesn't check for intermediate chunks
    where the registration might be inactive, as that shouldn't happen in
    practice.

    """

    return {
        "valid_from": util.to_iso_date(
            min(
                (
                    util.get_effect_from(state)
                    for state in util.get_states(reg)
                    if state.get("gyldighed") == "Aktiv"
                ),
                default=util.NEGATIVE_INFINITY,
            ),
        ),
        "valid_to": util.to_iso_date(
            max(
                (
                    util.get_effect_to(state)
                    for state in util.get_states(reg)
                    if state.get("gyldighed") == "Aktiv"
                ),
                default=util.POSITIVE_INFINITY,
            ),
            is_end=True,
        ),
    }


@forceable
async def is_date_range_in_org_unit_range(org_unit_obj, valid_from, valid_to):
    # query for the full range of effects; otherwise,
    # _get_active_validity() won't return any useful data for time
    # intervals predating the creation of the unit
    scope = lora.Connector(
        virkningfra=util.to_lora_time(util.NEGATIVE_INFINITY),
        virkningtil=util.to_lora_time(util.POSITIVE_INFINITY),
    ).organisationenhed

    if org_unit_obj.get("allow_nonexistent"):
        org_unit_valid_from = org_unit_obj.get(mapping.VALID_FROM)
        org_unit_valid_to = org_unit_obj.get(mapping.VALID_TO)
        is_contained_in_range(
            org_unit_valid_from,
            org_unit_valid_to,
            valid_from,
            valid_to,
            exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE,
        )
    else:
        org_unit_uuid = org_unit_obj.get(mapping.UUID)
        org_unit = await scope.get(org_unit_uuid)
        if not org_unit:
            exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=org_unit_uuid)

        gyldighed_key = "organisationenhedgyldighed"

        if not await _is_date_range_valid(
            org_unit, valid_from, valid_to, scope, gyldighed_key
        ):
            exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE(
                org_unit_uuid=org_unit_uuid,
                **_get_active_validity(org_unit),
            )


@forceable
def is_distinct_responsibility(
    fields: list[tuple[mapping.FieldTuple, typing.Mapping]],
):
    uuid_counts = collections.Counter(
        value["uuid"]
        for field, value in fields
        if field == mapping.RESPONSIBILITY_FIELD
    )
    duplicates = sorted(v for v, c in uuid_counts.items() if c > 1)

    if duplicates:
        exceptions.ErrorCodes.V_DUPLICATED_RESPONSIBILITY(
            duplicates=duplicates,
        )


@forceable
async def is_date_range_in_employee_range(
    employee_obj: dict,
    valid_from: datetime.datetime,
    valid_to: datetime.datetime,
):
    return await is_date_range_in_obj_range(
        obj=employee_obj,
        valid_from=valid_from,
        valid_to=valid_to,
        obj_type=LoraObjectType.user,
        gyldighed_key="brugergyldighed",
    )


@forceable
async def is_date_range_in_engagement_range(
    obj: dict, valid_from: datetime.datetime, valid_to: datetime.datetime
):  # pragma: no cover
    return await is_date_range_in_obj_range(
        obj=obj,
        valid_from=valid_from,
        valid_to=valid_to,
        obj_type=LoraObjectType.org_func,
        gyldighed_key="organisationfunktiongyldighed",
    )


@forceable
async def is_date_range_in_obj_range(
    obj: dict,
    valid_from: datetime.datetime,
    valid_to: datetime.datetime,
    obj_type: LoraObjectType,
    gyldighed_key: str,
):
    scope = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to),
    ).scope(obj_type)
    # If this is a not-yet created user, emulate check
    if obj.get("allow_nonexistent"):
        obj_valid_from = obj.get(mapping.VALID_FROM)
        obj_valid_to = obj.get(mapping.VALID_TO)
        is_contained_in_range(
            obj_valid_from,
            obj_valid_to,
            valid_from,
            valid_to,
            exceptions.ErrorCodes.V_DATE_OUTSIDE_EMPL_RANGE,
        )
    else:
        uuid = obj.get(mapping.UUID)
        existing_obj = await scope.get(uuid)

        if not existing_obj:
            # special case for backwards compatibility
            if obj_type is LoraObjectType.user:
                exceptions.ErrorCodes.E_USER_NOT_FOUND(employee_uuid=uuid)
            # coverage: pause
            exceptions.ErrorCodes.E_NOT_FOUND(scope=str(obj_type), uuid=uuid)
            # coverage: unpause

        if not await _is_date_range_valid(
            existing_obj, valid_from, valid_to, scope, gyldighed_key
        ):
            exceptions.ErrorCodes.V_DATE_OUTSIDE_EMPL_RANGE(
                uuid=uuid,
                **_get_active_validity(obj),
            )


@forceable
def is_contained_in_range(
    candidate_from, candidate_to, valid_from, valid_to, exception
):
    if valid_from < candidate_from or candidate_to < valid_to:
        exception(
            valid_from=util.to_iso_date(candidate_from),
            valid_to=util.to_iso_date(candidate_to),
        )


@forceable
async def is_candidate_parent_valid(
    unitid: str, parent: str, from_date: datetime.datetime
) -> None:
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
    c = lora.Connector(virkningfra="-infinity", virkningtil="infinity")

    org_unit_relations = (await c.organisationenhed.get(uuid=unitid))["relationer"]
    orgid = org_unit_relations["tilhoerer"][0]["uuid"]

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

        if parent == orgid:
            break
        parentobj = await c.organisationenhed.get(uuid=parent)

        if not parentobj:  # pragma: no cover
            exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(
                org_unit_uuid=parent,
            )

        # ensure the parent is active
        if not util.is_reg_valid(parentobj):
            exceptions.ErrorCodes.V_DATE_OUTSIDE_ORG_UNIT_RANGE(
                org_unit_uuid=parent,
            )

        parentorg = parentobj["relationer"]["tilhoerer"][0]["uuid"]

        # ensure it's in the same organisation
        if parentorg != orgid:
            exceptions.ErrorCodes.V_UNIT_OUTSIDE_ORG(
                org_unit_uuid=parent,
                current_org_uuid=orgid,
                target_org_uuid=parentorg,
            )

        # now switch to the next parent
        parent = parentobj["relationer"]["overordnet"][0]["uuid"]

        # after iterating at least once, have we hit a proper root node?
        # if so, we're done!
        if parent == orgid:
            break


@forceable
async def does_employee_have_existing_association(
    employee_uuid, org_unit_uuid, valid_from, association_uuid=None
):  # pragma: no cover
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
    return await does_uuid_have_existing_association(
        uuid=employee_uuid,
        uuid_search_key="tilknyttedebrugere",
        org_unit_uuid=org_unit_uuid,
        valid_from=valid_from,
        association_function_key=mapping.ASSOCIATION_KEY,
        association_uuid=association_uuid,
    )


@forceable
async def does_uuid_have_existing_association(
    uuid: str,
    uuid_search_key: str,
    org_unit_uuid: str,
    valid_from: str,
    association_function_key: str,
    association_uuid=None,
):  # pragma: no cover
    """
    Check if an employee already has an active association for a given org
    unit on a given date

    :param uuid: UUID of the obj
    :param uuid_search_key: "lora-column" in which to look for the uuid
    :param org_unit_uuid: UUID of the org unit
    :param valid_from: The date to check
    :param association_function_key: The key denoting the association type
    :param association_uuid: An optional uuid of an organisation
        being edited to be exempt from validation.
    :return:
    """
    c = lora.Connector(effective_date=valid_from)

    r = await c.organisationfunktion.load_uuids(
        tilknyttedeenheder=org_unit_uuid,
        gyldighed="Aktiv",
        funktionsnavn=association_function_key,
        **{uuid_search_key: uuid},
    )

    if association_uuid is not None and association_uuid in r:
        return

    if r:
        exceptions.ErrorCodes.V_MORE_THAN_ONE_ASSOCIATION(existing=r)


@forceable
def is_substitute_allowed(association_type_uuid: UUID):
    """
    checks whether the chosen association needs a substitute
    """
    if not util.is_substitute_allowed(association_type_uuid):
        exceptions.ErrorCodes.E_INVALID_TYPE(
            f'Substitute not allowed for association type "{association_type_uuid}"'
        )


@forceable
def is_substitute_self(employee_uuid: str, substitute_uuid: str):
    """
    Check if substitute is the same as employee

    :param employee_uuid: UUID of the employee
    :param substitute_uuid: UUID of the substitute
    :return:
    """
    if employee_uuid == substitute_uuid:
        exceptions.ErrorCodes.V_CANNOT_SUBSTITUTE_SELF(employee=employee_uuid)


@forceable
async def does_employee_have_active_engagement(employee_uuid, valid_from, valid_to):
    c = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to),
    )
    r = await c.organisationfunktion.load_uuids(
        tilknyttedebrugere=employee_uuid,
        gyldighed="Aktiv",
        funktionsnavn=mapping.ENGAGEMENT_KEY,
    )
    effect_tuples_list = await gather(
        *[
            create_task(
                c.organisationfunktion.get_effects(
                    funkid, {"tilstande": ("organisationfunktiongyldighed",)}, {}
                )
            )
            for funkid in r
        ]
    )

    valid_effects = [
        (start, end, effect)
        for effect_tuples in effect_tuples_list
        for start, end, effect in effect_tuples
        if util.is_reg_valid(effect) and start <= valid_from and valid_to <= end
    ]

    if not valid_effects:
        exceptions.ErrorCodes.V_NO_ACTIVE_ENGAGEMENT(employee=employee_uuid)


@forceable
async def does_employee_with_cpr_already_exist(
    cpr, valid_from, valid_to, org_uuid, allowed_user_id=None
) -> bool:
    """Check whether there exists an employee with the given CPR."""
    if not util.is_cpr_number(cpr):  # pragma: no cover
        return False

    c = lora.Connector(
        virkningfra=util.to_lora_time(valid_from),
        virkningtil=util.to_lora_time(valid_to),
    )

    user_ids = await c.bruger.load_uuids(
        tilknyttedepersoner=f"urn:dk:cpr:person:{cpr}", tilhoerer=org_uuid
    )

    return bool(user_ids) and allowed_user_id not in user_ids


@forceable
async def is_mutually_exclusive(*values):
    """Raise validation error if more than one of `values` is not None."""
    if len([val for val in values if val is not None]) > 1:  # pragma: no cover
        exceptions.ErrorCodes.E_INVALID_INPUT(values)
