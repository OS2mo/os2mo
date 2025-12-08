from datetime import datetime
from typing import Any
from uuid import UUID

from ..types import CPRNumber
from ._testing__address_read import TestingAddressRead
from ._testing__address_read import TestingAddressReadAddresses
from ._testing__class_read import TestingClassRead
from ._testing__class_read import TestingClassReadClasses
from ._testing__employee_read import TestingEmployeeRead
from ._testing__employee_read import TestingEmployeeReadEmployees
from ._testing__engagement_read import TestingEngagementRead
from ._testing__engagement_read import TestingEngagementReadEngagements
from ._testing__itsystem_create import TestingItsystemCreate
from ._testing__itsystem_create import TestingItsystemCreateItsystemCreate
from ._testing__itsystem_read import TestingItsystemRead
from ._testing__itsystem_read import TestingItsystemReadItsystems
from ._testing__ituser_read import TestingItuserRead
from ._testing__ituser_read import TestingItuserReadItusers
from ._testing__manager_create import TestingManagerCreate
from ._testing__manager_create import TestingManagerCreateManagerCreate
from ._testing__org_unit_read import TestingOrgUnitRead
from ._testing__org_unit_read import TestingOrgUnitReadOrgUnits
from ._testing__person_update import TestingPersonUpdate
from ._testing__person_update import TestingPersonUpdateEmployeeUpdate
from ._testing__rolebinding_create import TestingRolebindingCreate
from ._testing__rolebinding_create import TestingRolebindingCreateRolebindingCreate
from .acknowledge_event import AcknowledgeEvent
from .address_create import AddressCreate
from .address_create import AddressCreateAddressCreate
from .address_refresh import AddressRefresh
from .address_refresh import AddressRefreshAddressRefresh
from .address_terminate import AddressTerminate
from .address_terminate import AddressTerminateAddressTerminate
from .address_update import AddressUpdate
from .address_update import AddressUpdateAddressUpdate
from .addresses import Addresses
from .addresses import AddressesAddresses
from .association_refresh import AssociationRefresh
from .association_refresh import AssociationRefreshAssociationRefresh
from .async_base_client import AsyncBaseClient
from .base_model import UNSET
from .base_model import UnsetType
from .class_create import ClassCreate
from .class_create import ClassCreateClassCreate
from .class_refresh import ClassRefresh
from .class_refresh import ClassRefreshClassRefresh
from .class_terminate import ClassTerminate
from .class_terminate import ClassTerminateClassTerminate
from .class_update import ClassUpdate
from .class_update import ClassUpdateClassUpdate
from .declare_event_listener import DeclareEventListener
from .declare_event_listener import DeclareEventListenerEventListenerDeclare
from .engagement_create import EngagementCreate
from .engagement_create import EngagementCreateEngagementCreate
from .engagement_refresh import EngagementRefresh
from .engagement_refresh import EngagementRefreshEngagementRefresh
from .engagement_terminate import EngagementTerminate
from .engagement_terminate import EngagementTerminateEngagementTerminate
from .engagement_update import EngagementUpdate
from .engagement_update import EngagementUpdateEngagementUpdate
from .facet_refresh import FacetRefresh
from .facet_refresh import FacetRefreshFacetRefresh
from .fetch_event import FetchEvent
from .fetch_event import FetchEventEventFetch
from .get_event_namespaces import GetEventNamespaces
from .get_event_namespaces import GetEventNamespacesEventNamespaces
from .input_types import AddressCreateInput
from .input_types import AddressFilter
from .input_types import AddressTerminateInput
from .input_types import AddressUpdateInput
from .input_types import ClassCreateInput
from .input_types import ClassFilter
from .input_types import ClassTerminateInput
from .input_types import ClassUpdateInput
from .input_types import EmployeeCreateInput
from .input_types import EmployeeFilter
from .input_types import EmployeeUpdateInput
from .input_types import EngagementCreateInput
from .input_types import EngagementFilter
from .input_types import EngagementTerminateInput
from .input_types import EngagementUpdateInput
from .input_types import EventSendInput
from .input_types import FacetFilter
from .input_types import ITSystemCreateInput
from .input_types import ITSystemFilter
from .input_types import ITSystemTerminateInput
from .input_types import ITSystemUpdateInput
from .input_types import ITUserCreateInput
from .input_types import ITUserFilter
from .input_types import ITUserTerminateInput
from .input_types import ITUserUpdateInput
from .input_types import ListenerCreateInput
from .input_types import ManagerCreateInput
from .input_types import ManagerFilter
from .input_types import NamespaceFilter
from .input_types import OrganisationUnitCreateInput
from .input_types import OrganisationUnitFilter
from .input_types import OrganisationUnitTerminateInput
from .input_types import OrganisationUnitUpdateInput
from .input_types import OrgUnitsboundmanagerfilter
from .input_types import RoleBindingCreateInput
from .input_types import RoleBindingFilter
from .itsystem_create import ItsystemCreate
from .itsystem_create import ItsystemCreateItsystemCreate
from .itsystem_refresh import ItsystemRefresh
from .itsystem_refresh import ItsystemRefreshItsystemRefresh
from .itsystem_terminate import ItsystemTerminate
from .itsystem_terminate import ItsystemTerminateItsystemTerminate
from .itsystem_update import ItsystemUpdate
from .itsystem_update import ItsystemUpdateItsystemUpdate
from .ituser_create import ItuserCreate
from .ituser_create import ItuserCreateItuserCreate
from .ituser_refresh import ItuserRefresh
from .ituser_refresh import ItuserRefreshItuserRefresh
from .ituser_terminate import ItuserTerminate
from .ituser_terminate import ItuserTerminateItuserTerminate
from .ituser_update import ItuserUpdate
from .ituser_update import ItuserUpdateItuserUpdate
from .itusers import Itusers
from .itusers import ItusersItusers
from .kle_refresh import KleRefresh
from .kle_refresh import KleRefreshKleRefresh
from .leave_refresh import LeaveRefresh
from .leave_refresh import LeaveRefreshLeaveRefresh
from .list_events import ListEvents
from .list_events import ListEventsEvents
from .manager_refresh import ManagerRefresh
from .manager_refresh import ManagerRefreshManagerRefresh
from .org_unit_create import OrgUnitCreate
from .org_unit_create import OrgUnitCreateOrgUnitCreate
from .org_unit_engagements_refresh import OrgUnitEngagementsRefresh
from .org_unit_engagements_refresh import OrgUnitEngagementsRefreshEngagementRefresh
from .org_unit_refresh import OrgUnitRefresh
from .org_unit_refresh import OrgUnitRefreshOrgUnitRefresh
from .org_unit_terminate import OrgUnitTerminate
from .org_unit_terminate import OrgUnitTerminateOrgUnitTerminate
from .org_unit_update import OrgUnitUpdate
from .org_unit_update import OrgUnitUpdateOrgUnitUpdate
from .owner_refresh import OwnerRefresh
from .owner_refresh import OwnerRefreshOwnerRefresh
from .person_create import PersonCreate
from .person_create import PersonCreateEmployeeCreate
from .person_refresh import PersonRefresh
from .person_refresh import PersonRefreshEmployeeRefresh
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
from .read_classes import ReadClasses
from .read_classes import ReadClassesClasses
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
from .read_engagement_uuids import ReadEngagementUuids
from .read_engagement_uuids import ReadEngagementUuidsEngagements
from .read_engagements import ReadEngagements
from .read_engagements import ReadEngagementsEngagements
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
from .read_itsystems import ReadItsystems
from .read_itsystems import ReadItsystemsItsystems
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
from .read_manager_person_uuid import ReadManagerPersonUuid
from .read_manager_person_uuid import ReadManagerPersonUuidManagers
from .read_org_unit_ancestor_names import ReadOrgUnitAncestorNames
from .read_org_unit_ancestor_names import ReadOrgUnitAncestorNamesOrgUnits
from .read_org_unit_ancestors import ReadOrgUnitAncestors
from .read_org_unit_ancestors import ReadOrgUnitAncestorsOrgUnits
from .read_org_unit_name import ReadOrgUnitName
from .read_org_unit_name import ReadOrgUnitNameOrgUnits
from .read_org_unit_uuid import ReadOrgUnitUuid
from .read_org_unit_uuid import ReadOrgUnitUuidOrgUnits
from .read_org_units import ReadOrgUnits
from .read_org_units import ReadOrgUnitsOrgUnits
from .read_person_uuid import ReadPersonUuid
from .read_person_uuid import ReadPersonUuidEmployees
from .read_rolebindings import ReadRolebindings
from .read_rolebindings import ReadRolebindingsRolebindings
from .related_unit_refresh import RelatedUnitRefresh
from .related_unit_refresh import RelatedUnitRefreshRelatedUnitRefresh
from .resolve_dar_address import ResolveDarAddress
from .resolve_dar_address import ResolveDarAddressAddresses
from .rolebinding_refresh import RolebindingRefresh
from .rolebinding_refresh import RolebindingRefreshRolebindingRefresh
from .send_event import SendEvent
from .set_job_title import SetJobTitle
from .set_job_title import SetJobTitleEngagementUpdate
from .who_am_i import WhoAmI
from .who_am_i import WhoAmIMe


