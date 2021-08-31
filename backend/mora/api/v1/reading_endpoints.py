# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from mora import mapping
from mora.api.v1.models import Address
from mora.api.v1.models import Association
from mora.api.v1.models import Employee
from mora.api.v1.models import Engagement
from mora.api.v1.models import EngagementAssociation
from mora.api.v1.models import ITSystemBinding
from mora.api.v1.models import KLE
from mora.api.v1.models import Leave
from mora.api.v1.models import Manager
from mora.api.v1.models import OrganisationUnitFull
from mora.api.v1.models import Owner
from mora.api.v1.models import RelatedUnit
from mora.api.v1.models import Role
from mora.api.v1.models import to_only_uuid_model
from mora.common import get_connector
from mora.handler.impl.employee import ROLE_TYPE as EMPLOYEE_ROLE_TYPE
from mora.handler.impl.org_unit import ROLE_TYPE as ORG_UNIT_ROLE_TYPE
from mora.handler.reading import get_handler_for_type
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
    c = get_connector()
    search_params = _extract_search_params(query_args=query_args)
    return await _query_orgfunk(
        c=c,
        orgfunk_type=orgfunk_type,
        search_params=search_params,
        changed_since=changed_since,
    )


class CommonQueryParams:
    def __init__(
        self,
        at: Optional[Any] = None,
        validity: Optional[Any] = None,
        changed_since: Optional[Union[datetime, date]] = None,
    ):
        self.at = at
        self.validity = validity
        self.changed_since = changed_since


@router.get(
    f"/{MoOrgFunk.ADDRESS.value}",
    response_model=List[Address],
)
@date_to_datetime
async def search_address(
    common: CommonQueryParams = Depends(),
    engagement: Optional[str] = None,
):
    args = {"at": common.at, "validity": common.validity}
    if engagement is not None:
        args[MoOrgFunk.ENGAGEMENT.value] = engagement
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.ADDRESS,
        query_args=args,
        changed_since=common.changed_since,
    )


@router.get(
    f"/{MoOrgFunk.ENGAGEMENT_ASSOCIATION.value}",
    response_model=List[EngagementAssociation],
)
@date_to_datetime
async def search_engagement_association(
    common: CommonQueryParams = Depends(),
    engagement: Optional[UUID] = None,
):
    args = {"at": common.at, "validity": common.validity}
    if engagement is not None:
        args[MoOrgFunk.ENGAGEMENT.value] = engagement
    return await orgfunk_endpoint(
        orgfunk_type=MoOrgFunk.ENGAGEMENT_ASSOCIATION,
        query_args=args,
        changed_since=common.changed_since,
    )


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


def search_func_factory(orgfunk: MoOrgFunk):
    """
    convenient wrapper to generate "parametrized" endpoints
    :param orgfunk: parameter we are parametrized over
    :return: expose-ready function
    """

    @date_to_datetime
    async def search_orgfunk(
        common: CommonQueryParams = Depends(),
    ):
        return await orgfunk_endpoint(
            orgfunk_type=orgfunk,
            query_args={"at": common.at, "validity": common.validity},
            changed_since=common.changed_since,
        )

    search_orgfunk.__name__ = f"search_{orgfunk.value}"
    return search_orgfunk


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
        only_primary_uuid: Optional[bool] = None,
    ):
        args = {
            "at": at,
            "validity": validity,
            mapping.UUID: uuid,
            "only_primary_uuid": only_primary_uuid,
        }
        return await orgfunk_endpoint(
            orgfunk_type=orgfunk,
            query_args=args,
        )

    get_orgfunk_by_uuid.__name__ = f"get_{orgfunk.value}_by_uuid"
    return get_orgfunk_by_uuid


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

for orgfunk in [
    MoOrgFunk.ASSOCIATION,
    MoOrgFunk.ENGAGEMENT,
    MoOrgFunk.IT,
    MoOrgFunk.KLE,
    MoOrgFunk.LEAVE,
    MoOrgFunk.MANAGER,
    MoOrgFunk.OWNER,
    MoOrgFunk.RELATED_UNIT,
    MoOrgFunk.ROLE,
]:
    return_model = orgfunk_type_map[orgfunk]
    router.get(
        f"/{orgfunk.value}",
        response_model=List[return_model],
    )(search_func_factory(orgfunk))


for orgfunk, return_model in orgfunk_type_map.items():
    only_uuid_model = to_only_uuid_model(return_model)
    router.get(
        f"/{orgfunk.value}/by_uuid",
        response_model=Union[List[return_model], List[only_uuid_model]],
    )(uuid_func_factory(orgfunk))


role_type_map = {
    EMPLOYEE_ROLE_TYPE: Employee,
    ORG_UNIT_ROLE_TYPE: OrganisationUnitFull,
}
for role_type, model in role_type_map.items():
    search_function = role_type_search_factory(role_type)
    get_function = role_type_uuid_factory(role_type)

    router.get(
        f"/{role_type}",
        response_model=List[model],
    )(date_to_datetime(search_function))
    router.get(
        f"/{role_type}/by_uuid",
        response_model=List[model],
    )(date_to_datetime(get_function))
