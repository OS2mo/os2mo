from datetime import datetime
from typing import Any
from uuid import UUID

from ..types import CPRNumber
from ._testing__address_read import TestingAddressRead
from ._testing__address_read import TestingAddressReadAddresses
from ._testing__employee_read import TestingEmployeeRead
from ._testing__employee_read import TestingEmployeeReadEmployees
from ._testing__engagement_read import TestingEngagementRead
from ._testing__engagement_read import TestingEngagementReadEngagements
from ._testing__itsystem_create import TestingItsystemCreate
from ._testing__itsystem_create import TestingItsystemCreateItsystemCreate
from ._testing__ituser_read import TestingItuserRead
from ._testing__ituser_read import TestingItuserReadItusers
from ._testing__manager_create import TestingManagerCreate
from ._testing__manager_create import TestingManagerCreateManagerCreate
from .address_create import AddressCreate
from .address_create import AddressCreateAddressCreate
from .address_terminate import AddressTerminate
from .address_terminate import AddressTerminateAddressTerminate
from .address_update import AddressUpdate
from .address_update import AddressUpdateAddressUpdate
from .async_base_client import AsyncBaseClient
from .base_model import UNSET
from .base_model import UnsetType
from .class_create import ClassCreate
from .class_create import ClassCreateClassCreate
from .employee_refresh import EmployeeRefresh
from .employee_refresh import EmployeeRefreshEmployeeRefresh
from .engagement_create import EngagementCreate
from .engagement_create import EngagementCreateEngagementCreate
from .engagement_terminate import EngagementTerminate
from .engagement_terminate import EngagementTerminateEngagementTerminate
from .engagement_update import EngagementUpdate
from .engagement_update import EngagementUpdateEngagementUpdate
from .input_types import AddressCreateInput
from .input_types import AddressFilter
from .input_types import AddressTerminateInput
from .input_types import AddressUpdateInput
from .input_types import ClassCreateInput
from .input_types import EmployeeCreateInput
from .input_types import EmployeeFilter
from .input_types import EmployeeUpdateInput
from .input_types import EngagementCreateInput
from .input_types import EngagementFilter
from .input_types import EngagementTerminateInput
from .input_types import EngagementUpdateInput
from .input_types import ITSystemCreateInput
from .input_types import ITUserCreateInput
from .input_types import ITUserFilter
from .input_types import ITUserTerminateInput
from .input_types import ITUserUpdateInput
from .input_types import ManagerCreateInput
from .input_types import OrganisationUnitCreateInput
from .input_types import OrgUnitsboundmanagerfilter
from .ituser_create import ItuserCreate
from .ituser_create import ItuserCreateItuserCreate
from .ituser_terminate import ItuserTerminate
from .ituser_terminate import ItuserTerminateItuserTerminate
from .ituser_update import ItuserUpdate
from .ituser_update import ItuserUpdateItuserUpdate
from .org_unit_create import OrgUnitCreate
from .org_unit_create import OrgUnitCreateOrgUnitCreate
from .org_unit_engagements_refresh import OrgUnitEngagementsRefresh
from .org_unit_engagements_refresh import OrgUnitEngagementsRefreshEngagementRefresh
from .org_unit_refresh import OrgUnitRefresh
from .org_unit_refresh import OrgUnitRefreshOrgUnitRefresh
from .read_address_relation_uuids import ReadAddressRelationUuids
from .read_address_relation_uuids import ReadAddressRelationUuidsAddresses
from .read_address_uuid import ReadAddressUuid
from .read_address_uuid import ReadAddressUuidAddresses
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
from .read_class_uuid import ReadClassUuid
from .read_class_uuid import ReadClassUuidClasses
from .read_class_uuid_by_facet_and_class_user_key import (
    ReadClassUuidByFacetAndClassUserKey,
)
from .read_class_uuid_by_facet_and_class_user_key import (
    ReadClassUuidByFacetAndClassUserKeyClasses,
)
from .read_cleanup_addresses import ReadCleanupAddresses
from .read_cleanup_addresses import ReadCleanupAddressesAddresses
from .read_employee_registrations import ReadEmployeeRegistrations
from .read_employee_registrations import ReadEmployeeRegistrationsEmployees
from .read_employee_uuid_by_cpr_number import ReadEmployeeUuidByCprNumber
from .read_employee_uuid_by_cpr_number import ReadEmployeeUuidByCprNumberEmployees
from .read_employee_uuid_by_ituser_user_key import ReadEmployeeUuidByItuserUserKey
from .read_employee_uuid_by_ituser_user_key import (
    ReadEmployeeUuidByItuserUserKeyItusers,
)
from .read_employees import ReadEmployees
from .read_employees import ReadEmployeesEmployees
from .read_engagement_employee_uuid import ReadEngagementEmployeeUuid
from .read_engagement_employee_uuid import ReadEngagementEmployeeUuidEngagements
from .read_engagement_enddate import ReadEngagementEnddate
from .read_engagement_enddate import ReadEngagementEnddateEngagements
from .read_engagement_manager import ReadEngagementManager
from .read_engagement_manager import ReadEngagementManagerEngagements
from .read_engagement_uuid import ReadEngagementUuid
from .read_engagement_uuid import ReadEngagementUuidEngagements
from .read_engagements import ReadEngagements
from .read_engagements import ReadEngagementsEngagements
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuid
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuidEngagements
from .read_engagements_is_primary import ReadEngagementsIsPrimary
from .read_engagements_is_primary import ReadEngagementsIsPrimaryEngagements
from .read_facet_uuid import ReadFacetUuid
from .read_facet_uuid import ReadFacetUuidFacets
from .read_filtered_addresses import ReadFilteredAddresses
from .read_filtered_addresses import ReadFilteredAddressesAddresses
from .read_filtered_itusers import ReadFilteredItusers
from .read_filtered_itusers import ReadFilteredItusersItusers
from .read_itsystem_uuid import ReadItsystemUuid
from .read_itsystem_uuid import ReadItsystemUuidItsystems
from .read_ituser_by_employee_and_itsystem_uuid import (
    ReadItuserByEmployeeAndItsystemUuid,
)
from .read_ituser_by_employee_and_itsystem_uuid import (
    ReadItuserByEmployeeAndItsystemUuidItusers,
)
from .read_ituser_relation_uuids import ReadItuserRelationUuids
from .read_ituser_relation_uuids import ReadItuserRelationUuidsItusers
from .read_ituser_uuid import ReadItuserUuid
from .read_ituser_uuid import ReadItuserUuidItusers
from .read_itusers import ReadItusers
from .read_itusers import ReadItusersItusers
from .read_org_unit_ancestor_names import ReadOrgUnitAncestorNames
from .read_org_unit_ancestor_names import ReadOrgUnitAncestorNamesOrgUnits
from .read_org_unit_ancestors import ReadOrgUnitAncestors
from .read_org_unit_ancestors import ReadOrgUnitAncestorsOrgUnits
from .read_org_unit_name import ReadOrgUnitName
from .read_org_unit_name import ReadOrgUnitNameOrgUnits
from .read_person_uuid import ReadPersonUuid
from .read_person_uuid import ReadPersonUuidEmployees
from .set_job_title import SetJobTitle
from .set_job_title import SetJobTitleEngagementUpdate
from .user_create import UserCreate
from .user_create import UserCreateEmployeeCreate
from .user_update import UserUpdate
from .user_update import UserUpdateEmployeeUpdate


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):
    async def _testing__address_read(
        self, filter: AddressFilter | None | UnsetType = UNSET
    ) -> TestingAddressReadAddresses:
        query = gql(
            """
            query __testing__address_read($filter: AddressFilter) {
              addresses(filter: $filter) {
                objects {
                  validities {
                    uuid
                    user_key
                    address_type {
                      user_key
                    }
                    value
                    value2
                    person {
                      uuid
                    }
                    visibility {
                      user_key
                    }
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
        return TestingAddressRead.parse_obj(data).addresses

    async def _testing__engagement_read(
        self, filter: EngagementFilter | None | UnsetType = UNSET
    ) -> TestingEngagementReadEngagements:
        query = gql(
            """
            query __testing__engagement_read($filter: EngagementFilter) {
              engagements(filter: $filter) {
                objects {
                  validities {
                    uuid
                    user_key
                    person {
                      uuid
                    }
                    org_unit {
                      uuid
                    }
                    engagement_type {
                      user_key
                    }
                    job_function {
                      user_key
                    }
                    primary {
                      user_key
                    }
                    extension_1
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
        return TestingEngagementRead.parse_obj(data).engagements

    async def _testing__employee_read(
        self, filter: EmployeeFilter | None | UnsetType = UNSET
    ) -> TestingEmployeeReadEmployees:
        query = gql(
            """
            query __testing__employee_read($filter: EmployeeFilter) {
              employees(filter: $filter) {
                objects {
                  validities {
                    uuid
                    user_key
                    cpr_number
                    given_name
                    surname
                    nickname_given_name
                    nickname_surname
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingEmployeeRead.parse_obj(data).employees

    async def _testing__ituser_read(
        self, filter: ITUserFilter | None | UnsetType = UNSET
    ) -> TestingItuserReadItusers:
        query = gql(
            """
            query __testing__ituser_read($filter: ITUserFilter) {
              itusers(filter: $filter) {
                objects {
                  validities {
                    uuid
                    user_key
                    itsystem {
                      user_key
                    }
                    person {
                      uuid
                    }
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
        return TestingItuserRead.parse_obj(data).itusers

    async def _testing__itsystem_create(
        self, input: ITSystemCreateInput
    ) -> TestingItsystemCreateItsystemCreate:
        query = gql(
            """
            mutation __testing__itsystem_create($input: ITSystemCreateInput!) {
              itsystem_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingItsystemCreate.parse_obj(data).itsystem_create

    async def _testing__manager_create(
        self, input: ManagerCreateInput
    ) -> TestingManagerCreateManagerCreate:
        query = gql(
            """
            mutation __testing__manager_create($input: ManagerCreateInput!) {
              manager_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingManagerCreate.parse_obj(data).manager_create

    async def address_create(
        self, input: AddressCreateInput
    ) -> AddressCreateAddressCreate:
        query = gql(
            """
            mutation address_create($input: AddressCreateInput!) {
              address_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AddressCreate.parse_obj(data).address_create

    async def address_update(
        self, input: AddressUpdateInput
    ) -> AddressUpdateAddressUpdate:
        query = gql(
            """
            mutation address_update($input: AddressUpdateInput!) {
              address_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AddressUpdate.parse_obj(data).address_update

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

    async def user_create(self, input: EmployeeCreateInput) -> UserCreateEmployeeCreate:
        query = gql(
            """
            mutation user_create($input: EmployeeCreateInput!) {
              employee_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UserCreate.parse_obj(data).employee_create

    async def user_update(self, input: EmployeeUpdateInput) -> UserUpdateEmployeeUpdate:
        query = gql(
            """
            mutation user_update($input: EmployeeUpdateInput!) {
              employee_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return UserUpdate.parse_obj(data).employee_update

    async def engagement_create(
        self, input: EngagementCreateInput
    ) -> EngagementCreateEngagementCreate:
        query = gql(
            """
            mutation engagement_create($input: EngagementCreateInput!) {
              engagement_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return EngagementCreate.parse_obj(data).engagement_create

    async def engagement_update(
        self, input: EngagementUpdateInput
    ) -> EngagementUpdateEngagementUpdate:
        query = gql(
            """
            mutation engagement_update($input: EngagementUpdateInput!) {
              engagement_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return EngagementUpdate.parse_obj(data).engagement_update

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

    async def ituser_create(self, input: ITUserCreateInput) -> ItuserCreateItuserCreate:
        query = gql(
            """
            mutation ituser_create($input: ITUserCreateInput!) {
              ituser_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItuserCreate.parse_obj(data).ituser_create

    async def ituser_update(self, input: ITUserUpdateInput) -> ItuserUpdateItuserUpdate:
        query = gql(
            """
            mutation ituser_update($input: ITUserUpdateInput!) {
              ituser_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItuserUpdate.parse_obj(data).ituser_update

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

    async def org_unit_create(
        self, input: OrganisationUnitCreateInput
    ) -> OrgUnitCreateOrgUnitCreate:
        query = gql(
            """
            mutation org_unit_create($input: OrganisationUnitCreateInput!) {
              org_unit_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitCreate.parse_obj(data).org_unit_create

    async def read_engagements(
        self,
        uuids: list[UUID],
        from_date: datetime | None | UnsetType = UNSET,
        to_date: datetime | None | UnsetType = UNSET,
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

    async def set_job_title(
        self,
        uuid: UUID,
        from_: datetime,
        to: datetime | None | UnsetType = UNSET,
        job_function: UUID | None | UnsetType = UNSET,
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
        uuids: list[UUID],
        from_date: datetime | None | UnsetType = UNSET,
        to_date: datetime | None | UnsetType = UNSET,
    ) -> ReadEmployeesEmployees:
        query = gql(
            """
            query read_employees($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              employees(filter: {from_date: $from_date, to_date: $to_date, uuids: $uuids}) {
                objects {
                  validities {
                    uuid
                    cpr_number
                    given_name
                    surname
                    nickname_given_name
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
        uuids: list[UUID],
        from_date: datetime | None | UnsetType = UNSET,
        to_date: datetime | None | UnsetType = UNSET,
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
                filter: {org_unit: {uuids: [$org_unit_uuid]}, from_date: null, to_date: null}
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
        self, exchange: str, uuids: list[UUID]
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

    async def org_unit_refresh(
        self, exchange: str, uuids: list[UUID]
    ) -> OrgUnitRefreshOrgUnitRefresh:
        query = gql(
            """
            mutation org_unit_refresh($exchange: String!, $uuids: [UUID!]!) {
              org_unit_refresh(exchange: $exchange, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {"exchange": exchange, "uuids": uuids}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitRefresh.parse_obj(data).org_unit_refresh

    async def read_addresses(
        self,
        uuids: list[UUID],
        from_date: datetime | None | UnsetType = UNSET,
        to_date: datetime | None | UnsetType = UNSET,
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
                      cpr_number
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

    async def read_all_itusers(
        self,
        filter: ITUserFilter,
        cursor: Any | None | UnsetType = UNSET,
        limit: Any | None | UnsetType = UNSET,
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
                    uuid
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

    async def read_ituser_relation_uuids(
        self, ituser_uuid: UUID
    ) -> ReadItuserRelationUuidsItusers:
        query = gql(
            """
            query read_ituser_relation_uuids($ituser_uuid: UUID!) {
              itusers(filter: {uuids: [$ituser_uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
                    employee_uuid
                    org_unit_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"ituser_uuid": ituser_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadItuserRelationUuids.parse_obj(data).itusers

    async def read_engagement_employee_uuid(
        self, engagement_uuid: UUID
    ) -> ReadEngagementEmployeeUuidEngagements:
        query = gql(
            """
            query read_engagement_employee_uuid($engagement_uuid: UUID!) {
              engagements(filter: {uuids: [$engagement_uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
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
              addresses(filter: {uuids: [$address_uuid], from_date: null, to_date: null}) {
                objects {
                  validities {
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
              itusers(
                filter: {itsystem: {uuids: [$itsystem_uuid]}, from_date: null, to_date: null}
              ) {
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

    async def read_org_unit_name(self, org_unit_uuid: UUID) -> ReadOrgUnitNameOrgUnits:
        query = gql(
            """
            query read_org_unit_name($org_unit_uuid: UUID!) {
              org_units(filter: {uuids: [$org_unit_uuid]}) {
                objects {
                  current {
                    name
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"org_unit_uuid": org_unit_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadOrgUnitName.parse_obj(data).org_units

    async def read_itsystem_uuid(self, user_key: str) -> ReadItsystemUuidItsystems:
        query = gql(
            """
            query read_itsystem_uuid($user_key: String!) {
              itsystems(filter: {user_keys: [$user_key]}) {
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
        return ReadItsystemUuid.parse_obj(data).itsystems

    async def read_org_unit_ancestor_names(
        self, uuid: UUID
    ) -> ReadOrgUnitAncestorNamesOrgUnits:
        query = gql(
            """
            query read_org_unit_ancestor_names($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    name
                    ancestors {
                      name
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadOrgUnitAncestorNames.parse_obj(data).org_units

    async def read_address_uuid(
        self, filter: AddressFilter
    ) -> ReadAddressUuidAddresses:
        query = gql(
            """
            query read_address_uuid($filter: AddressFilter!) {
              addresses(filter: $filter) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadAddressUuid.parse_obj(data).addresses

    async def read_ituser_uuid(self, filter: ITUserFilter) -> ReadItuserUuidItusers:
        query = gql(
            """
            query read_ituser_uuid($filter: ITUserFilter!) {
              itusers(filter: $filter) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadItuserUuid.parse_obj(data).itusers

    async def read_engagement_uuid(
        self, filter: EngagementFilter
    ) -> ReadEngagementUuidEngagements:
        query = gql(
            """
            query read_engagement_uuid($filter: EngagementFilter!) {
              engagements(filter: $filter) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementUuid.parse_obj(data).engagements

    async def read_person_uuid(
        self, filter: EmployeeFilter | None | UnsetType = UNSET
    ) -> ReadPersonUuidEmployees:
        query = gql(
            """
            query read_person_uuid($filter: EmployeeFilter) {
              employees(filter: $filter) {
                objects {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadPersonUuid.parse_obj(data).employees

    async def read_engagement_enddate(
        self, employee_uuid: UUID
    ) -> ReadEngagementEnddateEngagements:
        query = gql(
            """
            query read_engagement_enddate($employee_uuid: UUID!) {
              engagements(
                filter: {employee: {uuids: [$employee_uuid]}, from_date: null, to_date: null}
              ) {
                objects {
                  validities {
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
        return ReadEngagementEnddate.parse_obj(data).engagements

    async def read_org_unit_ancestors(self, uuid: UUID) -> ReadOrgUnitAncestorsOrgUnits:
        query = gql(
            """
            query read_org_unit_ancestors($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid]}) {
                objects {
                  current {
                    ancestors {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"uuid": uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadOrgUnitAncestors.parse_obj(data).org_units

    async def read_engagement_manager(
        self,
        engagement_uuid: UUID,
        filter: OrgUnitsboundmanagerfilter | None | UnsetType = UNSET,
    ) -> ReadEngagementManagerEngagements:
        query = gql(
            """
            query read_engagement_manager($engagement_uuid: UUID!, $filter: OrgUnitsboundmanagerfilter) {
              engagements(filter: {uuids: [$engagement_uuid]}) {
                objects {
                  current {
                    managers(filter: $filter, inherit: true, exclude_self: true) {
                      person {
                        uuid
                      }
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {
            "engagement_uuid": engagement_uuid,
            "filter": filter,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementManager.parse_obj(data).engagements

    async def read_cleanup_addresses(
        self, filter: AddressFilter | None | UnsetType = UNSET
    ) -> ReadCleanupAddressesAddresses:
        query = gql(
            """
            query read_cleanup_addresses($filter: AddressFilter) {
              addresses(filter: $filter) {
                objects {
                  current {
                    employee_uuid
                    uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadCleanupAddresses.parse_obj(data).addresses

    async def read_employee_registrations(
        self, employee_uuid: UUID
    ) -> ReadEmployeeRegistrationsEmployees:
        query = gql(
            """
            query read_employee_registrations($employee_uuid: UUID!) {
              employees(filter: {uuids: [$employee_uuid]}) {
                objects {
                  registrations {
                    uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"employee_uuid": employee_uuid}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEmployeeRegistrations.parse_obj(data).employees
