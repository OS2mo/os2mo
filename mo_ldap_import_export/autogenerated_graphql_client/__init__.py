from .address_refresh import AddressRefresh
from .address_refresh import AddressRefreshAddressRefresh
from .address_terminate import AddressTerminate
from .address_terminate import AddressTerminateAddressTerminate
from .async_base_client import AsyncBaseClient
from .base_model import BaseModel
from .class_create import ClassCreate
from .class_create import ClassCreateClassCreate
from .class_update import ClassUpdate
from .class_update import ClassUpdateClassUpdate
from .client import GraphQLClient
from .engagement_org_unit_address_refresh import EngagementOrgUnitAddressRefresh
from .engagement_org_unit_address_refresh import (
    EngagementOrgUnitAddressRefreshAddressRefresh,
)
from .engagement_refresh import EngagementRefresh
from .engagement_refresh import EngagementRefreshEngagementRefresh
from .engagement_terminate import EngagementTerminate
from .engagement_terminate import EngagementTerminateEngagementTerminate
from .enums import AuditLogModel
from .enums import FileStore
from .enums import OwnerInferencePriority
from .exceptions import GraphQLClientError
from .exceptions import GraphQLClientGraphQLError
from .exceptions import GraphQLClientGraphQLMultiError
from .exceptions import GraphQLClientHttpError
from .exceptions import GraphQlClientInvalidResponseError
from .input_types import AddressCreateInput
from .input_types import AddressFilter
from .input_types import AddressRegistrationFilter
from .input_types import AddressTerminateInput
from .input_types import AddressUpdateInput
from .input_types import AssociationCreateInput
from .input_types import AssociationFilter
from .input_types import AssociationRegistrationFilter
from .input_types import AssociationTerminateInput
from .input_types import AssociationUpdateInput
from .input_types import AuditLogFilter
from .input_types import ClassCreateInput
from .input_types import ClassFilter
from .input_types import ClassRegistrationFilter
from .input_types import ClassTerminateInput
from .input_types import ClassUpdateInput
from .input_types import ConfigurationFilter
from .input_types import EmployeeCreateInput
from .input_types import EmployeeFilter
from .input_types import EmployeeRegistrationFilter
from .input_types import EmployeesBoundAddressFilter
from .input_types import EmployeesBoundAssociationFilter
from .input_types import EmployeesBoundEngagementFilter
from .input_types import EmployeesBoundITUserFilter
from .input_types import EmployeesBoundLeaveFilter
from .input_types import EmployeesBoundManagerFilter
from .input_types import EmployeesBoundRoleFilter
from .input_types import EmployeeTerminateInput
from .input_types import EmployeeUpdateInput
from .input_types import EngagementCreateInput
from .input_types import EngagementFilter
from .input_types import EngagementRegistrationFilter
from .input_types import EngagementTerminateInput
from .input_types import EngagementUpdateInput
from .input_types import FacetCreateInput
from .input_types import FacetFilter
from .input_types import FacetRegistrationFilter
from .input_types import FacetsBoundClassFilter
from .input_types import FacetTerminateInput
from .input_types import FacetUpdateInput
from .input_types import FileFilter
from .input_types import HealthFilter
from .input_types import ITAssociationCreateInput
from .input_types import ITAssociationTerminateInput
from .input_types import ITAssociationUpdateInput
from .input_types import ITSystemCreateInput
from .input_types import ITSystemFilter
from .input_types import ITSystemRegistrationFilter
from .input_types import ITSystemTerminateInput
from .input_types import ITSystemUpdateInput
from .input_types import ITUserCreateInput
from .input_types import ITUserFilter
from .input_types import ITUserRegistrationFilter
from .input_types import ITUserTerminateInput
from .input_types import ITUserUpdateInput
from .input_types import KLECreateInput
from .input_types import KLEFilter
from .input_types import KLERegistrationFilter
from .input_types import KLETerminateInput
from .input_types import KLEUpdateInput
from .input_types import LeaveCreateInput
from .input_types import LeaveFilter
from .input_types import LeaveRegistrationFilter
from .input_types import LeaveTerminateInput
from .input_types import LeaveUpdateInput
from .input_types import ManagerCreateInput
from .input_types import ManagerFilter
from .input_types import ManagerRegistrationFilter
from .input_types import ManagerTerminateInput
from .input_types import ManagerUpdateInput
from .input_types import ModelsUuidsBoundRegistrationFilter
from .input_types import OrganisationCreate
from .input_types import OrganisationUnitCreateInput
from .input_types import OrganisationUnitFilter
from .input_types import OrganisationUnitRegistrationFilter
from .input_types import OrganisationUnitTerminateInput
from .input_types import OrganisationUnitUpdateInput
from .input_types import OrgUnitsboundaddressfilter
from .input_types import OrgUnitsboundassociationfilter
from .input_types import OrgUnitsboundengagementfilter
from .input_types import OrgUnitsboundituserfilter
from .input_types import OrgUnitsboundklefilter
from .input_types import OrgUnitsboundleavefilter
from .input_types import OrgUnitsboundownerfilter
from .input_types import OrgUnitsboundrelatedunitfilter
from .input_types import OrgUnitsboundrolefilter
from .input_types import OwnerCreateInput
from .input_types import OwnerFilter
from .input_types import OwnerTerminateInput
from .input_types import OwnerUpdateInput
from .input_types import ParentsBoundClassFilter
from .input_types import ParentsBoundFacetFilter
from .input_types import ParentsBoundOrganisationUnitFilter
from .input_types import RAOpenValidityInput
from .input_types import RAValidityInput
from .input_types import RegistrationFilter
from .input_types import RelatedUnitFilter
from .input_types import RelatedUnitsUpdateInput
from .input_types import RoleCreateInput
from .input_types import RoleFilter
from .input_types import RoleRegistrationFilter
from .input_types import RoleTerminateInput
from .input_types import RoleUpdateInput
from .input_types import UuidsBoundClassFilter
from .input_types import UuidsBoundEmployeeFilter
from .input_types import UuidsBoundEngagementFilter
from .input_types import UuidsBoundFacetFilter
from .input_types import UuidsBoundITSystemFilter
from .input_types import UuidsBoundITUserFilter
from .input_types import UuidsBoundLeaveFilter
from .input_types import UuidsBoundOrganisationUnitFilter
from .input_types import ValidityInput
from .itsystem_create import ItsystemCreate
from .itsystem_create import ItsystemCreateItsystemCreate
from .ituser_refresh import ItuserRefresh
from .ituser_refresh import ItuserRefreshItuserRefresh
from .ituser_terminate import ItuserTerminate
from .ituser_terminate import ItuserTerminateItuserTerminate
from .org_unit_engagements_refresh import OrgUnitEngagementsRefresh
from .org_unit_engagements_refresh import OrgUnitEngagementsRefreshEngagementRefresh
from .person_address_refresh import PersonAddressRefresh
from .person_address_refresh import PersonAddressRefreshAddressRefresh
from .person_engagement_refresh import PersonEngagementRefresh
from .person_engagement_refresh import PersonEngagementRefreshEngagementRefresh
from .person_ituser_refresh import PersonItuserRefresh
from .person_ituser_refresh import PersonItuserRefreshItuserRefresh
from .read_addresses import ReadAddresses
from .read_addresses import ReadAddressesAddresses
from .read_addresses import ReadAddressesAddressesObjects
from .read_addresses import ReadAddressesAddressesObjectsValidities
from .read_addresses import ReadAddressesAddressesObjectsValiditiesAddressType
from .read_addresses import ReadAddressesAddressesObjectsValiditiesPerson
from .read_addresses import ReadAddressesAddressesObjectsValiditiesValidity
from .read_all_address_uuids import ReadAllAddressUuids
from .read_all_address_uuids import ReadAllAddressUuidsAddresses
from .read_all_address_uuids import ReadAllAddressUuidsAddressesObjects
from .read_all_address_uuids import ReadAllAddressUuidsAddressesObjectsValidities
from .read_all_address_uuids import (
    ReadAllAddressUuidsAddressesObjectsValiditiesValidity,
)
from .read_all_address_uuids import ReadAllAddressUuidsAddressesPageInfo
from .read_all_employee_uuids import ReadAllEmployeeUuids
from .read_all_employee_uuids import ReadAllEmployeeUuidsEmployees
from .read_all_employee_uuids import ReadAllEmployeeUuidsEmployeesObjects
from .read_all_employee_uuids import ReadAllEmployeeUuidsEmployeesObjectsValidities
from .read_all_employee_uuids import (
    ReadAllEmployeeUuidsEmployeesObjectsValiditiesValidity,
)
from .read_all_employee_uuids import ReadAllEmployeeUuidsEmployeesPageInfo
from .read_all_engagement_uuids import ReadAllEngagementUuids
from .read_all_engagement_uuids import ReadAllEngagementUuidsEngagements
from .read_all_engagement_uuids import ReadAllEngagementUuidsEngagementsObjects
from .read_all_engagement_uuids import (
    ReadAllEngagementUuidsEngagementsObjectsValidities,
)
from .read_all_engagement_uuids import (
    ReadAllEngagementUuidsEngagementsObjectsValiditiesValidity,
)
from .read_all_engagement_uuids import ReadAllEngagementUuidsEngagementsPageInfo
from .read_all_ituser_uuids import ReadAllItuserUuids
from .read_all_ituser_uuids import ReadAllItuserUuidsItusers
from .read_all_ituser_uuids import ReadAllItuserUuidsItusersObjects
from .read_all_ituser_uuids import ReadAllItuserUuidsItusersObjectsValidities
from .read_all_ituser_uuids import ReadAllItuserUuidsItusersObjectsValiditiesValidity
from .read_all_ituser_uuids import ReadAllItuserUuidsItusersPageInfo
from .read_all_itusers import ReadAllItusers
from .read_all_itusers import ReadAllItusersItusers
from .read_all_itusers import ReadAllItusersItusersObjects
from .read_all_itusers import ReadAllItusersItusersObjectsValidities
from .read_all_itusers import ReadAllItusersItusersPageInfo
from .read_all_org_unit_uuids import ReadAllOrgUnitUuids
from .read_all_org_unit_uuids import ReadAllOrgUnitUuidsOrgUnits
from .read_all_org_unit_uuids import ReadAllOrgUnitUuidsOrgUnitsObjects
from .read_all_org_unit_uuids import ReadAllOrgUnitUuidsOrgUnitsObjectsValidities
from .read_all_org_unit_uuids import (
    ReadAllOrgUnitUuidsOrgUnitsObjectsValiditiesValidity,
)
from .read_all_org_unit_uuids import ReadAllOrgUnitUuidsOrgUnitsPageInfo
from .read_class_name_by_class_uuid import ReadClassNameByClassUuid
from .read_class_name_by_class_uuid import ReadClassNameByClassUuidClasses
from .read_class_name_by_class_uuid import ReadClassNameByClassUuidClassesObjects
from .read_class_name_by_class_uuid import ReadClassNameByClassUuidClassesObjectsCurrent
from .read_class_user_keys import ReadClassUserKeys
from .read_class_user_keys import ReadClassUserKeysClasses
from .read_class_user_keys import ReadClassUserKeysClassesObjects
from .read_class_user_keys import ReadClassUserKeysClassesObjectsCurrent
from .read_class_uuid import ReadClassUuid
from .read_class_uuid import ReadClassUuidClasses
from .read_class_uuid import ReadClassUuidClassesObjects
from .read_class_uuid_by_facet_and_class_user_key import (
    ReadClassUuidByFacetAndClassUserKey,
)
from .read_class_uuid_by_facet_and_class_user_key import (
    ReadClassUuidByFacetAndClassUserKeyClasses,
)
from .read_class_uuid_by_facet_and_class_user_key import (
    ReadClassUuidByFacetAndClassUserKeyClassesObjects,
)
from .read_employee_addresses import ReadEmployeeAddresses
from .read_employee_addresses import ReadEmployeeAddressesAddresses
from .read_employee_addresses import ReadEmployeeAddressesAddressesObjects
from .read_employee_uuid_by_cpr_number import ReadEmployeeUuidByCprNumber
from .read_employee_uuid_by_cpr_number import ReadEmployeeUuidByCprNumberEmployees
from .read_employee_uuid_by_cpr_number import (
    ReadEmployeeUuidByCprNumberEmployeesObjects,
)
from .read_employee_uuid_by_ituser_user_key import ReadEmployeeUuidByItuserUserKey
from .read_employee_uuid_by_ituser_user_key import (
    ReadEmployeeUuidByItuserUserKeyItusers,
)
from .read_employee_uuid_by_ituser_user_key import (
    ReadEmployeeUuidByItuserUserKeyItusersObjects,
)
from .read_employee_uuid_by_ituser_user_key import (
    ReadEmployeeUuidByItuserUserKeyItusersObjectsCurrent,
)
from .read_employees import ReadEmployees
from .read_employees import ReadEmployeesEmployees
from .read_employees import ReadEmployeesEmployeesObjects
from .read_employees import ReadEmployeesEmployeesObjectsValidities
from .read_employees import ReadEmployeesEmployeesObjectsValiditiesValidity
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnit,
)
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnitEngagements,
)
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnitEngagementsObjects,
)
from .read_employees_with_engagement_to_org_unit import (
    ReadEmployeesWithEngagementToOrgUnitEngagementsObjectsCurrent,
)
from .read_engagement_uuid_by_ituser_user_key import ReadEngagementUuidByItuserUserKey
from .read_engagement_uuid_by_ituser_user_key import (
    ReadEngagementUuidByItuserUserKeyItusers,
)
from .read_engagement_uuid_by_ituser_user_key import (
    ReadEngagementUuidByItuserUserKeyItusersObjects,
)
from .read_engagement_uuid_by_ituser_user_key import (
    ReadEngagementUuidByItuserUserKeyItusersObjectsCurrent,
)
from .read_engagements import ReadEngagements
from .read_engagements import ReadEngagementsEngagements
from .read_engagements import ReadEngagementsEngagementsObjects
from .read_engagements import ReadEngagementsEngagementsObjectsValidities
from .read_engagements import ReadEngagementsEngagementsObjectsValiditiesValidity
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuid
from .read_engagements_by_employee_uuid import ReadEngagementsByEmployeeUuidEngagements
from .read_engagements_by_employee_uuid import (
    ReadEngagementsByEmployeeUuidEngagementsObjects,
)
from .read_engagements_by_employee_uuid import (
    ReadEngagementsByEmployeeUuidEngagementsObjectsCurrent,
)
from .read_engagements_by_employee_uuid import (
    ReadEngagementsByEmployeeUuidEngagementsObjectsCurrentValidity,
)
from .read_engagements_by_engagements_filter import ReadEngagementsByEngagementsFilter
from .read_engagements_by_engagements_filter import (
    ReadEngagementsByEngagementsFilterEngagements,
)
from .read_engagements_by_engagements_filter import (
    ReadEngagementsByEngagementsFilterEngagementsObjects,
)
from .read_engagements_by_engagements_filter import (
    ReadEngagementsByEngagementsFilterEngagementsObjectsCurrent,
)
from .read_engagements_is_primary import ReadEngagementsIsPrimary
from .read_engagements_is_primary import ReadEngagementsIsPrimaryEngagements
from .read_engagements_is_primary import ReadEngagementsIsPrimaryEngagementsObjects
from .read_engagements_is_primary import (
    ReadEngagementsIsPrimaryEngagementsObjectsValidities,
)
from .read_engagements_is_primary import (
    ReadEngagementsIsPrimaryEngagementsObjectsValiditiesValidity,
)
from .read_facet_classes import ReadFacetClasses
from .read_facet_classes import ReadFacetClassesClasses
from .read_facet_classes import ReadFacetClassesClassesObjects
from .read_facet_classes import ReadFacetClassesClassesObjectsCurrent
from .read_facet_uuid import ReadFacetUuid
from .read_facet_uuid import ReadFacetUuidFacets
from .read_facet_uuid import ReadFacetUuidFacetsObjects
from .read_filtered_addresses import ReadFilteredAddresses
from .read_filtered_addresses import ReadFilteredAddressesAddresses
from .read_filtered_addresses import ReadFilteredAddressesAddressesObjects
from .read_filtered_addresses import ReadFilteredAddressesAddressesObjectsValidities
from .read_filtered_addresses import (
    ReadFilteredAddressesAddressesObjectsValiditiesAddressType,
)
from .read_filtered_addresses import (
    ReadFilteredAddressesAddressesObjectsValiditiesValidity,
)
from .read_filtered_itusers import ReadFilteredItusers
from .read_filtered_itusers import ReadFilteredItusersItusers
from .read_filtered_itusers import ReadFilteredItusersItusersObjects
from .read_filtered_itusers import ReadFilteredItusersItusersObjectsValidities
from .read_filtered_itusers import ReadFilteredItusersItusersObjectsValiditiesItsystem
from .read_filtered_itusers import ReadFilteredItusersItusersObjectsValiditiesValidity
from .read_is_primary_engagements import ReadIsPrimaryEngagements
from .read_is_primary_engagements import ReadIsPrimaryEngagementsEngagements
from .read_is_primary_engagements import ReadIsPrimaryEngagementsEngagementsObjects
from .read_is_primary_engagements import (
    ReadIsPrimaryEngagementsEngagementsObjectsCurrent,
)
from .read_itsystems import ReadItsystems
from .read_itsystems import ReadItsystemsItsystems
from .read_itsystems import ReadItsystemsItsystemsObjects
from .read_itsystems import ReadItsystemsItsystemsObjectsCurrent
from .read_ituser_by_employee_and_itsystem_uuid import (
    ReadItuserByEmployeeAndItsystemUuid,
)
from .read_ituser_by_employee_and_itsystem_uuid import (
    ReadItuserByEmployeeAndItsystemUuidItusers,
)
from .read_ituser_by_employee_and_itsystem_uuid import (
    ReadItuserByEmployeeAndItsystemUuidItusersObjects,
)
from .read_itusers import ReadItusers
from .read_itusers import ReadItusersItusers
from .read_itusers import ReadItusersItusersObjects
from .read_itusers import ReadItusersItusersObjectsValidities
from .read_itusers import ReadItusersItusersObjectsValiditiesValidity
from .read_org_unit_addresses import ReadOrgUnitAddresses
from .read_org_unit_addresses import ReadOrgUnitAddressesAddresses
from .read_org_unit_addresses import ReadOrgUnitAddressesAddressesObjects
from .read_org_units import ReadOrgUnits
from .read_org_units import ReadOrgUnitsOrgUnits
from .read_org_units import ReadOrgUnitsOrgUnitsObjects
from .read_org_units import ReadOrgUnitsOrgUnitsObjectsValidities
from .read_org_units import ReadOrgUnitsOrgUnitsObjectsValiditiesValidity
from .read_root_org_uuid import ReadRootOrgUuid
from .read_root_org_uuid import ReadRootOrgUuidOrg
from .set_job_title import SetJobTitle
from .set_job_title import SetJobTitleEngagementUpdate