def gql(q: str) -> str:
    return q


class GraphQLClient(AsyncBaseClient):
    async def get_event_namespaces(
        self, filter: NamespaceFilter | None | UnsetType = UNSET
    ) -> GetEventNamespacesEventNamespaces:
        query = gql(
            """
            query get_event_namespaces($filter: NamespaceFilter) {
              event_namespaces(filter: $filter) {
                objects {
                  name
                  owner
                  public
                  listeners {
                    owner
                    routing_key
                    user_key
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
        return GetEventNamespaces.parse_obj(data).event_namespaces

    async def send_event(self, input: EventSendInput) -> bool:
        query = gql(
            """
            mutation send_event($input: EventSendInput!) {
              event_send(input: $input)
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return SendEvent.parse_obj(data).event_send

    async def declare_event_listener(
        self, input: ListenerCreateInput
    ) -> DeclareEventListenerEventListenerDeclare:
        query = gql(
            """
            mutation declare_event_listener($input: ListenerCreateInput!) {
              event_listener_declare(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return DeclareEventListener.parse_obj(data).event_listener_declare

    async def list_events(self, listener: UUID) -> ListEventsEvents:
        query = gql(
            """
            query list_events($listener: UUID!) {
              events(filter: {listeners: {uuids: [$listener]}}) {
                objects {
                  subject
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"listener": listener}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ListEvents.parse_obj(data).events

    async def fetch_event(self, listener: UUID) -> FetchEventEventFetch | None:
        query = gql(
            """
            query fetch_event($listener: UUID!) {
              event_fetch(filter: {listener: $listener}) {
                token
                subject
              }
            }
            """
        )
        variables: dict[str, object] = {"listener": listener}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return FetchEvent.parse_obj(data).event_fetch

    async def acknowledge_event(self, token: Any) -> bool:
        query = gql(
            """
            mutation acknowledge_event($token: EventToken!) {
              event_acknowledge(input: {token: $token})
            }
            """
        )
        variables: dict[str, object] = {"token": token}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AcknowledgeEvent.parse_obj(data).event_acknowledge

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

    async def class_terminate(
        self, input: ClassTerminateInput
    ) -> ClassTerminateClassTerminate:
        query = gql(
            """
            mutation class_terminate($input: ClassTerminateInput!) {
              class_terminate(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ClassTerminate.parse_obj(data).class_terminate

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

    async def itsystem_update(
        self, input: ITSystemUpdateInput
    ) -> ItsystemUpdateItsystemUpdate:
        query = gql(
            """
            mutation itsystem_update($input: ITSystemUpdateInput!) {
              itsystem_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItsystemUpdate.parse_obj(data).itsystem_update

    async def itsystem_terminate(
        self, input: ITSystemTerminateInput
    ) -> ItsystemTerminateItsystemTerminate:
        query = gql(
            """
            mutation itsystem_terminate($input: ITSystemTerminateInput!) {
              itsystem_terminate(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItsystemTerminate.parse_obj(data).itsystem_terminate

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

    async def org_unit_update(
        self, input: OrganisationUnitUpdateInput
    ) -> OrgUnitUpdateOrgUnitUpdate:
        query = gql(
            """
            mutation org_unit_update($input: OrganisationUnitUpdateInput!) {
              org_unit_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitUpdate.parse_obj(data).org_unit_update

    async def org_unit_terminate(
        self, input: OrganisationUnitTerminateInput
    ) -> OrgUnitTerminateOrgUnitTerminate:
        query = gql(
            """
            mutation org_unit_terminate($input: OrganisationUnitTerminateInput!) {
              org_unit_terminate(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitTerminate.parse_obj(data).org_unit_terminate

    async def person_create(
        self, input: EmployeeCreateInput
    ) -> PersonCreateEmployeeCreate:
        query = gql(
            """
            mutation person_create($input: EmployeeCreateInput!) {
              employee_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return PersonCreate.parse_obj(data).employee_create

    async def who_am_i(self) -> WhoAmIMe:
        query = gql(
            """
            query WhoAmI {
              me {
                actor {
                  uuid
                }
              }
            }
            """
        )
        variables: dict[str, object] = {}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return WhoAmI.parse_obj(data).me

    async def read_facet_uuid(self, filter: FacetFilter) -> ReadFacetUuidFacets:
        query = gql(
            """
            query read_facet_uuid($filter: FacetFilter!) {
              facets(filter: $filter) {
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
        return ReadFacetUuid.parse_obj(data).facets

    async def read_class_uuid(self, filter: ClassFilter) -> ReadClassUuidClasses:
        query = gql(
            """
            query read_class_uuid($filter: ClassFilter!) {
              classes(filter: $filter) {
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
        return ReadClassUuid.parse_obj(data).classes

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
                    fraction
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

    async def read_engagement_uuids(
        self, engagement_filter: EngagementFilter
    ) -> ReadEngagementUuidsEngagements:
        query = gql(
            """
            query read_engagement_uuids($engagement_filter: EngagementFilter!) {
              engagements(filter: $engagement_filter) {
                objects {
                  uuid
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
        variables: dict[str, object] = {"engagement_filter": engagement_filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadEngagementUuids.parse_obj(data).engagements

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
                    user_key
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

    async def read_org_units(
        self,
        uuids: list[UUID],
        from_date: datetime | None | UnsetType = UNSET,
        to_date: datetime | None | UnsetType = UNSET,
    ) -> ReadOrgUnitsOrgUnits:
        query = gql(
            """
            query read_org_units($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              org_units(filter: {from_date: $from_date, to_date: $to_date, uuids: $uuids}) {
                objects {
                  validities {
                    uuid
                    user_key
                    name
                    parent {
                      uuid
                    }
                    unit_type {
                      uuid
                    }
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
        return ReadOrgUnits.parse_obj(data).org_units

    async def read_itsystems(
        self,
        uuids: list[UUID],
        from_date: datetime | None | UnsetType = UNSET,
        to_date: datetime | None | UnsetType = UNSET,
    ) -> ReadItsystemsItsystems:
        query = gql(
            """
            query read_itsystems($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              itsystems(filter: {from_date: $from_date, to_date: $to_date, uuids: $uuids}) {
                objects {
                  validities {
                    uuid
                    user_key
                    name
                    validity {
                      from
                      to
                    }
                    roles {
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
        return ReadItsystems.parse_obj(data).itsystems

    async def read_classes(
        self,
        uuids: list[UUID],
        from_date: datetime | None | UnsetType = UNSET,
        to_date: datetime | None | UnsetType = UNSET,
    ) -> ReadClassesClasses:
        query = gql(
            """
            query read_classes($uuids: [UUID!]!, $from_date: DateTime, $to_date: DateTime) {
              classes(filter: {from_date: $from_date, to_date: $to_date, uuids: $uuids}) {
                objects {
                  validities {
                    uuid
                    user_key
                    name
                    scope
                    owner
                    published
                    facet {
                      uuid
                    }
                    parent {
                      uuid
                    }
                    it_system {
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
        variables: dict[str, object] = {
            "uuids": uuids,
            "from_date": from_date,
            "to_date": to_date,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadClasses.parse_obj(data).classes

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
                    engagement_uuids
                    rolebindings {
                      uuid
                    }
                    external_id
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

    async def itusers(self, filter: ITUserFilter) -> ItusersItusers:
        query = gql(
            """
            query itusers($filter: ITUserFilter!) {
              itusers(filter: $filter) {
                objects {
                  uuid
                  current {
                    external_id
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return Itusers.parse_obj(data).itusers

    async def addresses(self, filter: AddressFilter) -> AddressesAddresses:
        query = gql(
            """
            query addresses($filter: AddressFilter!) {
              addresses(filter: $filter) {
                objects {
                  uuid
                  current {
                    ituser_uuid
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return Addresses.parse_obj(data).addresses

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
                    ituser_uuid
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
                    employee_uuid
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

    async def read_itsystem_uuid(
        self, filter: ITSystemFilter
    ) -> ReadItsystemUuidItsystems:
        query = gql(
            """
            query read_itsystem_uuid($filter: ITSystemFilter!) {
              itsystems(filter: $filter) {
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

    async def read_org_unit_uuid(
        self, filter: OrganisationUnitFilter
    ) -> ReadOrgUnitUuidOrgUnits:
        query = gql(
            """
            query read_org_unit_uuid($filter: OrganisationUnitFilter!) {
              org_units(filter: $filter) {
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
        return ReadOrgUnitUuid.parse_obj(data).org_units

    async def read_manager_person_uuid(
        self, filter: ManagerFilter, inherit: bool
    ) -> ReadManagerPersonUuidManagers:
        query = gql(
            """
            query read_manager_person_uuid($filter: ManagerFilter!, $inherit: Boolean!) {
              managers(filter: $filter, inherit: $inherit) {
                objects {
                  current {
                    person {
                      uuid
                    }
                  }
                }
              }
            }
            """
        )
        variables: dict[str, object] = {"filter": filter, "inherit": inherit}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ReadManagerPersonUuid.parse_obj(data).managers

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
                    engagement_type_response {
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

    async def read_rolebindings(
        self, filter: RoleBindingFilter | None | UnsetType = UNSET
    ) -> ReadRolebindingsRolebindings:
        query = gql(
            """
            query read_rolebindings($filter: RoleBindingFilter) {
              rolebindings(filter: $filter) {
                objects {
                  current {
                    ituser {
                      person {
                        uuid
                      }
                    }
                    role {
                      uuid
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
        return ReadRolebindings.parse_obj(data).rolebindings

    async def resolve_dar_address(
        self, filter: AddressFilter | None | UnsetType = UNSET
    ) -> ResolveDarAddressAddresses:
        query = gql(
            """
            query resolve_dar_address($filter: AddressFilter) {
              addresses(filter: $filter) {
                objects {
                  uuid
                  current {
                    resolve {
                      __typename
                      ... on DARAddress {
                        zip_code
                        zip_code_name
                        floor
                        door
                        road_name
                        house_number
                        supplementary_city
                      }
                      value
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
        return ResolveDarAddress.parse_obj(data).addresses

    async def address_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> AddressRefreshAddressRefresh:
        query = gql(
            """
            mutation address_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              address_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AddressRefresh.parse_obj(data).address_refresh

    async def association_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> AssociationRefreshAssociationRefresh:
        query = gql(
            """
            mutation association_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              association_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return AssociationRefresh.parse_obj(data).association_refresh

    async def class_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> ClassRefreshClassRefresh:
        query = gql(
            """
            mutation class_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              class_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ClassRefresh.parse_obj(data).class_refresh

    async def engagement_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> EngagementRefreshEngagementRefresh:
        query = gql(
            """
            mutation engagement_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              engagement_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return EngagementRefresh.parse_obj(data).engagement_refresh

    async def facet_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> FacetRefreshFacetRefresh:
        query = gql(
            """
            mutation facet_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              facet_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return FacetRefresh.parse_obj(data).facet_refresh

    async def itsystem_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> ItsystemRefreshItsystemRefresh:
        query = gql(
            """
            mutation itsystem_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              itsystem_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItsystemRefresh.parse_obj(data).itsystem_refresh

    async def ituser_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> ItuserRefreshItuserRefresh:
        query = gql(
            """
            mutation ituser_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              ituser_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ItuserRefresh.parse_obj(data).ituser_refresh

    async def kle_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> KleRefreshKleRefresh:
        query = gql(
            """
            mutation kle_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              kle_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return KleRefresh.parse_obj(data).kle_refresh

    async def leave_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> LeaveRefreshLeaveRefresh:
        query = gql(
            """
            mutation leave_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              leave_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return LeaveRefresh.parse_obj(data).leave_refresh

    async def manager_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> ManagerRefreshManagerRefresh:
        query = gql(
            """
            mutation manager_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              manager_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return ManagerRefresh.parse_obj(data).manager_refresh

    async def org_unit_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> OrgUnitRefreshOrgUnitRefresh:
        query = gql(
            """
            mutation org_unit_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              org_unit_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OrgUnitRefresh.parse_obj(data).org_unit_refresh

    async def owner_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> OwnerRefreshOwnerRefresh:
        query = gql(
            """
            mutation owner_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              owner_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return OwnerRefresh.parse_obj(data).owner_refresh

    async def person_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> PersonRefreshEmployeeRefresh:
        query = gql(
            """
            mutation person_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              employee_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return PersonRefresh.parse_obj(data).employee_refresh

    async def related_unit_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> RelatedUnitRefreshRelatedUnitRefresh:
        query = gql(
            """
            mutation related_unit_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              related_unit_refresh(
                exchange: $exchange
                owner: $owner
                filter: {uuids: $uuids}
              ) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return RelatedUnitRefresh.parse_obj(data).related_unit_refresh

    async def rolebinding_refresh(
        self,
        uuids: list[UUID],
        exchange: str | None | UnsetType = UNSET,
        owner: UUID | None | UnsetType = UNSET,
    ) -> RolebindingRefreshRolebindingRefresh:
        query = gql(
            """
            mutation rolebinding_refresh($exchange: String, $owner: UUID, $uuids: [UUID!]!) {
              rolebinding_refresh(exchange: $exchange, owner: $owner, filter: {uuids: $uuids}) {
                objects
              }
            }
            """
        )
        variables: dict[str, object] = {
            "exchange": exchange,
            "owner": owner,
            "uuids": uuids,
        }
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return RolebindingRefresh.parse_obj(data).rolebinding_refresh

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

    async def _testing__class_read(
        self, filter: ClassFilter | None | UnsetType = UNSET
    ) -> TestingClassReadClasses:
        query = gql(
            """
            query __testing__class_read($filter: ClassFilter) {
              classes(filter: $filter) {
                objects {
                  validities {
                    uuid
                    user_key
                    name
                    scope
                    owner
                    published
                    facet {
                      uuid
                    }
                    parent {
                      uuid
                    }
                    it_system {
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
        return TestingClassRead.parse_obj(data).classes

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

    async def _testing__itsystem_read(
        self, filter: ITSystemFilter | None | UnsetType = UNSET
    ) -> TestingItsystemReadItsystems:
        query = gql(
            """
            query __testing__itsystem_read($filter: ITSystemFilter) {
              itsystems(filter: $filter) {
                objects {
                  validities {
                    uuid
                    user_key
                    name
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
        return TestingItsystemRead.parse_obj(data).itsystems

    async def _testing__org_unit_read(
        self, filter: OrganisationUnitFilter | None | UnsetType = UNSET
    ) -> TestingOrgUnitReadOrgUnits:
        query = gql(
            """
            query __testing__org_unit_read($filter: OrganisationUnitFilter) {
              org_units(filter: $filter) {
                objects {
                  validities {
                    uuid
                    user_key
                    name
                    parent {
                      uuid
                    }
                    unit_type {
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
        return TestingOrgUnitRead.parse_obj(data).org_units

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

    async def _testing__rolebinding_create(
        self, input: RoleBindingCreateInput
    ) -> TestingRolebindingCreateRolebindingCreate:
        query = gql(
            """
            mutation __testing__rolebinding_create($input: RoleBindingCreateInput!) {
              rolebinding_create(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingRolebindingCreate.parse_obj(data).rolebinding_create

    async def _testing__person_update(
        self, input: EmployeeUpdateInput
    ) -> TestingPersonUpdateEmployeeUpdate:
        query = gql(
            """
            mutation __testing__person_update($input: EmployeeUpdateInput!) {
              employee_update(input: $input) {
                uuid
              }
            }
            """
        )
        variables: dict[str, object] = {"input": input}
        response = await self.execute(query=query, variables=variables)
        data = self.get_data(response)
        return TestingPersonUpdate.parse_obj(data).employee_update
