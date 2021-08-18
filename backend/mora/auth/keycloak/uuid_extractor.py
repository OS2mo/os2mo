# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import re
from structlog import get_logger
from typing import Set
from typing import List
from uuid import UUID

from fastapi import Request

from mora import common
# import mora.main
from mora.mapping import (
    ASSOCIATED_ORG_UNITS_FIELD,
    CHILDREN,
    DATA,
    ORG_UNIT,
    PARENT,
    TYPE,
)

logger = get_logger()

UUID_KEY = 'uuid'

# URL paths

# TODO: re-introduce feature where the paths below are fetched via
#  the main.app-url_path_for(...). The importing of mora.main
#  causes the instrumentation to fail why we are temporarily using
#  hard-coded constants instead -
#  see https://redmine.magenta-aps.dk/issues/45047

# CREATE_OU = mora.main.app.url_path_for('create_org_unit')
# TERMINATE_DETAIL = mora.main.app.url_path_for('terminate')
# TERMINATE_UNIT = re.compile(
#     mora.main.app.url_path_for(
#         'terminate_org_unit',
#         uuid='[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
#     )
# )

CREATE_OU = '/service/ou/create'
TERMINATE_DETAIL = '/service/details/terminate'
TERMINATE_UNIT = re.compile(
    '/service/ou/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    '/terminate'
)


def get_ancestor_uuids(tree: List[dict]) -> Set[UUID]:
    """
    Recursively extract org unit UUIDs from org unit ancestor tree.

    :param tree: (sub)tree containing the descendants of an org unit
    :param uuids: set of UUIDs to append the UUIDs of the descendants to
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

    c = common.get_connector()
    r = await c.organisationfunktion.get(uuid=payload[UUID_KEY])
    org_unit_uuid = ASSOCIATED_ORG_UNITS_FIELD.get_uuid(r)

    return {UUID(org_unit_uuid)}


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

    # payload is a list when the frontend calls /service/details/create
    # and a dict when /service/details/edit is called
    payload = await request.json()

    if isinstance(payload, list):
        # So far in the org unit RBAC case we have only experienced lists
        # containing exactly one element, but let's leave this assertion until
        # the entire RBAC code is done
        assert len(payload) == 1

        payload = payload[0]

    # Creating or editing org unit detail (address, IT-system,...)
    if payload[TYPE] != ORG_UNIT:
        return {UUID(payload[ORG_UNIT][UUID_KEY])}

    # Renaming, moving or editing the details of the unit itself (i.e.
    # not address details and similar)
    data = payload[DATA]
    if PARENT in data and ORG_UNIT not in payload:
        # Moving a unit
        return {UUID(data[UUID_KEY]), UUID(data[PARENT][UUID_KEY])}

    # Renaming or editing details on the unit itself
    return {UUID(payload[DATA][UUID_KEY])}

# TODO: so far there are only integration tests covering this module -
#  unit tests are still missing
