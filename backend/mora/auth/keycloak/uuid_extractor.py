# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from typing import Set
from typing import List
import re

from more_itertools import one
from structlog import get_logger
from uuid import UUID

from fastapi import Request

from mora import common
# import mora.main
from mora.mapping import (
    ASSOCIATED_ORG_UNITS_FIELD,
    CHILDREN,
    DATA,
    EntityType,
    ORG_UNIT,
    PARENT,
    PERSON,
    TYPE,
    USER_FIELD
)

logger = get_logger()


def _get_terminate_entity_regex(entity: EntityType) -> re.Pattern:
    return re.compile(
        f'/service/{entity.value}/[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-'
        f'[0-9a-f]{{4}}-[0-9a-f]{{12}}/terminate'
    )


UUID_KEY = 'uuid'

# URL paths

# TODO: re-introduce feature where the paths below are fetched via
#  the main.app-url_path_for(...). The importing of mora.main
#  causes the instrumentation to fail why we are temporarily using
#  hard-coded constants instead -
#  see https://redmine.magenta-aps.dk/issues/45047

# CREATE_OU = mora.main.app.url_path_for('create_org_unit')
# TERMINATE_DETAIL = mora.main.app.url_path_for('terminate')
# TERMINATE_UNIT = _get_terminate_entity_regex('terminate_org_unit')
# TERMINATE_EMPLOYEE = _get_terminate_entity_regex('terminate_employee')

CREATE_OU = '/service/ou/create'
TERMINATE_DETAIL = '/service/details/terminate'
TERMINATE_UNIT = _get_terminate_entity_regex(EntityType.ORG_UNIT)
TERMINATE_EMPLOYEE = _get_terminate_entity_regex(EntityType.EMPLOYEE)


def get_ancestor_uuids(tree: List[dict]) -> Set[UUID]:
    """
    Recursively extract org unit UUIDs from org unit ancestor tree.

    :param tree: (sub)tree containing the descendants of an org unit
    :return: set of UUIDs of all the org units in the tree
    """

    # So far in the org unit RBAC case we have only experienced lists
    # containing exactly one element, but let's leave this assertion until
    # the entire RBAC code is done
    assert len(tree) == 1  # Fix

    node = tree[0]

    uuids = {UUID(node.get(UUID_KEY))}  # Do not assume non-empty list
    if CHILDREN in node:
        uuids = uuids.union(get_ancestor_uuids(node[CHILDREN]))
    return uuids

# The following functions (or coroutines) are strategies for extracting the
# org unit UUID(s) when an endpoint with the RBAC feature enabled is called.
# These UUIDs are required in order to determine the owner of the
# corresponding org units


async def get_org_unit_uuids(request: Request) -> Set[UUID]:
    # State like pattern - choose appropriate UUID extraction strategy based
    # on the URL path of the incoming request
    """
    Extract org unit UUIDs of the org units in the entire relevant branch of
    the org unit ancestor tree. For example, if UnitA is a parent of UnitB
    which is a parent of UnitC, then will return a list containing the UUIDs
    of UnitA, UnitB and UnitC.

    :param request: the incoming request to the endpoint
    :return: list of the org unit UUIDs
    """

    logger.debug('uuid_extract_strategy called')

    if request.url.path == CREATE_OU:
        return await create_ou_extract_strategy(request)
    if TERMINATE_UNIT.match(request.url.path):
        return path_extract_strategy(request)
    if TERMINATE_EMPLOYEE.match(request.url.path):
        return path_extract_strategy(request)
    if request.url.path == TERMINATE_DETAIL:
        return await terminate_detail_extract_strategy(request)
    return await json_extract_strategy(request)


async def create_ou_extract_strategy(request: Request) -> Set[UUID]:
    # Strategy pattern
    """
    Extract org unit UUID from the request payload when creating a new
    org unit.

    :param request: the incoming request to the endpoint
    :return: list containing the org unit UUID
    """

    logger.debug('create_ou_uuid_extract_strategy called')

    payload = await request.json()
    if PARENT not in payload:
        return set()
    uuid = payload[PARENT][UUID_KEY]
    logger.debug('Parent org unit UUID is ' + uuid)

    return {UUID(uuid)}


