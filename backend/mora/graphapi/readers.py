#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from fastapi import Depends
from fastapi import Query

from mora.common import get_connector
from mora.handler.reading import get_handler_for_type
from mora.mapping import MoOrgFunk

# --------------------------------------------------------------------------------------
# Code
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


class CommonQueryParams:
    def __init__(
        self,
        at: Optional[Union[date, datetime]] = Query(
            None, description="ISO 8601-compatible date or datetime."
        ),
        validity: Optional[str] = Query(
            None,
            description=(
                "Supports strings {`past`, `present`, `future`}, or a time interval "
                "formatted as `<start>/<end>`, where `<start>` and `<end>` can be an "
                "ISO 8601-formatted string or the values {`-infinity`, `infinity`}."
            ),
            examples={
                "present": {
                    "summary": "Current valid elements",
                    "value": "present",
                },
                "past": {
                    "summary": "Previously valid elements",
                    "value": "past",
                },
                "future": {
                    "summary": "Future valid elements",
                    "value": "future",
                },
                "interval": {
                    "summary": "Elements valid in a specific interval",
                    "value": "1912-06-23T12:17:56+01:00/1954-06-07",
                },
                "interval_infinite": {
                    "summary": "Elements valid from a specific date",
                    "value": "1991-02-20/infinity",
                },
            },
        ),
        changed_since: Optional[Union[date, datetime]] = None,
    ):
        self.at = at
        self.validity = validity
        self.changed_since = changed_since


def role_type_search_factory(role_type: str):
    async def search_role_type(
        common: CommonQueryParams = Depends(),
    ):
        """
        This can be expanded with general search paramters
        :param at:
        :param validity:
        :param changed_since:
        :return:
        """
        c = get_connector()
        cls = get_handler_for_type(role_type)
        return await cls.get(
            c=c,
            search_fields=_extract_search_params(
                query_args={"at": common.at, "validity": common.validity}
            ),
            changed_since=common.changed_since,
        )

    search_role_type.__name__ = f"search_{role_type}"
    return search_role_type


def role_type_uuid_factory(role_type: str):
    async def get_role_type_by_uuid(
        uuid: List[UUID] = Query(...),
        common: CommonQueryParams = Depends(),
    ) -> List[Dict]:
        """
        As uuid is allowed, this cannot be expanded with general search
        parameters, a limitation posed by LoRa

        :param uuid:
        :param at:
        :param validity:
        :param changed_since:
        :return:
        """
        c = get_connector()
        cls = get_handler_for_type(role_type)
        return await cls.get(
            c=c,
            search_fields=_extract_search_params(
                query_args={"at": common.at, "validity": common.validity, "uuid": uuid}
            ),
            changed_since=common.changed_since,
        )

    get_role_type_by_uuid.__name__ = f"get_{role_type}_by_uuid"
    return get_role_type_by_uuid


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
