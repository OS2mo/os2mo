# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import parse_obj_as


from mora import common, mapping
from mora.handler.impl.employee import ROLE_TYPE as EMPLOYEE_ROLE_TYPE
from mora.handler.impl.org_unit import ROLE_TYPE as ORG_UNIT_ROLE_TYPE
from mora.handler.reading import get_handler_for_type
from mora.api.v1.models import Address
from mora.api.v1.models import Association
from mora.api.v1.models import Employee, MOBase
from mora.api.v1.models import RelatedUnit
from mora.api.v1.models import Engagement
from mora.api.v1.models import EngagementAssociation
from mora.api.v1.models import Owner
from mora.api.v1.models import OrganisationUnitFull
from mora.api.v1.models import Manager
from mora.api.v1.models import Role
from mora.api.v1.models import KLE
from mora.api.v1.models import Leave
from mora.api.v1.models import ITSystemBinding
from mora.lora import Connector
from mora.mapping import MoOrgFunk
from mora.util import date_to_datetime

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


def export_orgfunk_endpoints(orgfunk, return_type: MOBase):
    @date_to_datetime
    async def search_orgfunk_base(
        at: Optional[Any] = None,
        validity: Optional[Any] = None,
        changed_since: Optional[Union[datetime, date]] = None,
    ):
        org_funcs = await orgfunk_endpoint(
            orgfunk_type=orgfunk,
            query_args={"at": at, "validity": validity},
            changed_since=changed_since,
        )
        return parse_obj_as(List[return_type], org_funcs)  # type: ignore

    @date_to_datetime
    async def search_orgfunk_special(
        at: Optional[Any] = None,
        validity: Optional[Any] = None,
        changed_since: Optional[Union[datetime, date]] = None,
        engagement: Optional[UUID] = None,
    ):
        args = {"at": at, "validity": validity}
        if engagement is not None:
            args[MoOrgFunk.ENGAGEMENT.value] = engagement
        return await orgfunk_endpoint(
            orgfunk_type=orgfunk,
            query_args=args,
            changed_since=changed_since,
        )

    search_orgfunk = search_orgfunk_base
    if orgfunk in [MoOrgFunk.ENGAGEMENT_ASSOCIATION, MoOrgFunk.ADDRESS]:
        search_orgfunk = search_orgfunk_special

    search_orgfunk.__name__ = f"get_{orgfunk.value}"

    @date_to_datetime
    async def get_orgfunk_by_uuid(
        uuid: List[UUID] = Query(...),
        at: Optional[Any] = None,
        validity: Optional[Any] = None,
        only_primary_uuid: Optional[Any] = None,
    ):
        args = {
            "at": at,
            "validity": validity,
            mapping.UUID: uuid,
            "only_primary_uuid": only_primary_uuid,
        }
        org_funcs = await orgfunk_endpoint(orgfunk_type=orgfunk, query_args=args)
        return parse_obj_as(List[return_type], org_funcs)  # type: ignore

    get_orgfunk_by_uuid.__name__ = f"get_{orgfunk.value}_by_uuid"

    router.get(
        f"/{orgfunk.value}",
        response_model=List[return_type],  # type: ignore
    )(search_orgfunk)

    router.get(
        f"/{orgfunk.value}/by_uuid",
        response_model=List[return_type],  # type: ignore
    )(get_orgfunk_by_uuid)


def export_role_endpoints(role, return_type):
    @date_to_datetime
    async def search_role(
        at: Optional[Any] = None,
        validity: Optional[Any] = None,
        changed_since: Optional[Union[datetime, date]] = None,
    ):
        """
        This can be expanded with general search paramters
        :param at:
        :param validity:
        :param changed_since:
        :return:
        """
        c = common.get_connector()
        cls = get_handler_for_type(role)
        roles = await cls.get(
            c, {"at": at, "validity": validity}, changed_since=changed_since
        )
        return parse_obj_as(List[return_type], roles)  # type: ignore

    search_role.__name__ = f"search_{role}"

    @date_to_datetime
    async def get_role_by_uuid(
        uuid: List[UUID] = Query(...),
        at: Optional[Any] = None,
        validity: Optional[Any] = None,
        changed_since: Optional[Union[datetime, date]] = None,
    ):
        """
        As uuid is allowed, this cannot be expanded with general search
        parameters, a limitation posed by LoRa

        :param uuid:
        :param at:
        :param validity:
        :param changed_since: Date used to filter registrations from LoRa
        :return:
        """
        c = common.get_connector()
        cls = get_handler_for_type(role)
        roles = await cls.get(
            c,
            {"at": at, "validity": validity, "uuid": uuid},
            changed_since=changed_since,
        )
        return parse_obj_as(List[return_type], roles)  # type: ignore

    get_role_by_uuid.__name__ = f"get_{role}_by_uuid"

    router.get(
        f"/{role}",
        response_model=List[return_type],
    )(search_role)

    router.get(
        f"/{role}/by_uuid",
        response_model=List[return_type],
    )(get_role_by_uuid)


orgfunk_type_map = {
    MoOrgFunk.ADDRESS: Address,
    MoOrgFunk.ASSOCIATION: Association,
    MoOrgFunk.ENGAGEMENT: Engagement,
    MoOrgFunk.ENGAGEMENT_ASSOCIATION: EngagementAssociation,
    MoOrgFunk.IT: ITSystemBinding,
    MoOrgFunk.KLE: KLE,
    MoOrgFunk.LEAVE: Leave,
    MoOrgFunk.MANAGER: Manager,
    MoOrgFunk.OWNER: Owner,
    MoOrgFunk.RELATED_UNIT: RelatedUnit,
    MoOrgFunk.ROLE: Role,
}
for orgfunk in MoOrgFunk:
    assert orgfunk in orgfunk_type_map

for orgfunk, return_type in orgfunk_type_map.items():
    export_orgfunk_endpoints(orgfunk, return_type)

role_type_map = {
    ORG_UNIT_ROLE_TYPE: OrganisationUnitFull,
    EMPLOYEE_ROLE_TYPE: Employee,
}
for role, return_type in role_type_map.items():
    export_role_endpoints(role, return_type)
