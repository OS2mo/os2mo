# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Query
from mora import common
from mora.handler.impl.employee import ROLE_TYPE as EMPLOYEE_ROLE_TYPE
from mora.handler.impl.org_unit import ROLE_TYPE as ORG_UNIT_ROLE_TYPE
from mora.handler.reading import get_handler_for_type
from mora.lora import Connector
from mora.mapping import MoOrgFunk
from mora.util import date_to_datetime
from starlette.datastructures import ImmutableMultiDict

router = APIRouter(prefix="/api/v1")

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
    c: Connector,
    orgfunk_type: MoOrgFunk,
    search_params: Dict[str, Any],
    changed_since: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    helper, used to make the actual queries against LoRa
    :param c:
    :param orgfunk_type:
    :param search_params:
    :return:
    """
    cls = get_handler_for_type(orgfunk_type.value)
    ret = await cls.get(c, search_params, changed_since=changed_since)
    return ret


@date_to_datetime
async def orgfunk_endpoint(
    orgfunk_type: MoOrgFunk,
    query_args: Dict[str, Any],
    changed_since: Optional[Union[datetime, date]] = None,
) -> Dict[str, Any]:
    c = common.get_connector()
    search_params = _extract_search_params(query_args=query_args)
    return await _query_orgfunk(
        c=c,
        orgfunk_type=orgfunk_type,
        search_params=search_params,
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.ENGAGEMENT.value}")
@date_to_datetime
async def search_engagement(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
) -> Dict[str, Any]:
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.ENGAGEMENT,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.ASSOCIATION.value}")
@date_to_datetime
async def search_association(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.ASSOCIATION,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.IT.value}")
@date_to_datetime
async def search_it(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.IT,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.KLE.value}")
@date_to_datetime
async def search_kle(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.KLE,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.ROLE.value}")
@date_to_datetime
async def search_role(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.ROLE,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.ADDRESS.value}")
@date_to_datetime
async def search_address(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
    engagement: Optional[str] = None,
):
    args = {"at": at, "validity": validity}
    if engagement is not None:
        args[MoOrgFunk.ENGAGEMENT.value] = engagement
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.ADDRESS,
        query_args=args,
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.ENGAGEMENT_ASSOCIATION.value}")
@date_to_datetime
async def search_engagement_association(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
    engagement: Optional[UUID] = None,
):
    args = {"at": at, "validity": validity}
    if engagement is not None:
        args[MoOrgFunk.ENGAGEMENT.value] = engagement
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.ENGAGEMENT_ASSOCIATION,
        query_args=args,
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.LEAVE.value}")
@date_to_datetime
async def search_leave(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.LEAVE,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.MANAGER.value}")
@date_to_datetime
async def search_manager(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.MANAGER,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{MoOrgFunk.RELATED_UNIT.value}")
@date_to_datetime
async def search_related_unit(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.RELATED_UNIT,
        query_args={"at": at, "validity": validity},
        changed_since=changed_since,
    )


@router.get(f"/{EMPLOYEE_ROLE_TYPE}")
@date_to_datetime
async def search_employee(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    """
    This can be expanded with general search paramters
    :param at:
    :param validity:
    :param changed_since:
    :return:
    """
    c = common.get_connector()
    cls = get_handler_for_type(EMPLOYEE_ROLE_TYPE)
    return await cls.get(
        c, {"at": at, "validity": validity}, changed_since=changed_since
    )


@router.get(f"/{EMPLOYEE_ROLE_TYPE}/by_uuid")
@date_to_datetime
async def get_employee_by_uuid(
    uuid: List[UUID] = Query(...),
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    """
    As uuid is allowed, this cannot be expanded with general search
    parameters, a limitation posed by LoRa

    :param uuid:
    :param at:
    :param validity:
    :param changed_since:
    :return:
    """
    c = common.get_connector()
    cls = get_handler_for_type(EMPLOYEE_ROLE_TYPE)
    return await cls.get(
        c,
        {"at": at, "validity": validity, "uuid": uuid},
        changed_since=changed_since,
    )


@router.get(f"/{ORG_UNIT_ROLE_TYPE}")
@date_to_datetime
async def search_org_unit(
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    """
    This can be expanded with general search paramters

    :param at:
    :param validity:
    :param changed_since:
    :return:
    """
    c = common.get_connector()
    cls = get_handler_for_type(ORG_UNIT_ROLE_TYPE)
    return await cls.get(
        c, {"at": at, "validity": validity}, changed_since=changed_since
    )


@router.get(f"/{ORG_UNIT_ROLE_TYPE}/by_uuid")
@date_to_datetime
async def get_org_unit_by_uuid(
    uuid: List[UUID] = Query(...),
    at: Optional[Any] = None,
    validity: Optional[Any] = None,
    changed_since: Optional[Union[datetime, date]] = Query(None),
):
    """
    As uuid is allowed, this cannot be expanded with general search
    parameters, a limitation posed by LoRa

    :param uuid:
    :param at:
    :param validity:
    :param changed_since:
    :return:
    """
    c = common.get_connector()
    cls = get_handler_for_type(ORG_UNIT_ROLE_TYPE)
    return await cls.get(
        c,
        {"at": at, "validity": validity, "uuid": uuid},
        changed_since=changed_since,
    )


def to_dict(multi_dict: ImmutableMultiDict) -> Dict[Any, Union[Any, List[Any]]]:
    """
    flattens a multi-dict to a simple dictionary, collecting items in lists as needed
    :param multi_dict:
    :return:
    """
    # convert to dictionary
    dictionary = {key: multi_dict.getlist(key) for key in multi_dict}

    # unpack lists of one
    return {
        key: list_value[0] if len(list_value) == 1 else list_value
        for key, list_value in dictionary.items()
    }


def uuid_func_factory(orgfunk: MoOrgFunk):
    """
    convenient wrapper to generate "parametrized" endpoints
    :param orgfunk: parameter we are parametrized over
    :return: expose-ready function
    """

    async def get_orgfunk_by_uuid(
        uuid: List[UUID] = Query(...),
        at: Optional[Any] = None,
        validity: Optional[Any] = None,
        only_primary_uuid: Optional[Any] = None,
    ):
        args = {
            "at": at,
            "validity": validity,
            "uuid": uuid,
            "only_primary_uuid": only_primary_uuid,
        }
        return await orgfunk_endpoint(orgfunk_type=orgfunk, query_args=args)

    get_orgfunk_by_uuid.__name__ = f"get_{orgfunk.value}_by_uuid"
    return get_orgfunk_by_uuid


for orgfunk in MoOrgFunk:
    router.get(f"/{orgfunk.value}/by_uuid")(uuid_func_factory(orgfunk))
