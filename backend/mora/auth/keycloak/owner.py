# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

import asyncio
from typing import List
from typing import Optional
from typing import Set
from uuid import UUID
from more_itertools import flatten

from mora import common
from mora.handler.impl.owner import OwnerReader
import mora.service.orgunit
from mora.mapping import OU
from mora.auth.keycloak import uuid_extractor


async def get_ancestor_owners(uuid: UUID) -> Set[UUID]:
    """
    Get the owners of an org unit and all of its ancestors. For example, if
    UnitA (with owner A) is a parent of UnitB (with owner B) which is a parent
    of UnitC (with owner C), then calling the function with the UUID of
    UnitC will return `{<owner A uuid>, <owner B uuid>, <owner C uuid>}`

    :param uuid: the UUID of the org unit
    :return: set of owner UUIDs
    """

    ancestors_tree = await _get_ancestors(uuid)
    ancestor_uuids = uuid_extractor.get_ancestor_uuids(ancestors_tree)

    ancestor_owner_sublists = await asyncio.gather(
        *map(_get_org_unit_owners, ancestor_uuids)
    )
    ancestor_owners = set(flatten(ancestor_owner_sublists))

    return ancestor_owners


async def _get_ancestors(uuid: UUID) -> List[dict]:
    """
    Get org unit ancestor tree from LoRa.

    :param uuid: UUID of the leaf org unit in the tree
    :return: nested ancestor org unit tree

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
    return await mora.service.orgunit.get_unit_tree(
        c, [str(uuid)], with_siblings=False
    )


async def _get_org_unit_owners(uuid: UUID) -> List[Optional[UUID]]:
    """
    Get the UUID of the owner of an org unit

    :param uuid: the UUID of the org unit
    :return: list of UUIDs of the owners of the org unit
    """

    # NOTE!!: Currently, there can be multiple owners (but this will change)

    c = common.get_connector()
    r = await OwnerReader.get_from_type(c, OU, uuid, changed_since=None)

    return [UUID(item['owner']['uuid']) for item in r if item]