__all__ = [
    "AddressCreateInput",
    "AddressFilter",
    "AddressRefresh",
    "AddressRefreshAddressRefresh",
    "AddressRegistrationFilter",
    "AddressTerminate",
    "AddressTerminateAddressTerminate",
    "AddressTerminateInput",
    "AddressUpdateInput",
    "AssociationCreateInput",
    "AssociationFilter",
    "AssociationRegistrationFilter",
    "AssociationTerminateInput",
    "AssociationUpdateInput",
    "AsyncBaseClient",
    "AuditLogFilter",
    "AuditLogModel",
    "BaseModel",
    "ClassCreate",
    "ClassCreateClassCreate",
    "ClassCreateInput",
    "ClassFilter",
    "ClassRegistrationFilter",
    "ClassTerminateInput",
    "ClassUpdate",
    "ClassUpdateClassUpdate",
    "ClassUpdateInput",
    "ConfigurationFilter",
    "EmployeeCreateInput",
    "EmployeeFilter",
    "EmployeeRegistrationFilter",
    "EmployeeTerminateInput",
    "EmployeeUpdateInput",
    "EmployeesBoundAddressFilter",
    "EmployeesBoundAssociationFilter",
    "EmployeesBoundEngagementFilter",
    "EmployeesBoundITUserFilter",
    "EmployeesBoundLeaveFilter",
    "EmployeesBoundManagerFilter",
    "EmployeesBoundRoleFilter",
    "EngagementCreateInput",
    "EngagementFilter",
    "EngagementOrgUnitAddressRefresh",
    "EngagementOrgUnitAddressRefreshAddressRefresh",
    "EngagementRefresh",
    "EngagementRefreshEngagementRefresh",
    "EngagementRegistrationFilter",
    "EngagementTerminate",
    "EngagementTerminateEngagementTerminate",
    "EngagementTerminateInput",
    "EngagementUpdateInput",
    "FacetCreateInput",
    "FacetFilter",
    "FacetRegistrationFilter",
    "FacetTerminateInput",
    "FacetUpdateInput",
    "FacetsBoundClassFilter",
    "FileFilter",
    "FileStore",
    "GraphQLClient",
    "GraphQLClientError",
    "GraphQLClientGraphQLError",
    "GraphQLClientGraphQLMultiError",
    "GraphQLClientHttpError",
    "GraphQlClientInvalidResponseError",
    "HealthFilter",
    "ITAssociationCreateInput",
    "ITAssociationTerminateInput",
    "ITAssociationUpdateInput",
    "ITSystemCreateInput",
    "ITSystemFilter",
    "ITSystemRegistrationFilter",
    "ITSystemTerminateInput",
    "ITSystemUpdateInput",
    "ITUserCreateInput",
    "ITUserFilter",
    "ITUserRegistrationFilter",
    "ITUserTerminateInput",
    "ITUserUpdateInput",
    "ItsystemCreate",
    "ItsystemCreateItsystemCreate",
    "ItuserRefresh",
    "ItuserRefreshItuserRefresh",
    "ItuserTerminate",
    "ItuserTerminateItuserTerminate",
    "KLECreateInput",
    "KLEFilter",
    "KLERegistrationFilter",
    "KLETerminateInput",
    "KLEUpdateInput",
    "LeaveCreateInput",
    "LeaveFilter",
    "LeaveRegistrationFilter",
    "LeaveTerminateInput",
    "LeaveUpdateInput",
    "ManagerCreateInput",
    "ManagerFilter",
    "ManagerRegistrationFilter",
    "ManagerTerminateInput",
    "ManagerUpdateInput",
    "ModelsUuidsBoundRegistrationFilter",
    "OrgUnitEngagementsRefresh",
    "OrgUnitEngagementsRefreshEngagementRefresh",
    "OrgUnitsboundaddressfilter",
    "OrgUnitsboundassociationfilter",
    "OrgUnitsboundengagementfilter",
    "OrgUnitsboundituserfilter",
    "OrgUnitsboundklefilter",
    "OrgUnitsboundleavefilter",
    "OrgUnitsboundownerfilter",
    "OrgUnitsboundrelatedunitfilter",
    "OrgUnitsboundrolefilter",
    "OrganisationCreate",
    "OrganisationUnitCreateInput",
    "OrganisationUnitFilter",
    "OrganisationUnitRegistrationFilter",
    "OrganisationUnitTerminateInput",
    "OrganisationUnitUpdateInput",
    "OwnerCreateInput",
    "OwnerFilter",
    "OwnerInferencePriority",
    "OwnerTerminateInput",
    "OwnerUpdateInput",
    "ParentsBoundClassFilter",
    "ParentsBoundFacetFilter",
    "ParentsBoundOrganisationUnitFilter",
    "PersonAddressRefresh",
    "PersonAddressRefreshAddressRefresh",
    "PersonEngagementRefresh",
    "PersonEngagementRefreshEngagementRefresh",
    "PersonItuserRefresh",
    "PersonItuserRefreshItuserRefresh",
    "RAOpenValidityInput",
    "RAValidityInput",
    "ReadAddresses",
    "ReadAddressesAddresses",
    "ReadAddressesAddressesObjects",
    "ReadAddressesAddressesObjectsValidities",
    "ReadAddressesAddressesObjectsValiditiesAddressType",
    "ReadAddressesAddressesObjectsValiditiesPerson",
    "ReadAddressesAddressesObjectsValiditiesValidity",
    "ReadAllAddressUuids",
    "ReadAllAddressUuidsAddresses",
    "ReadAllAddressUuidsAddressesObjects",
    "ReadAllAddressUuidsAddressesObjectsValidities",
    "ReadAllAddressUuidsAddressesObjectsValiditiesValidity",
    "ReadAllAddressUuidsAddressesPageInfo",
    "ReadAllEmployeeUuids",
    "ReadAllEmployeeUuidsEmployees",
    "ReadAllEmployeeUuidsEmployeesObjects",
    "ReadAllEmployeeUuidsEmployeesObjectsValidities",
    "ReadAllEmployeeUuidsEmployeesObjectsValiditiesValidity",
    "ReadAllEmployeeUuidsEmployeesPageInfo",
    "ReadAllEngagementUuids",
    "ReadAllEngagementUuidsEngagements",
    "ReadAllEngagementUuidsEngagementsObjects",
    "ReadAllEngagementUuidsEngagementsObjectsValidities",
    "ReadAllEngagementUuidsEngagementsObjectsValiditiesValidity",
    "ReadAllEngagementUuidsEngagementsPageInfo",
    "ReadAllItuserUuids",
    "ReadAllItuserUuidsItusers",
    "ReadAllItuserUuidsItusersObjects",
    "ReadAllItuserUuidsItusersObjectsValidities",
    "ReadAllItuserUuidsItusersObjectsValiditiesValidity",
    "ReadAllItuserUuidsItusersPageInfo",
    "ReadAllItusers",
    "ReadAllItusersItusers",
    "ReadAllItusersItusersObjects",
    "ReadAllItusersItusersObjectsValidities",
    "ReadAllItusersItusersPageInfo",
    "ReadAllOrgUnitUuids",
    "ReadAllOrgUnitUuidsOrgUnits",
    "ReadAllOrgUnitUuidsOrgUnitsObjects",
    "ReadAllOrgUnitUuidsOrgUnitsObjectsValidities",
    "ReadAllOrgUnitUuidsOrgUnitsObjectsValiditiesValidity",
    "ReadAllOrgUnitUuidsOrgUnitsPageInfo",
    "ReadClassNameByClassUuid",
    "ReadClassNameByClassUuidClasses",
    "ReadClassNameByClassUuidClassesObjects",
    "ReadClassNameByClassUuidClassesObjectsCurrent",
    "ReadClassUserKeys",
    "ReadClassUserKeysClasses",
    "ReadClassUserKeysClassesObjects",
    "ReadClassUserKeysClassesObjectsCurrent",
    "ReadClassUuid",
    "ReadClassUuidByFacetAndClassUserKey",
    "ReadClassUuidByFacetAndClassUserKeyClasses",
    "ReadClassUuidByFacetAndClassUserKeyClassesObjects",
    "ReadClassUuidClasses",
    "ReadClassUuidClassesObjects",
    "ReadEmployeeAddresses",
    "ReadEmployeeAddressesAddresses",
    "ReadEmployeeAddressesAddressesObjects",
    "ReadEmployeeUuidByCprNumber",
    "ReadEmployeeUuidByCprNumberEmployees",
    "ReadEmployeeUuidByCprNumberEmployeesObjects",
    "ReadEmployeeUuidByItuserUserKey",
    "ReadEmployeeUuidByItuserUserKeyItusers",
    "ReadEmployeeUuidByItuserUserKeyItusersObjects",
    "ReadEmployeeUuidByItuserUserKeyItusersObjectsCurrent",
    "ReadEmployees",
    "ReadEmployeesEmployees",
    "ReadEmployeesEmployeesObjects",
    "ReadEmployeesEmployeesObjectsValidities",
    "ReadEmployeesEmployeesObjectsValiditiesValidity",
    "ReadEmployeesWithEngagementToOrgUnit",
    "ReadEmployeesWithEngagementToOrgUnitEngagements",
    "ReadEmployeesWithEngagementToOrgUnitEngagementsObjects",
    "ReadEmployeesWithEngagementToOrgUnitEngagementsObjectsCurrent",
    "ReadEngagementUuidByItuserUserKey",
    "ReadEngagementUuidByItuserUserKeyItusers",
    "ReadEngagementUuidByItuserUserKeyItusersObjects",
    "ReadEngagementUuidByItuserUserKeyItusersObjectsCurrent",
    "ReadEngagements",
    "ReadEngagementsByEmployeeUuid",
    "ReadEngagementsByEmployeeUuidEngagements",
    "ReadEngagementsByEmployeeUuidEngagementsObjects",
    "ReadEngagementsByEmployeeUuidEngagementsObjectsCurrent",
    "ReadEngagementsByEmployeeUuidEngagementsObjectsCurrentValidity",
    "ReadEngagementsByEngagementsFilter",
    "ReadEngagementsByEngagementsFilterEngagements",
    "ReadEngagementsByEngagementsFilterEngagementsObjects",
    "ReadEngagementsByEngagementsFilterEngagementsObjectsCurrent",
    "ReadEngagementsEngagements",
    "ReadEngagementsEngagementsObjects",
    "ReadEngagementsEngagementsObjectsValidities",
    "ReadEngagementsEngagementsObjectsValiditiesValidity",
    "ReadEngagementsIsPrimary",
    "ReadEngagementsIsPrimaryEngagements",
    "ReadEngagementsIsPrimaryEngagementsObjects",
    "ReadEngagementsIsPrimaryEngagementsObjectsValidities",
    "ReadEngagementsIsPrimaryEngagementsObjectsValiditiesValidity",
    "ReadFacetClasses",
    "ReadFacetClassesClasses",
    "ReadFacetClassesClassesObjects",
    "ReadFacetClassesClassesObjectsCurrent",
    "ReadFacetUuid",
    "ReadFacetUuidFacets",
    "ReadFacetUuidFacetsObjects",
    "ReadFilteredAddresses",
    "ReadFilteredAddressesAddresses",
    "ReadFilteredAddressesAddressesObjects",
    "ReadFilteredAddressesAddressesObjectsValidities",
    "ReadFilteredAddressesAddressesObjectsValiditiesAddressType",
    "ReadFilteredAddressesAddressesObjectsValiditiesValidity",
    "ReadFilteredItusers",
    "ReadFilteredItusersItusers",
    "ReadFilteredItusersItusersObjects",
    "ReadFilteredItusersItusersObjectsValidities",
    "ReadFilteredItusersItusersObjectsValiditiesItsystem",
    "ReadFilteredItusersItusersObjectsValiditiesValidity",
    "ReadIsPrimaryEngagements",
    "ReadIsPrimaryEngagementsEngagements",
    "ReadIsPrimaryEngagementsEngagementsObjects",
    "ReadIsPrimaryEngagementsEngagementsObjectsCurrent",
    "ReadItsystems",
    "ReadItsystemsItsystems",
    "ReadItsystemsItsystemsObjects",
    "ReadItsystemsItsystemsObjectsCurrent",
    "ReadItuserByEmployeeAndItsystemUuid",
    "ReadItuserByEmployeeAndItsystemUuidItusers",
    "ReadItuserByEmployeeAndItsystemUuidItusersObjects",
    "ReadItusers",
    "ReadItusersItusers",
    "ReadItusersItusersObjects",
    "ReadItusersItusersObjectsValidities",
    "ReadItusersItusersObjectsValiditiesValidity",
    "ReadOrgUnitAddresses",
    "ReadOrgUnitAddressesAddresses",
    "ReadOrgUnitAddressesAddressesObjects",
    "ReadOrgUnits",
    "ReadOrgUnitsOrgUnits",
    "ReadOrgUnitsOrgUnitsObjects",
    "ReadOrgUnitsOrgUnitsObjectsValidities",
    "ReadOrgUnitsOrgUnitsObjectsValiditiesValidity",
    "ReadRootOrgUuid",
    "ReadRootOrgUuidOrg",
    "RegistrationFilter",
    "RelatedUnitFilter",
    "RelatedUnitsUpdateInput",
    "RoleCreateInput",
    "RoleFilter",
    "RoleRegistrationFilter",
    "RoleTerminateInput",
    "RoleUpdateInput",
    "SetJobTitle",
    "SetJobTitleEngagementUpdate",
    "UuidsBoundClassFilter",
    "UuidsBoundEmployeeFilter",
    "UuidsBoundEngagementFilter",
    "UuidsBoundFacetFilter",
    "UuidsBoundITSystemFilter",
    "UuidsBoundITUserFilter",
    "UuidsBoundLeaveFilter",
    "UuidsBoundOrganisationUnitFilter",
    "ValidityInput",
]
