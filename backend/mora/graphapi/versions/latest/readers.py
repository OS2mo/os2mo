# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""LoRa data read helpers."""

from typing import Any
from uuid import UUID

from mora.common import get_connector
from mora.handler.reading import get_handler_for_type
from mora.mapping import MoOrgFunk

ORGFUNK_VALUES = tuple(map(lambda x: x.value, MoOrgFunk))


def to_lora_args(key: Any, value: Any) -> tuple[Any, Any]:
    if key in ORGFUNK_VALUES:  # pragma: no cover
        return f"tilknyttedefunktioner:{key}", value
    return key, value


def _extract_search_params(query_args: dict[Any | MoOrgFunk, Any]) -> dict[Any, Any]:
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


async def search_role_type(role_type: str, **kwargs: Any) -> list[dict[str, Any]]:
    connector = get_connector()
    handler = get_handler_for_type(role_type)
    return await handler.get(
        c=connector,
        search_fields=_extract_search_params(
            query_args={
                "at": None,
                "validity": None,
                **kwargs,  # type: ignore
            }
        ),
    )


async def get_role_type_by_uuid(
    role_type: str, uuid: list[UUID]
) -> list[dict[str, Any]]:
    c = get_connector()
    cls = get_handler_for_type(role_type)
    return await cls.get(
        c=c,
        search_fields=_extract_search_params(
            query_args={"at": None, "validity": None, "uuid": uuid}
        ),
    )