def path_extract_strategy(request: Request) -> Set[UUID]:
    # Strategy pattern
    """
    Extract org unit UUID from the request path.

    :param request: the incoming request to the endpoint
    :return: list containing the org unit UUID
    """

    logger.debug('path_extract_strategy called')

    return {UUID(request.path_params.get(UUID_KEY))}


async def terminate_detail_extract_strategy(request: Request) -> Set[UUID]:
    # Strategy pattern
    """
    Extract org unit UUID from the request payload when terminating an
    org unit detail.

    :param request: the incoming request to the endpoint
    :return: list containing the org unit UUID
    """

    logger.debug('terminate_detail_uuid_extract_strategy called')

    payload = await request.json()

    # Example payload
    # {
    #     "type": "address",
    #     "uuid": "8086178e-f2e2-418a-a46c-de6f3699d747",
    #     "validity": {
    #         "to": "2021-07-01"
    #     }
    # }

    if payload[TYPE] == ORG_UNIT:
        return {UUID(payload[UUID_KEY])}

    org_function = await _get_org_function(payload)
    org_unit_uuid = ASSOCIATED_ORG_UNITS_FIELD.get_uuid(org_function)
    if org_unit_uuid:
        return {UUID(org_unit_uuid)}
    employee_uuid = USER_FIELD.get_uuid(org_function)

    return {UUID(employee_uuid)}


async def json_extract_strategy(request: Request) -> Set[UUID]:
    # Strategy pattern
    """
    Extract org unit UUID from the request payload when creating, editing,
    renaming or moving an org unit. In the case where we are moving an org
    unit, the list returned will contain exactly two elements (the source and
    target unit) and in all other cases the list will only contain the source
    unit UUID.

    :param request: the incoming request to the endpoint
    :return: list of the org unit UUID(s)
    """

    logger.debug('json_uuid_extract_strategy called')

    payload = await _get_payload(request)

    # Creating or editing org unit detail (address, IT-system,...)
    if payload[TYPE] != ORG_UNIT:
        if ORG_UNIT in payload:
            return {UUID(payload[ORG_UNIT][UUID_KEY])}
        return {UUID(payload[PERSON][UUID_KEY])}

    # Renaming, moving or editing the details of the unit itself (i.e.
    # not address details and similar)
    data = payload[DATA]
    if PARENT in data and ORG_UNIT not in payload:
        # Moving a unit
        return {UUID(data[UUID_KEY]), UUID(data[PARENT][UUID_KEY])}

    # Renaming or editing details on the unit itself
    return {UUID(payload[DATA][UUID_KEY])}


async def get_entity_type(request: Request) -> EntityType:
    payload = await _get_payload(request)
    if request.url.path == CREATE_OU or TERMINATE_UNIT.match(request.url.path):
        entity_type = EntityType.ORG_UNIT
    elif request.url.path == TERMINATE_DETAIL:
        if payload[TYPE] == ORG_UNIT:
            entity_type = EntityType.ORG_UNIT
        else:
            org_function = await _get_org_function(payload)
            org_unit_uuid = ASSOCIATED_ORG_UNITS_FIELD.get_uuid(org_function)
            entity_type = EntityType.ORG_UNIT if org_unit_uuid else EntityType.EMPLOYEE
    elif ORG_UNIT in payload or payload.get(TYPE) == ORG_UNIT:
        entity_type = EntityType.ORG_UNIT
    else:
        entity_type = EntityType.EMPLOYEE

    logger.debug('get_entity_type returns ', entity_type=entity_type)
    return entity_type


async def _get_payload(request: Request) -> dict:
    payload = await request.json()

    # payload is a list when the frontend calls /service/details/create
    # and a dict when /service/details/edit is called

    if isinstance(payload, list):
        # So far in the org unit RBAC case we have only experienced lists
        # containing exactly one element, but let's leave this assertion until
        # the entire RBAC code is done
        payload = one(payload)

    assert isinstance(payload, dict)

    return payload


async def _get_org_function(payload: dict) -> dict:
    c = common.get_connector()
    return await c.organisationfunktion.get(uuid=payload[UUID_KEY])

# TODO: so far there are only integration tests covering this module -
#  unit tests are still missing - and since this code probably will be
#  removed later we should not spend too much effort on this
