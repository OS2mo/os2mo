from datetime import datetime
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from .address_terminate import AddressTerminate
from .address_terminate import AddressTerminateAddressTerminate
from .async_base_client import AsyncBaseClient
from .base_model import UNSET
from .base_model import UnsetType
from .class_create import ClassCreate
from .class_create import ClassCreateClassCreate
from .class_update import ClassUpdate
from .class_update import ClassUpdateClassUpdate
from .engagement_terminate import EngagementTerminate
from .engagement_terminate import EngagementTerminateEngagementTerminate
from .input_types import AddressTerminateInput
from .input_types import ClassCreateInput
from .input_types import ClassUpdateInput
from .input_types import EngagementTerminateInput
from .input_types import ITSystemCreateInput
from .input_types import ITUserTerminateInput
from .itsystem_create import ItsystemCreate
from .itsystem_create import ItsystemCreateItsystemCreate
from .ituser_terminate import ItuserTerminate
from .ituser_terminate import ItuserTerminateItuserTerminate
from .read_class_name_by_class_uuid import ReadClassNameByClassUuid
from .read_class_name_by_class_uuid import ReadClassNameByClassUuidClasses
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
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnit,
)
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnitEngagements,
)
from .read_engagement_org_unit_uuid import ReadEngagementOrgUnitUuid
from .read_engagement_org_unit_uuid import ReadEngagementOrgUnitUuidEngagements
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuid
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuidEngagements
from .read_facet_classes import ReadFacetClasses
from .read_facet_classes import ReadFacetClassesClasses
from .read_facet_uuid import ReadFacetUuid
from .read_facet_uuid import ReadFacetUuidFacets
from .read_is_primary_engagements import ReadIsPrimaryEngagements
from .read_is_primary_engagements import ReadIsPrimaryEngagementsEngagements
from .read_root_org_uuid import ReadRootOrgUuid
from .read_root_org_uuid import ReadRootOrgUuidOrg
from .set_job_title import SetJobTitle
from .set_job_title import SetJobTitleEngagementUpdate


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):
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
        self, cpr_number: str
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

    async def read_engagement_org_unit_uuid(
        self, engagement_uuid: UUID
    ) -> ReadEngagementOrgUnitUuidEngagements:
        query = gql(
            """
            query read_engagement_org_unit_uuid($engagement_uuid: UUID!) {
              engagements(filter: {uuids: [$engagement_uuid]}) {
                objects {
                  current {
                    org_unit_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"engagement_uuid": engagement_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementOrgUnitUuid.parse_obj(data).engagements

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
              classes(filter: {uuids: [$uuids]}) {
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
