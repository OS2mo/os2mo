from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from ..types import CPRNumber
from ._testing_ituser_create import TestingItuserCreate
from ._testing_ituser_create import TestingItuserCreateItuserCreate
from ._testing_user_create import TestingUserCreate
from ._testing_user_create import TestingUserCreateEmployeeCreate
from .address_terminate import AddressTerminate
from .address_terminate import AddressTerminateAddressTerminate
from .async_base_client import AsyncBaseClient
from .base_model import UNSET
from .base_model import UnsetType
from .class_create import ClassCreate
from .class_create import ClassCreateClassCreate
from .class_update import ClassUpdate
from .class_update import ClassUpdateClassUpdate
from .employee_refresh import EmployeeRefresh
from .employee_refresh import EmployeeRefreshEmployeeRefresh
from .engagement_terminate import EngagementTerminate
from .engagement_terminate import EngagementTerminateEngagementTerminate
from .input_types import AddressFilter
from .input_types import AddressTerminateInput
from .input_types import ClassCreateInput
from .input_types import ClassUpdateInput
from .input_types import EmployeeCreateInput
from .input_types import EngagementFilter
from .input_types import EngagementTerminateInput
from .input_types import ITSystemCreateInput
from .input_types import ITUserCreateInput
from .input_types import ITUserFilter
from .input_types import ITUserTerminateInput
from .itsystem_create import ItsystemCreate
from .itsystem_create import ItsystemCreateItsystemCreate
from .ituser_terminate import ItuserTerminate
from .ituser_terminate import ItuserTerminateItuserTerminate
from .org_unit_engagements_refresh import OrgUnitEngagementsRefresh
from .org_unit_engagements_refresh import OrgUnitEngagementsRefreshEngagementRefresh
from .read_address_relation_uuids import ReadAddressRelationUuids
from .read_address_relation_uuids import ReadAddressRelationUuidsAddresses
from .read_addresses import ReadAddresses
from .read_addresses import ReadAddressesAddresses
from .read_all_ituser_user_keys_by_itsystem_uuid import (
    ReadAllItuserUserKeysByItsystemUuid,
)
from .read_all_ituser_user_keys_by_itsystem_uuid import (
    ReadAllItuserUserKeysByItsystemUuidItusers,
)
from .read_all_itusers import ReadAllItusers
from .read_all_itusers import ReadAllItusersItusers
from .read_class_name_by_class_uuid import ReadClassNameByClassUuid
from .read_class_name_by_class_uuid import ReadClassNameByClassUuidClasses
from .read_class_user_keys import ReadClassUserKeys
from .read_class_user_keys import ReadClassUserKeysClasses
from .read_class_uuid import ReadClassUuid
from .read_class_uuid import ReadClassUuidClasses
from .read_class_uuid_by_facet_and_class_user_key import (
    ReadClassUuidByFacetAndClassUserKey,
)
from .read_class_uuid_by_facet_and_class_user_key import (
    ReadClassUuidByFacetAndClassUserKeyClasses,
)
from .read_employee_addresses import ReadEmployeeAddresses
from .read_employee_addresses import ReadEmployeeAddressesAddresses
from .read_employee_uuid_by_cpr_number import ReadEmployeeUuidByCprNumber
from .read_employee_uuid_by_cpr_number import ReadEmployeeUuidByCprNumberEmployees
from .read_employee_uuid_by_ituser_user_key import ReadEmployeeUuidByItuserUserKey
from .read_employee_uuid_by_ituser_user_key import (
    ReadEmployeeUuidByItuserUserKeyItusers,
)
from .read_employees import ReadEmployees
from .read_employees import ReadEmployeesEmployees
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnit,
)
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnitEngagements,
)
from .read_engagement_employee_uuid import ReadEngagementEmployeeUuid
from .read_engagement_employee_uuid import ReadEngagementEmployeeUuidEngagements
from .read_engagement_uuid_by_ituser_user_key import ReadEngagementUuidByItuserUserKey
from .read_engagement_uuid_by_ituser_user_key import (
    ReadEngagementUuidByItuserUserKeyItusers,
)
from .read_engagements import ReadEngagements
from .read_engagements import ReadEngagementsEngagements
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuid
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuidEngagements
from .read_engagements_by_engagements_filter import ReadEngagementsByEngagementsFilter
from .read_engagements_by_engagements_filter import (
    ReadEngagementsByEngagementsFilterEngagements,
)
from .read_engagements_is_primary import ReadEngagementsIsPrimary
from .read_engagements_is_primary import ReadEngagementsIsPrimaryEngagements
from .read_facet_classes import ReadFacetClasses
from .read_facet_classes import ReadFacetClassesClasses
from .read_facet_uuid import ReadFacetUuid
from .read_facet_uuid import ReadFacetUuidFacets
from .read_filtered_addresses import ReadFilteredAddresses
from .read_filtered_addresses import ReadFilteredAddressesAddresses
from .read_filtered_itusers import ReadFilteredItusers
from .read_filtered_itusers import ReadFilteredItusersItusers
from .read_is_primary_engagements import ReadIsPrimaryEngagements
from .read_is_primary_engagements import ReadIsPrimaryEngagementsEngagements
from .read_itsystems import ReadItsystems
from .read_itsystems import ReadItsystemsItsystems
from .read_ituser_by_employee_and_itsystem_uuid import (
    ReadItuserByEmployeeAndItsystemUuid,
)
from .read_ituser_by_employee_and_itsystem_uuid import (
    ReadItuserByEmployeeAndItsystemUuidItusers,
)
from .read_ituser_employee_uuid import ReadItuserEmployeeUuid
from .read_ituser_employee_uuid import ReadItuserEmployeeUuidItusers
from .read_itusers import ReadItusers
from .read_itusers import ReadItusersItusers
from .read_org_unit_addresses import ReadOrgUnitAddresses
from .read_org_unit_addresses import ReadOrgUnitAddressesAddresses
from .read_org_units import ReadOrgUnits
from .read_org_units import ReadOrgUnitsOrgUnits
from .read_root_org_uuid import ReadRootOrgUuid
from .read_root_org_uuid import ReadRootOrgUuidOrg
from .set_job_title import SetJobTitle
from .set_job_title import SetJobTitleEngagementUpdate


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):
    async def _testing_user_create(
        self, input: EmployeeCreateInput
    ) -> TestingUserCreateEmployeeCreate:
        query = gql(
            """
            mutation __testing_user_create($input: EmployeeCreateInput!) {
              employee_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingUserCreate.parse_obj(data).employee_create

    async def _testing_ituser_create(
        self, input: ITUserCreateInput
    ) -> TestingItuserCreateItuserCreate:
        query = gql(
            """
            mutation __testing_ituser_create($input: ITUserCreateInput!) {
              ituser_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingItuserCreate.parse_obj(data).ituser_create

    async def itsystem_create(
        self, input: ITSystemCreateInput
    ) -> ItsystemCreateItsystemCreate:
        query = gql(
            """
            mutation itsystem_create($input: ITSystemCreateInput!) {
              itsystem_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItsystemCreate.parse_obj(data).itsystem_create

    async def read_facet_classes(self, facet_user_key: str) -> ReadFacetClassesClasses:
        query = gql(
            """
            query read_facet_classes($facet_user_key: String!) {
              classes(filter: {facet: {user_keys: [$facet_user_key]}}) {
                objects {
                  current {
                    user_key
                    uuid
                    scope
                    name
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"facet_user_key": facet_user_key}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadFacetClasses.parse_obj(data).classes

    async def read_facet_uuid(self, user_key: str) -> ReadFacetUuidFacets:
        query = gql(
            """
            query read_facet_uuid($user_key: String!) {
              facets(filter: {user_keys: [$user_key]}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"user_key": user_key}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadFacetUuid.parse_obj(data).facets

    async def class_create(self, input: ClassCreateInput) -> ClassCreateClassCreate:
        query = gql(
            """
            mutation class_create($input: ClassCreateInput!) {
              class_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ClassCreate.parse_obj(data).class_create

    async def read_class_uuid(self, user_key: str) -> ReadClassUuidClasses:
        query = gql(
            """
            query read_class_uuid($user_key: String!) {
              classes(filter: {user_keys: [$user_key]}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"user_key": user_key}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadClassUuid.parse_obj(data).classes

    async def class_update(self, input: ClassUpdateInput) -> ClassUpdateClassUpdate:
        query = gql(
            """
            mutation class_update($input: ClassUpdateInput!) {
              class_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ClassUpdate.parse_obj(data).class_update

    async def read_root_org_uuid(self) -> ReadRootOrgUuidOrg:
        query = gql(
            """
            query read_root_org_uuid {
              org {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadRootOrgUuid.parse_obj(data).org

    async def address_terminate(
        self, input: AddressTerminateInput
    ) -> AddressTerminateAddressTerminate:
        query = gql(
            """
            mutation address_terminate($input: AddressTerminateInput!) {
              address_terminate(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AddressTerminate.parse_obj(data).address_terminate

    async def engagement_terminate(
        self, input: EngagementTerminateInput
    ) -> EngagementTerminateEngagementTerminate:
        query = gql(
            """
            mutation engagement_terminate($input: EngagementTerminateInput!) {
              engagement_terminate(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return EngagementTerminate.parse_obj(data).engagement_terminate

    async def ituser_terminate(
        self, input: ITUserTerminateInput
    ) -> ItuserTerminateItuserTerminate:
        query = gql(
            """
            mutation ituser_terminate($input: ITUserTerminateInput!) {
              ituser_terminate(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItuserTerminate.parse_obj(data).ituser_terminate

    async def read_employees_with_engagement_to_org_unit(
        self, org_unit_uuid: UUID
    ) -> ReadEmployeesWithEngagementToOrgUnitEngagements:
        query = gql(
            """
            query read_employees_with_engagement_to_org_unit($org_unit_uuid: UUID!) {
              engagements(filter: {org_unit: {uuids: [$org_unit_uuid]}}) {
                objects {
                  current {
                    employee_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"org_unit_uuid": org_unit_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEmployeesWithEngagementToOrgUnit.parse_obj(data).engagements

    async def read_engagements(
        self,
        uuids: List[UUID],
        from_date: Union[Optional[datetime], UnsetType] = UNSET,
        to_date: Union[Optional[datetime], UnsetType] = UNSET,
    ) -> ReadEngagementsEngagements:
        query = gql(
            """
            query read_engagements($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              engagements(filter: {uuids: $uuids, from_date: $from_date, to_date: $to_date}) {
                objects {
                  validities {
                    user_key
                    extension_1
                    extension_2
                    extension_3
                    extension_4
                    extension_5
                    extension_6
                    extension_7
                    extension_8
                    extension_9
                    extension_10
                    leave_uuid
                    primary_uuid
                    job_function_uuid
                    org_unit_uuid
                    engagement_type_uuid
                    employee_uuid
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "uuids": uuids,
            "from_date": from_date,
            "to_date": to_date,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagements.parse_obj(data).engagements

    async def read_engagements_by_employee_uuid(
        self, employee_uuid: UUID
    ) -> ReadEngagementsByEmployeeUuidEngagements:
        query = gql(
            """
            query read_engagements_by_employee_uuid($employee_uuid: UUID!) {
              engagements(filter: {employee: {uuids: [$employee_uuid]}}) {
                objects {
                  current {
                    uuid
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"employee_uuid": employee_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementsByEmployeeUuid.parse_obj(data).engagements

    async def read_engagements_by_engagements_filter(
        self, engagements_filter: EngagementFilter
    ) -> ReadEngagementsByEngagementsFilterEngagements:
        query = gql(
            """
            query read_engagements_by_engagements_filter($engagements_filter: EngagementFilter!) {
              engagements(filter: $engagements_filter) {
                objects {
                  current {
                    uuid
                    user_key
                    org_unit_uuid
                    job_function_uuid
                    engagement_type_uuid
                    primary_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"engagements_filter": engagements_filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementsByEngagementsFilter.parse_obj(data).engagements

    async def set_job_title(
        self,
        uuid: UUID,
        from_: datetime,
        to: Union[Optional[datetime], UnsetType] = UNSET,
        job_function: Union[Optional[UUID], UnsetType] = UNSET,
    ) -> SetJobTitleEngagementUpdate:
        query = gql(
            """
            mutation set_job_title($uuid: UUID!, $from: DateTime!, $to: DateTime, $job_function: UUID) {
              engagement_update(
                input: {uuid: $uuid, validity: {from: $from, to: $to}, job_function: $job_function}
              ) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {
            "uuid": uuid,
            "from": from_,
            "to": to,
            "job_function": job_function,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return SetJobTitle.parse_obj(data).engagement_update

    async def read_employee_uuid_by_cpr_number(
        self, cpr_number: CPRNumber
    ) -> ReadEmployeeUuidByCprNumberEmployees:
        query = gql(
            """
            query read_employee_uuid_by_cpr_number($cpr_number: CPR!) {
              employees(filter: {cpr_numbers: [$cpr_number]}) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"cpr_number": cpr_number}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEmployeeUuidByCprNumber.parse_obj(data).employees

    async def read_employees(
        self,
        uuids: List[UUID],
        from_date: Union[Optional[datetime], UnsetType] = UNSET,
        to_date: Union[Optional[datetime], UnsetType] = UNSET,
    ) -> ReadEmployeesEmployees:
        query = gql(
            """
            query read_employees($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              employees(filter: {from_date: $from_date, to_date: $to_date, uuids: $uuids}) {
                objects {
                  validities {
                    uuid
                    cpr_no
                    givenname
                    surname
                    nickname_givenname
                    nickname_surname
                    validity {
                      to
                      from
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "uuids": uuids,
            "from_date": from_date,
            "to_date": to_date,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEmployees.parse_obj(data).employees

    async def read_itusers(
        self,
        uuids: List[UUID],
        from_date: Union[Optional[datetime], UnsetType] = UNSET,
        to_date: Union[Optional[datetime], UnsetType] = UNSET,
    ) -> ReadItusersItusers:
        query = gql(
            """
            query read_itusers($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              itusers(filter: {from_date: $from_date, to_date: $to_date, uuids: $uuids}) {
                objects {
                  validities {
                    user_key
                    validity {
                      from
                      to
                    }
                    employee_uuid
                    itsystem_uuid
                    engagement_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "uuids": uuids,
            "from_date": from_date,
            "to_date": to_date,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadItusers.parse_obj(data).itusers

    async def read_employee_uuid_by_ituser_user_key(
        self, user_key: str
    ) -> ReadEmployeeUuidByItuserUserKeyItusers:
        query = gql(
            """
            query read_employee_uuid_by_ituser_user_key($user_key: String!) {
              itusers(filter: {user_keys: [$user_key]}) {
                objects {
                  current {
                    employee_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"user_key": user_key}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEmployeeUuidByItuserUserKey.parse_obj(data).itusers

    async def read_engagement_uuid_by_ituser_user_key(
        self, user_key: str, itsystem_uuid: UUID
    ) -> ReadEngagementUuidByItuserUserKeyItusers:
        query = gql(
            """
            query read_engagement_uuid_by_ituser_user_key($user_key: String!, $itsystem_uuid: UUID!) {
              itusers(filter: {user_keys: [$user_key], itsystem: {uuids: [$itsystem_uuid]}}) {
                objects {
                  current {
                    engagement_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "user_key": user_key,
            "itsystem_uuid": itsystem_uuid,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementUuidByItuserUserKey.parse_obj(data).itusers

    async def read_ituser_by_employee_and_itsystem_uuid(
        self, employee_uuid: UUID, itsystem_uuid: UUID
    ) -> ReadItuserByEmployeeAndItsystemUuidItusers:
        query = gql(
            """
            query read_ituser_by_employee_and_itsystem_uuid($employee_uuid: UUID!, $itsystem_uuid: UUID!) {
              itusers(
                filter: {employee: {uuids: [$employee_uuid]}, itsystem: {uuids: [$itsystem_uuid]}}
              ) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "employee_uuid": employee_uuid,
            "itsystem_uuid": itsystem_uuid,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadItuserByEmployeeAndItsystemUuid.parse_obj(data).itusers

    async def read_is_primary_engagements(
        self, uuids: List[UUID]
    ) -> ReadIsPrimaryEngagementsEngagements:
        query = gql(
            """
            query read_is_primary_engagements($uuids: [UUID!]!) {
              engagements(filter: {uuids: $uuids}) {
                objects {
                  current {
                    is_primary
                    uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuids": uuids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadIsPrimaryEngagements.parse_obj(data).engagements

    async def read_employee_addresses(
        self, employee_uuid: UUID, address_type_uuid: UUID
    ) -> ReadEmployeeAddressesAddresses:
        query = gql(
            """
            query read_employee_addresses($employee_uuid: UUID!, $address_type_uuid: UUID!) {
              addresses(
                filter: {address_type: {uuids: [$address_type_uuid]}, employee: {uuids: [$employee_uuid]}}
              ) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "employee_uuid": employee_uuid,
            "address_type_uuid": address_type_uuid,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEmployeeAddresses.parse_obj(data).addresses

    async def read_org_unit_addresses(
        self, org_unit_uuid: UUID, address_type_uuid: UUID
    ) -> ReadOrgUnitAddressesAddresses:
        query = gql(
            """
            query read_org_unit_addresses($org_unit_uuid: UUID!, $address_type_uuid: UUID!) {
              addresses(
                filter: {address_type: {uuids: [$address_type_uuid]}, org_unit: {uuids: [$org_unit_uuid]}}
              ) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "org_unit_uuid": org_unit_uuid,
            "address_type_uuid": address_type_uuid,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadOrgUnitAddresses.parse_obj(data).addresses

    async def read_class_uuid_by_facet_and_class_user_key(
        self, facet_user_key: str, class_user_key: str
    ) -> ReadClassUuidByFacetAndClassUserKeyClasses:
        query = gql(
            """
            query read_class_uuid_by_facet_and_class_user_key($facet_user_key: String!, $class_user_key: String!) {
              classes(
                filter: {facet: {user_keys: [$facet_user_key]}, user_keys: [$class_user_key]}
              ) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "facet_user_key": facet_user_key,
            "class_user_key": class_user_key,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadClassUuidByFacetAndClassUserKey.parse_obj(data).classes

    async def read_class_name_by_class_uuid(
        self, class_uuid: UUID
    ) -> ReadClassNameByClassUuidClasses:
        query = gql(
            """
            query read_class_name_by_class_uuid($class_uuid: UUID!) {
              classes(filter: {uuids: [$class_uuid]}) {
                objects {
                  current {
                    name
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"class_uuid": class_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadClassNameByClassUuid.parse_obj(data).classes

    async def org_unit_engagements_refresh(
        self, exchange: str, org_unit_uuid: UUID
    ) -> OrgUnitEngagementsRefreshEngagementRefresh:
        query = gql(
            """
            mutation org_unit_engagements_refresh($exchange: String!, $org_unit_uuid: UUID!) {
              engagement_refresh(
                exchange: $exchange
                filter: {org_unit: {uuids: [$org_unit_uuid]}}
              ) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "org_unit_uuid": org_unit_uuid,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitEngagementsRefresh.parse_obj(data).engagement_refresh

    async def employee_refresh(
        self, exchange: str, uuids: List[UUID]
    ) -> EmployeeRefreshEmployeeRefresh:
        query = gql(
            """
            mutation employee_refresh($exchange: String!, $uuids: [UUID!]!) {
              employee_refresh(exchange: $exchange, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {"exchange": exchange, "uuids": uuids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return EmployeeRefresh.parse_obj(data).employee_refresh

    async def read_addresses(
        self,
        uuids: List[UUID],
        from_date: Union[Optional[datetime], UnsetType] = UNSET,
        to_date: Union[Optional[datetime], UnsetType] = UNSET,
    ) -> ReadAddressesAddresses:
        query = gql(
            """
            query read_addresses($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              addresses(filter: {uuids: $uuids, from_date: $from_date, to_date: $to_date}) {
                objects {
                  validities {
                    value: name
                    value2
                    uuid
                    visibility_uuid
                    employee_uuid
                    org_unit_uuid
                    engagement_uuid
                    person: employee {
                      cpr_no
                    }
                    validity {
                      from
                      to
                    }
                    address_type {
                      user_key
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "uuids": uuids,
            "from_date": from_date,
            "to_date": to_date,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadAddresses.parse_obj(data).addresses

    async def read_itsystems(self) -> ReadItsystemsItsystems:
        query = gql(
            """
            query read_itsystems {
              itsystems {
                objects {
                  current {
                    uuid
                    user_key
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadItsystems.parse_obj(data).itsystems

    async def read_org_units(self) -> ReadOrgUnitsOrgUnits:
        query = gql(
            """
            query read_org_units {
              org_units(filter: {from_date: null, to_date: null}) {
                objects {
                  uuid
                  validities {
                    uuid
                    name
                    user_key
                    parent_uuid
                    validity {
                      to
                      from
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadOrgUnits.parse_obj(data).org_units

    async def read_class_user_keys(
        self, facet_user_keys: List[str]
    ) -> ReadClassUserKeysClasses:
        query = gql(
            """
            query read_class_user_keys($facet_user_keys: [String!]!) {
              classes(filter: {facet: {user_keys: $facet_user_keys}}) {
                objects {
                  current {
                    user_key
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"facet_user_keys": facet_user_keys}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadClassUserKeys.parse_obj(data).classes

    async def read_all_itusers(
        self,
        filter: ITUserFilter,
        cursor: Union[Optional[Any], UnsetType] = UNSET,
        limit: Union[Optional[Any], UnsetType] = UNSET,
    ) -> ReadAllItusersItusers:
        query = gql(
            """
            query read_all_itusers($filter: ITUserFilter!, $cursor: Cursor = null, $limit: int = 100) {
              itusers(limit: $limit, cursor: $cursor, filter: $filter) {
                objects {
                  validities {
                    itsystem_uuid
                    employee_uuid
                    user_key
                  }
                }
                page_info {
                  next_cursor
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "filter": filter,
            "cursor": cursor,
            "limit": limit,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadAllItusers.parse_obj(data).itusers

    async def read_filtered_addresses(
        self, filter: AddressFilter
    ) -> ReadFilteredAddressesAddresses:
        query = gql(
            """
            query read_filtered_addresses($filter: AddressFilter!) {
              addresses(filter: $filter) {
                objects {
                  validities {
                    address_type {
                      user_key
                    }
                    uuid
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadFilteredAddresses.parse_obj(data).addresses

    async def read_filtered_itusers(
        self, filter: ITUserFilter
    ) -> ReadFilteredItusersItusers:
        query = gql(
            """
            query read_filtered_itusers($filter: ITUserFilter!) {
              itusers(filter: $filter) {
                objects {
                  validities {
                    itsystem {
                      user_key
                    }
                    uuid
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadFilteredItusers.parse_obj(data).itusers

    async def read_engagements_is_primary(
        self, filter: EngagementFilter
    ) -> ReadEngagementsIsPrimaryEngagements:
        query = gql(
            """
            query read_engagements_is_primary($filter: EngagementFilter!) {
              engagements(filter: $filter) {
                objects {
                  validities {
                    is_primary
                    uuid
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementsIsPrimary.parse_obj(data).engagements

    async def read_ituser_employee_uuid(
        self, ituser_uuid: UUID
    ) -> ReadItuserEmployeeUuidItusers:
        query = gql(
            """
            query read_ituser_employee_uuid($ituser_uuid: UUID!) {
              itusers(filter: {uuids: [$ituser_uuid]}) {
                objects {
                  current {
                    employee_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"ituser_uuid": ituser_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadItuserEmployeeUuid.parse_obj(data).itusers

    async def read_engagement_employee_uuid(
        self, engagement_uuid: UUID
    ) -> ReadEngagementEmployeeUuidEngagements:
        query = gql(
            """
            query read_engagement_employee_uuid($engagement_uuid: UUID!) {
              engagements(filter: {uuids: [$engagement_uuid]}) {
                objects {
                  current {
                    employee_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"engagement_uuid": engagement_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementEmployeeUuid.parse_obj(data).engagements

    async def read_address_relation_uuids(
        self, address_uuid: UUID
    ) -> ReadAddressRelationUuidsAddresses:
        query = gql(
            """
            query read_address_relation_uuids($address_uuid: UUID!) {
              addresses(filter: {uuids: [$address_uuid]}) {
                objects {
                  current {
                    employee_uuid
                    org_unit_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"address_uuid": address_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadAddressRelationUuids.parse_obj(data).addresses

    async def read_all_ituser_user_keys_by_itsystem_uuid(
        self, itsystem_uuid: UUID
    ) -> ReadAllItuserUserKeysByItsystemUuidItusers:
        query = gql(
            """
            query read_all_ituser_user_keys_by_itsystem_uuid($itsystem_uuid: UUID!) {
              itusers(filter: {itsystem: {uuids: [$itsystem_uuid]}}) {
                objects {
                  validities {
                    user_key
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"itsystem_uuid": itsystem_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadAllItuserUserKeysByItsystemUuid.parse_obj(data).itusers
