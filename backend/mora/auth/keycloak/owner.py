# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import List
from typing import Set
from uuid import UUID

from more_itertools import flatten
from structlog import get_logger

import mora.service.orgunit
from mora import common
from mora.auth.keycloak import uuid_extractor
from mora.handler.impl.owner import OwnerReader
from mora.mapping import EntityType
from mora.mapping import OWNER
from mora.mapping import UUID as UUID_KEY

logger = get_logger()


async def get_owners(uuid: UUID, entity_type: EntityType) -> Set[UUID]:
    logger.debug("get_owners called")
    if entity_type == EntityType.ORG_UNIT:
        return await get_ancestor_owners(uuid)
    return await _get_entity_owners(uuid, EntityType.EMPLOYEE)


async def get_ancestor_owners(uuid: UUID) -> Set[UUID]:
    """
    Get the owners of an org unit and all of its ancestors. For example, if
    UnitA (with owner A) is a parent of UnitB (with owner B) which is a parent
    of UnitC (with owner C), then calling the function with the UUID of
    UnitC will return `{<owner A uuid>, <owner B uuid>, <owner C uuid>}`

    :param uuid: the UUID of the org unit
    :return: set of owner UUIDs
    """

    logger.debug("get_ancestor_owners called")

    ancestors_tree = await _get_ancestors(uuid)
    ancestor_uuids = uuid_extractor.get_ancestor_uuids(ancestors_tree)

    ancestor_owner_sublists = await asyncio.gather(
        *(_get_entity_owners(uuid, EntityType.ORG_UNIT) for uuid in ancestor_uuids)
    )

    ancestor_owners = set(flatten(ancestor_owner_sublists))

    return ancestor_owners


async def _get_ancestors(uuid: UUID) -> List[dict]:
    """
    Get org unit ancestor tree from LoRa.

    :param uuid: UUID of the leaf org unit in the tree
    :return: nested ancestor org unit tree branch (including the leaf unit)

    **Example return value**

    .. sourcecode:: python

        [
            {
                "name": "Overordnet Enhed",
                "user_key": "root",
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {
                    "from": "2016-01-01",
                    "to": None
                },
                "children": [
                    {
                        "name": "Humanistisk fakultet",
                        "user_key": "hum",
                        "uuid": "9d07123e-47ac-4a9a-88c8-da82e3a4bc9e",
                        "validity": {
                            "from": "2016-01-01",
                            "to": None
                        },
                        "children": [
                            {
                                "name": "Filosofisk Institut",
                                "user_key": "fil",
                                "uuid": "85715fc7-925d-401b-822d-467eb4b163b6",
                                "validity": {
                                    "from": "2016-01-01",
                                    "to": None
                                }
                            }
                        ]
                    }
                ]
            }
        ]

    """
    c = common.get_connector()
    return await mora.service.orgunit.get_unit_tree(c, [str(uuid)], with_siblings=False)


async def _get_entity_owners(uuid: UUID, entity_type: EntityType) -> Set[UUID]:
    """
    Get the UUID of the owner of an entity (org unit or employee)

    :param uuid: the UUID of the entity
    :param entity_type: the type of entity (org unit or employee)
    :return: list of UUIDs of the owners of the entity
    """

    # NOTE!!: Currently, there can be multiple owners (but this will change)

    logger.debug("_get_entity_owners called for entity type ", entity_type=entity_type)

    c = common.get_connector()
    r = await OwnerReader.get_from_type(c, entity_type.value, uuid, changed_since=None)

    r = filter(bool, r)
    return {UUID(item[OWNER][UUID_KEY]) for item in r}
