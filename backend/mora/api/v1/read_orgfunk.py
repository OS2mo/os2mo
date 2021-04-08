# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from typing import Any, Dict, Union

import flask

from mora import async_util, common
from mora.exceptions import ErrorCodes
from mora.handler.reading import get_handler_for_type
from mora.lora import Connector
from mora.mapping import MoOrgFunk
from mora.util import restrictargs

blueprint = flask.Blueprint(
    "read", __name__, static_url_path="", url_prefix="/api/v1"
)

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


async def _query_orgfunk(
    c: Connector, orgfunk_type: MoOrgFunk, search_params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    helper, used to make the actual queries against LoRa
    :param c:
    :param orgfunk_type:
    :param search_params:
    :return:
    """
    cls = get_handler_for_type(orgfunk_type.value)
    ret = await cls.get(c, search_params)
    return ret


async def orgfunk_endpoint(orgfunk_type: MoOrgFunk,
                           query_args: Dict[str, Any]) -> Dict[str, Any]:
    c = common.get_connector()
    search_params = _extract_search_params(query_args=query_args)
    return await _query_orgfunk(
        c=c, orgfunk_type=orgfunk_type, search_params=search_params
    )


@blueprint.route(f"/{MoOrgFunk.ENGAGEMENT.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_engagement() -> flask.Response:
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.ENGAGEMENT, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.ASSOCIATION.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_association():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.ASSOCIATION, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.IT.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_it():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.IT, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.KLE.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_kle():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.KLE, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.ROLE.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_role():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.ROLE, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.ADDRESS.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_address():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.ADDRESS, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.LEAVE.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_leave():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.LEAVE, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.MANAGER.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_manager():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.MANAGER, query_args=flask.request.args
        )
    )


@blueprint.route(f"/{MoOrgFunk.RELATED_UNIT.value}")
@restrictargs("at", "validity", *ORGFUNK_VALUES)
@async_util.async_to_sync
async def search_related_unit():
    return flask.jsonify(
        await orgfunk_endpoint(
            orgfunk_type=MoOrgFunk.RELATED_UNIT, query_args=flask.request.args
        )
    )


def uuid_func_factory(orgfunk: MoOrgFunk):
    """
    convenient wrapper to generate "parametrized" endpoints
    :param orgfunk: parameter we are parametrized over
    :return: expose-ready function
    """

    @restrictargs("at", "validity", required=["uuid"])
    @async_util.async_to_sync
    async def get_orgfunk_by_uuid():
        # Better implementation available once FastAPI
        if not set(flask.request.args.keys()) <= {"at", "validity", "uuid"}:
            raise ErrorCodes.E_INVALID_INPUT()
        return await orgfunk_endpoint(
            orgfunk_type=orgfunk, query_args=flask.request.args
        )

    get_orgfunk_by_uuid.__name__ = f"get_{orgfunk.value}_by_uuid"
    return get_orgfunk_by_uuid


for orgfunk in MoOrgFunk:
    blueprint.route(f"/{orgfunk.value}/by_uuid")(uuid_func_factory(orgfunk))
