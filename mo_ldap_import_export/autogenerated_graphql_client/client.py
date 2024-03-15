from uuid import UUID

from .address_terminate import AddressTerminate
from .address_terminate import AddressTerminateAddressTerminate
from .async_base_client import AsyncBaseClient
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
from .read_class_uuid import ReadClassUuid
from .read_class_uuid import ReadClassUuidClasses
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnit,
)
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnitEngagements,
)
from .read_facet_uuid import ReadFacetUuid
from .read_facet_uuid import ReadFacetUuidFacets
from .read_root_org_uuid import ReadRootOrgUuid
from .read_root_org_uuid import ReadRootOrgUuidOrg


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
