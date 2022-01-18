#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
"""LoRa data read helpers."""
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
from typing import Dict
from typing import List
from typing import Union
from uuid import UUID

from mora.common import get_connector
from mora.handler.reading import get_handler_for_type
from mora.mapping import MoOrgFunk

# --------------------------------------------------------------------------------------
# Readers
# --------------------------------------------------------------------------------------

ORGFUNK_VALUES = tuple(map(lambda x: x.value, MoOrgFunk))


def to_lora_args(key, value):
    if key in ORGFUNK_VALUES:
        return f"tilknyttedefunktioner:{key}", value
    return key, value


def _extract_search_params(
    query_args: Dict[Union[Any, MoOrgFunk], Any]
) -> Dict[Any, Any]:
    """Deals with special LoRa-search format.

    Requires data to be written properly formatted.

    One day this should be tightly coupled with the writing logic, but not today.

    :param query_args:
    :return:
    """
    args = {**query_args}
    args.pop("at", None)
    args.pop("validity", None)

    # Transform from mo-search-params to lora-search-params
    args = dict([to_lora_args(key, value) for key, value in args.items()])

    return args


async def search_role_type(role_type: str):
    connector = get_connector()
    handler = get_handler_for_type(role_type)
    return await handler.get(
        c=connector,
        search_fields=_extract_search_params(query_args={"at": None, "validity": None}),
        changed_since=None,
    )


async def get_role_type_by_uuid(role_type: str, uuid: List[UUID]):
    c = get_connector()
    cls = get_handler_for_type(role_type)
    return await cls.get(
        c=c,
        search_fields=_extract_search_params(
            query_args={"at": None, "validity": None, "uuid": uuid}
        ),
        changed_since=None,
    )
