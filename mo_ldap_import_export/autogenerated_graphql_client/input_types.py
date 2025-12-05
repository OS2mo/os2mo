# This file has been modified by the UnsetInputTypesPlugin
from datetime import datetime
from typing import Any
from typing import Optional
from uuid import UUID

from pydantic import Field

from ..types import CPRNumber
from .base_model import UNSET
from .base_model import BaseModel
from .base_model import UnsetType
from .enums import AccessLogModel
from .enums import FileStore
from .enums import OwnerInferencePriority


class AccessLogFilter(BaseModel):
    ids: list[UUID] | None = None
    uuids: list[UUID] | None = None
    actors: list[UUID] | None = None
    models: list[AccessLogModel] | None = None
    start: datetime | None = None
    end: datetime | None = None


class AddressCreateInput(BaseModel):
    uuid: UUID | None = None
    org_unit: UUID | None = None
    person: UUID | None = None
    employee: UUID | None = None
    engagement: UUID | None = None
    ituser: UUID | None = None
    visibility: UUID | None = None
    validity: "RAValidityInput"
    user_key: str | None = None
    value: str
    address_type: UUID


class AddressFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["AddressRegistrationFilter"] = None
    address_type: Optional["ClassFilter"] = None
    address_types: list[UUID] | None = None
    address_type_user_keys: list[str] | None = None
    engagement: Optional["EngagementFilter"] = None
    engagements: list[UUID] | None = None
    ituser: Optional["ITUserFilter"] = None
    visibility: Optional["ClassFilter"] = None


class AddressRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class AddressTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class AddressUpdateInput(BaseModel):
    uuid: UUID
    org_unit: UUID | None = None
    person: UUID | None = None
    employee: UUID | None = None
    engagement: UUID | None = None
    ituser: UUID | None = None
    visibility: UUID | None = None
    validity: "RAValidityInput"
    user_key: str | None = None
    value: str | None = None
    address_type: UUID | None = None


class AssociationCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    primary: UUID | None = None
    validity: "RAValidityInput"
    person: UUID | None = None
    employee: UUID | None = None
    substitute: UUID | None = None
    trade_union: UUID | None = None
    org_unit: UUID
    association_type: UUID


class AssociationFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["AssociationRegistrationFilter"] = None
    association_type: Optional["ClassFilter"] = None
    association_types: list[UUID] | None = None
    association_type_user_keys: list[str] | None = None
    it_association: bool | None = None


class AssociationRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class AssociationTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class AssociationUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    primary: UUID | None = None
    validity: "RAValidityInput"
    person: UUID | None = None
    employee: UUID | None = None
    substitute: UUID | None = None
    trade_union: UUID | None = None
    org_unit: UUID | None = None
    association_type: UUID | None = None


class ClassCreateInput(BaseModel):
    uuid: UUID | None = None
    name: str
    user_key: str
    facet_uuid: UUID
    scope: str | None = None
    published: str = "Publiceret"
    parent_uuid: UUID | None = None
    example: str | None = None
    owner: UUID | None = None
    validity: "ValidityInput"
    it_system_uuid: UUID | None = None
    description: str | None = None


class ClassFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ClassRegistrationFilter"] = None
    name: list[str] | None = None
    facet: Optional["FacetFilter"] = None
    facets: list[UUID] | None = None
    facet_user_keys: list[str] | None = None
    parent: Optional["ClassFilter"] = None
    parents: list[UUID] | None = None
    parent_user_keys: list[str] | None = None
    it_system: Optional["ITSystemFilter"] = None
    owner: Optional["ClassOwnerFilter"] = None
    scope: list[str] | None = None


class ClassOwnerFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["OrganisationUnitRegistrationFilter"] = None
    query: str | None | UnsetType = UNSET
    names: list[str] | None | UnsetType = UNSET
    parent: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    parents: list[UUID] | None | UnsetType = UNSET
    child: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    hierarchy: Optional["ClassFilter"] = None
    hierarchies: list[UUID] | None = None
    subtree: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    descendant: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    ancestor: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    engagement: Optional["EngagementFilter"] = None
    include_none: bool = False


class ClassRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class ClassTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class ClassUpdateInput(BaseModel):
    uuid: UUID
    name: str
    user_key: str
    facet_uuid: UUID
    scope: str | None = None
    published: str = "Publiceret"
    parent_uuid: UUID | None = None
    example: str | None = None
    owner: UUID | None = None
    validity: "ValidityInput"
    it_system_uuid: UUID | None = None
    description: str | None = None


class ConfigurationFilter(BaseModel):
    identifiers: list[str] | None = None


class DescendantParentBoundOrganisationUnitFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["OrganisationUnitRegistrationFilter"] = None
    query: str | None | UnsetType = UNSET
    names: list[str] | None | UnsetType = UNSET
    parents: list[UUID] | None | UnsetType = UNSET
    child: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    hierarchy: Optional["ClassFilter"] = None
    hierarchies: list[UUID] | None = None
    subtree: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    ancestor: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    engagement: Optional["EngagementFilter"] = None


class EmployeeCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    nickname_given_name: str | None = None
    nickname_surname: str | None = None
    seniority: Any | None = None
    cpr_number: CPRNumber | None = None
    given_name: str
    surname: str


class EmployeeFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["EmployeeRegistrationFilter"] = None
    query: str | None | UnsetType = UNSET
    cpr_numbers: list[CPRNumber] | None = None


class EmployeeRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class EmployeeTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID
    vacate: bool = False


class EmployeeUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    nickname_given_name: str | None = None
    nickname_surname: str | None = None
    seniority: Any | None = None
    cpr_number: CPRNumber | None = None
    given_name: str | None = None
    surname: str | None = None
    validity: "RAValidityInput"


class EmployeesBoundAddressFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["AddressRegistrationFilter"] = None
    address_type: Optional["ClassFilter"] = None
    address_types: list[UUID] | None = None
    address_type_user_keys: list[str] | None = None
    engagement: Optional["EngagementFilter"] = None
    engagements: list[UUID] | None = None
    ituser: Optional["ITUserFilter"] = None
    visibility: Optional["ClassFilter"] = None


class EmployeesBoundAssociationFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["AssociationRegistrationFilter"] = None
    association_type: Optional["ClassFilter"] = None
    association_types: list[UUID] | None = None
    association_type_user_keys: list[str] | None = None
    it_association: bool | None = None


class EmployeesBoundEngagementFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["EngagementRegistrationFilter"] = None
    job_function: Optional["ClassFilter"] = None
    engagement_type: Optional["ClassFilter"] = None


class EmployeesBoundITUserFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ITUserRegistrationFilter"] = None
    itsystem: Optional["ITSystemFilter"] = None
    itsystem_uuids: list[UUID] | None = None
    engagement: Optional["EngagementFilter"] = None
    external_ids: list[str] | None = None


class EmployeesBoundLeaveFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["LeaveRegistrationFilter"] = None


class EmployeesBoundManagerFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ManagerRegistrationFilter"] = None
    responsibility: Optional["ClassFilter"] = None
    manager_type: Optional["ClassFilter"] = None
    exclude: Optional["EmployeeFilter"] = None


class EngagementBoundITUserFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ITUserRegistrationFilter"] = None
    itsystem: Optional["ITSystemFilter"] = None
    itsystem_uuids: list[UUID] | None = None
    external_ids: list[str] | None = None


class EngagementCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    primary: UUID | None = None
    validity: "RAValidityInput"
    fraction: int | None = None
    extension_1: str | None = None
    extension_2: str | None = None
    extension_3: str | None = None
    extension_4: str | None = None
    extension_5: str | None = None
    extension_6: str | None = None
    extension_7: str | None = None
    extension_8: str | None = None
    extension_9: str | None = None
    extension_10: str | None = None
    employee: UUID | None = None
    person: UUID | None = None
    org_unit: UUID
    engagement_type: UUID
    job_function: UUID


class EngagementFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["EngagementRegistrationFilter"] = None
    job_function: Optional["ClassFilter"] = None
    engagement_type: Optional["ClassFilter"] = None


class EngagementRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class EngagementTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class EngagementUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    primary: UUID | None = None
    validity: "RAValidityInput"
    fraction: int | None = None
    extension_1: str | None = None
    extension_2: str | None = None
    extension_3: str | None = None
    extension_4: str | None = None
    extension_5: str | None = None
    extension_6: str | None = None
    extension_7: str | None = None
    extension_8: str | None = None
    extension_9: str | None = None
    extension_10: str | None = None
    employee: UUID | None = None
    person: UUID | None = None
    org_unit: UUID | None = None
    engagement_type: UUID | None = None
    job_function: UUID | None = None


class EventAcknowledgeInput(BaseModel):
    token: Any


class EventFilter(BaseModel):
    listener: UUID


class EventSendInput(BaseModel):
    namespace: str
    routing_key: str
    subject: str
    priority: int = 10000


class EventSilenceInput(BaseModel):
    listeners: "ListenerFilter"
    subjects: list[str]


class EventUnsilenceInput(BaseModel):
    listeners: Optional["ListenerFilter"] = None
    subjects: list[str] | None = None
    priorities: list[int] | None = None


class FacetCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str
    published: str = "Publiceret"
    validity: "ValidityInput"


class FacetFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["FacetRegistrationFilter"] = None
    parent: Optional["FacetFilter"] = None
    parents: list[UUID] | None = None
    parent_user_keys: list[str] | None = None


class FacetRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class FacetTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class FacetUpdateInput(BaseModel):
    uuid: UUID
    user_key: str
    published: str = "Publiceret"
    validity: "ValidityInput"


class FacetsBoundClassFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ClassRegistrationFilter"] = None
    name: list[str] | None = None
    facet: Optional["FacetFilter"] = None
    facet_user_keys: list[str] | None = None
    parent: Optional["ClassFilter"] = None
    parents: list[UUID] | None = None
    parent_user_keys: list[str] | None = None
    it_system: Optional["ITSystemFilter"] = None
    owner: Optional["ClassOwnerFilter"] = None
    scope: list[str] | None = None


class FileFilter(BaseModel):
    file_store: FileStore
    file_names: list[str] | None = None


class FullEventFilter(BaseModel):
    listeners: Optional["ListenerFilter"] = None
    subjects: list[str] | None = None
    priorities: list[int] | None = None
    silenced: bool | None = None


class HealthFilter(BaseModel):
    identifiers: list[str] | None = None


class ITAssociationCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    primary: UUID | None = None
    validity: "RAValidityInput"
    org_unit: UUID
    person: UUID
    it_user: UUID
    job_function: UUID


class ITAssociationTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class ITAssociationUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    primary: UUID | None = None
    validity: "RAValidityInput"
    org_unit: UUID | None = None
    it_user: UUID | None = None
    job_function: UUID | None = None


class ITSystemCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str
    name: str
    validity: "RAOpenValidityInput"


class ITSystemFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ITSystemRegistrationFilter"] = None


class ITSystemRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class ITSystemTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class ITSystemUpdateInput(BaseModel):
    uuid: UUID
    user_key: str
    name: str
    validity: "RAOpenValidityInput"


class ITUserCreateInput(BaseModel):
    uuid: UUID | None = None
    external_id: str | None = None
    primary: UUID | None = None
    person: UUID | None = None
    org_unit: UUID | None = None
    engagement: UUID | None = None
    engagements: list[UUID] | None = None
    validity: "RAValidityInput"
    user_key: str
    itsystem: UUID
    note: str | None = None


class ITUserFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["ITUserRegistrationFilter"] = None
    itsystem: Optional["ITSystemFilter"] = None
    itsystem_uuids: list[UUID] | None = None
    engagement: Optional["EngagementFilter"] = None
    external_ids: list[str] | None = None


class ITUserRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class ITUserTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class ITUserUpdateInput(BaseModel):
    uuid: UUID
    external_id: str | None = None
    primary: UUID | None = None
    person: UUID | None = None
    org_unit: UUID | None = None
    engagement: UUID | None = None
    engagements: list[UUID] | None = None
    validity: "RAValidityInput"
    user_key: str | None = None
    itsystem: UUID | None = None
    note: str | None = None


class ItSystemboundclassfilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ClassRegistrationFilter"] = None
    name: list[str] | None = None
    facet: Optional["FacetFilter"] = None
    facets: list[UUID] | None = None
    facet_user_keys: list[str] | None = None
    parent: Optional["ClassFilter"] = None
    parents: list[UUID] | None = None
    parent_user_keys: list[str] | None = None
    owner: Optional["ClassOwnerFilter"] = None
    scope: list[str] | None = None


class ItuserBoundAddressFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["AddressRegistrationFilter"] = None
    address_type: Optional["ClassFilter"] = None
    address_types: list[UUID] | None = None
    address_type_user_keys: list[str] | None = None
    engagement: Optional["EngagementFilter"] = None
    engagements: list[UUID] | None = None
    visibility: Optional["ClassFilter"] = None


class ItuserBoundRoleBindingFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["RoleRegistrationFilter"] = None
    role: Optional["ClassFilter"] = None


class KLECreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    org_unit: UUID
    kle_aspects: list[UUID]
    kle_number: UUID
    validity: "RAValidityInput"


class KLEFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["KLERegistrationFilter"] = None


class KLERegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class KLETerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class KLEUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    kle_number: UUID | None = None
    kle_aspects: list[UUID] | None = None
    org_unit: UUID | None = None
    validity: "RAValidityInput"


class LeaveCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    person: UUID
    engagement: UUID
    leave_type: UUID
    validity: "RAValidityInput"


class LeaveFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["LeaveRegistrationFilter"] = None


class LeaveRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class LeaveTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class LeaveUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    person: UUID | None = None
    engagement: UUID | None = None
    leave_type: UUID | None = None
    validity: "RAValidityInput"


class ListenerCreateInput(BaseModel):
    namespace: str = "mo"
    user_key: str
    routing_key: str


class ListenerDeleteInput(BaseModel):
    uuid: UUID
    delete_pending_events: bool = False


class ListenerFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    owners: list[UUID] | None = None
    routing_keys: list[str] | None = None
    namespaces: Optional["NamespaceFilter"] = None


class ListenersBoundFullEventFilter(BaseModel):
    subjects: list[str] | None = None
    priorities: list[int] | None = None
    silenced: bool | None = None


class ManagerCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    person: UUID | None = None
    responsibility: list[UUID]
    org_unit: UUID
    manager_level: UUID
    manager_type: UUID
    validity: "RAValidityInput"


class ManagerFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["ManagerRegistrationFilter"] = None
    responsibility: Optional["ClassFilter"] = None
    manager_type: Optional["ClassFilter"] = None
    exclude: Optional["EmployeeFilter"] = None


class ManagerRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class ManagerTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class ManagerUpdateInput(BaseModel):
    uuid: UUID
    validity: "RAValidityInput"
    user_key: str | None = None
    person: UUID | None = None
    responsibility: list[UUID] | None = None
    org_unit: UUID | None = None
    manager_type: UUID | None = None
    manager_level: UUID | None = None


class ModelsUuidsBoundRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class NamespaceCreateInput(BaseModel):
    name: str
    public: bool = False


class NamespaceDeleteInput(BaseModel):
    name: str


class NamespaceFilter(BaseModel):
    names: list[str] | None = None
    owners: list[UUID] | None = None
    public: bool | None = None


class NamespacesBoundListenerFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    owners: list[UUID] | None = None
    routing_keys: list[str] | None = None


class OrgUnitsboundaddressfilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["AddressRegistrationFilter"] = None
    address_type: Optional["ClassFilter"] = None
    address_types: list[UUID] | None = None
    address_type_user_keys: list[str] | None = None
    engagement: Optional["EngagementFilter"] = None
    engagements: list[UUID] | None = None
    ituser: Optional["ITUserFilter"] = None
    visibility: Optional["ClassFilter"] = None


class OrgUnitsboundassociationfilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["AssociationRegistrationFilter"] = None
    association_type: Optional["ClassFilter"] = None
    association_types: list[UUID] | None = None
    association_type_user_keys: list[str] | None = None
    it_association: bool | None = None


class OrgUnitsboundengagementfilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["EngagementRegistrationFilter"] = None
    job_function: Optional["ClassFilter"] = None
    engagement_type: Optional["ClassFilter"] = None


class OrgUnitsboundituserfilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ITUserRegistrationFilter"] = None
    itsystem: Optional["ITSystemFilter"] = None
    itsystem_uuids: list[UUID] | None = None
    engagement: Optional["EngagementFilter"] = None
    external_ids: list[str] | None = None


class OrgUnitsboundklefilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["KLERegistrationFilter"] = None


class OrgUnitsboundleavefilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["LeaveRegistrationFilter"] = None


class OrgUnitsboundmanagerfilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ManagerRegistrationFilter"] = None
    responsibility: Optional["ClassFilter"] = None
    manager_type: Optional["ClassFilter"] = None
    exclude: Optional["EmployeeFilter"] = None


class OrgUnitsboundrelatedunitfilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET


class OrganisationCreate(BaseModel):
    municipality_code: int | None | UnsetType = UNSET


class OrganisationUnitCreateInput(BaseModel):
    uuid: UUID | None | UnsetType = UNSET
    validity: "RAValidityInput"
    name: str
    user_key: str | None | UnsetType = UNSET
    parent: UUID | None | UnsetType = UNSET
    org_unit_type: UUID
    time_planning: UUID | None | UnsetType = UNSET
    org_unit_level: UUID | None | UnsetType = UNSET
    org_unit_hierarchy: UUID | None | UnsetType = UNSET


class OrganisationUnitFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["OrganisationUnitRegistrationFilter"] = None
    query: str | None | UnsetType = UNSET
    names: list[str] | None | UnsetType = UNSET
    parent: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    parents: list[UUID] | None | UnsetType = UNSET
    child: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    hierarchy: Optional["ClassFilter"] = None
    hierarchies: list[UUID] | None = None
    subtree: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    descendant: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    ancestor: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    engagement: Optional["EngagementFilter"] = None


class OrganisationUnitRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class OrganisationUnitTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class OrganisationUnitUpdateInput(BaseModel):
    uuid: UUID
    validity: "RAValidityInput"
    name: str | None | UnsetType = UNSET
    user_key: str | None | UnsetType = UNSET
    parent: UUID | None | UnsetType = UNSET
    org_unit_type: UUID | None | UnsetType = UNSET
    org_unit_level: UUID | None | UnsetType = UNSET
    org_unit_hierarchy: UUID | None | UnsetType = UNSET
    time_planning: UUID | None | UnsetType = UNSET


class OwnerCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    org_unit: UUID | None = None
    person: UUID | None = None
    owner: UUID | None = None
    inference_priority: OwnerInferencePriority | None = None
    validity: "RAValidityInput"


class OwnerFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    owner: Optional["EmployeeFilter"] = None


class OwnerTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class OwnerUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    org_unit: UUID | None = None
    person: UUID | None = None
    owner: UUID | None = None
    inference_priority: OwnerInferencePriority | None = None
    validity: "RAValidityInput"


class OwnersBoundListenerFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    routing_keys: list[str] | None = None
    namespaces: Optional["NamespaceFilter"] = None


class OwnersBoundNamespaceFilter(BaseModel):
    names: list[str] | None = None
    public: bool | None = None


class ParentBoundOrganisationUnitFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["OrganisationUnitRegistrationFilter"] = None
    query: str | None | UnsetType = UNSET
    names: list[str] | None | UnsetType = UNSET
    parents: list[UUID] | None | UnsetType = UNSET
    child: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    hierarchy: Optional["ClassFilter"] = None
    hierarchies: list[UUID] | None = None
    subtree: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    descendant: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    ancestor: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    engagement: Optional["EngagementFilter"] = None


class ParentsBoundClassFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ClassRegistrationFilter"] = None
    name: list[str] | None = None
    facet: Optional["FacetFilter"] = None
    facets: list[UUID] | None = None
    facet_user_keys: list[str] | None = None
    parent: Optional["ClassFilter"] = None
    parent_user_keys: list[str] | None = None
    it_system: Optional["ITSystemFilter"] = None
    owner: Optional["ClassOwnerFilter"] = None
    scope: list[str] | None = None


class ParentsBoundFacetFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["FacetRegistrationFilter"] = None
    parent: Optional["FacetFilter"] = None
    parent_user_keys: list[str] | None = None


class RAOpenValidityInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime | None = None


class RAValidityInput(BaseModel):
    from_: datetime = Field(alias="from")
    to: datetime | None = None


class RegistrationFilter(BaseModel):
    uuids: list[UUID] | None = None
    actors: list[UUID] | None = None
    models: list[str] | None = None
    start: datetime | None = None
    end: datetime | None = None


class RelatedUnitFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None


class RelatedUnitsUpdateInput(BaseModel):
    uuid: UUID | None = None
    origin: UUID
    destination: list[UUID] | None = None
    validity: "RAValidityInput"


class RoleBindingCreateInput(BaseModel):
    uuid: UUID | None = None
    user_key: str | None = None
    org_unit: UUID | None = None
    ituser: UUID
    role: UUID
    validity: "RAValidityInput"


class RoleBindingFilter(BaseModel):
    uuids: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    registration: Optional["RoleRegistrationFilter"] = None
    ituser: Optional["ITUserFilter"] = None
    role: Optional["ClassFilter"] = None


class RoleBindingTerminateInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime
    uuid: UUID


class RoleBindingUpdateInput(BaseModel):
    uuid: UUID
    user_key: str | None = None
    org_unit: UUID | None = None
    ituser: UUID
    role: UUID | None = None
    validity: "RAValidityInput"


class RoleRegistrationFilter(BaseModel):
    actors: list[UUID] | None = None
    start: datetime | None = None
    end: datetime | None = None


class UuidsBoundClassFilter(BaseModel):
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ClassRegistrationFilter"] = None
    name: list[str] | None = None
    facet: Optional["FacetFilter"] = None
    facets: list[UUID] | None = None
    facet_user_keys: list[str] | None = None
    parent: Optional["ClassFilter"] = None
    parents: list[UUID] | None = None
    parent_user_keys: list[str] | None = None
    it_system: Optional["ITSystemFilter"] = None
    owner: Optional["ClassOwnerFilter"] = None
    scope: list[str] | None = None


class UuidsBoundEmployeeFilter(BaseModel):
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["EmployeeRegistrationFilter"] = None
    query: str | None | UnsetType = UNSET
    cpr_numbers: list[CPRNumber] | None = None


class UuidsBoundEngagementFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["EngagementRegistrationFilter"] = None
    job_function: Optional["ClassFilter"] = None
    engagement_type: Optional["ClassFilter"] = None


class UuidsBoundFacetFilter(BaseModel):
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["FacetRegistrationFilter"] = None
    parent: Optional["FacetFilter"] = None
    parents: list[UUID] | None = None
    parent_user_keys: list[str] | None = None


class UuidsBoundITSystemFilter(BaseModel):
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ITSystemRegistrationFilter"] = None


class UuidsBoundITUserFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["ITUserRegistrationFilter"] = None
    itsystem: Optional["ITSystemFilter"] = None
    itsystem_uuids: list[UUID] | None = None
    engagement: Optional["EngagementFilter"] = None
    external_ids: list[str] | None = None


class UuidsBoundLeaveFilter(BaseModel):
    org_unit: Optional["OrganisationUnitFilter"] = None
    org_units: list[UUID] | None = None
    employee: Optional["EmployeeFilter"] | UnsetType = UNSET
    employees: list[UUID] | None = None
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["LeaveRegistrationFilter"] = None


class UuidsBoundOrganisationUnitFilter(BaseModel):
    user_keys: list[str] | None = None
    from_date: datetime | None | UnsetType = UNSET
    to_date: datetime | None | UnsetType = UNSET
    registration: Optional["OrganisationUnitRegistrationFilter"] = None
    query: str | None | UnsetType = UNSET
    names: list[str] | None | UnsetType = UNSET
    parent: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    parents: list[UUID] | None | UnsetType = UNSET
    child: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    hierarchy: Optional["ClassFilter"] = None
    hierarchies: list[UUID] | None = None
    subtree: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    descendant: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    ancestor: Optional["OrganisationUnitFilter"] | UnsetType = UNSET
    engagement: Optional["EngagementFilter"] = None


class ValidityInput(BaseModel):
    from_: datetime | None = Field(alias="from", default=None)
    to: datetime | None = None


AccessLogFilter.update_forward_refs()
AddressCreateInput.update_forward_refs()
AddressFilter.update_forward_refs()
AddressRegistrationFilter.update_forward_refs()
AddressTerminateInput.update_forward_refs()
AddressUpdateInput.update_forward_refs()
AssociationCreateInput.update_forward_refs()
AssociationFilter.update_forward_refs()
AssociationRegistrationFilter.update_forward_refs()
AssociationTerminateInput.update_forward_refs()
AssociationUpdateInput.update_forward_refs()
ClassCreateInput.update_forward_refs()
ClassFilter.update_forward_refs()
ClassOwnerFilter.update_forward_refs()
ClassRegistrationFilter.update_forward_refs()
ClassTerminateInput.update_forward_refs()
ClassUpdateInput.update_forward_refs()
ConfigurationFilter.update_forward_refs()
DescendantParentBoundOrganisationUnitFilter.update_forward_refs()
EmployeeCreateInput.update_forward_refs()
EmployeeFilter.update_forward_refs()
EmployeeRegistrationFilter.update_forward_refs()
EmployeeTerminateInput.update_forward_refs()
EmployeeUpdateInput.update_forward_refs()
EmployeesBoundAddressFilter.update_forward_refs()
EmployeesBoundAssociationFilter.update_forward_refs()
EmployeesBoundEngagementFilter.update_forward_refs()
EmployeesBoundITUserFilter.update_forward_refs()
EmployeesBoundLeaveFilter.update_forward_refs()
EmployeesBoundManagerFilter.update_forward_refs()
EngagementBoundITUserFilter.update_forward_refs()
EngagementCreateInput.update_forward_refs()
EngagementFilter.update_forward_refs()
EngagementRegistrationFilter.update_forward_refs()
EngagementTerminateInput.update_forward_refs()
EngagementUpdateInput.update_forward_refs()
EventAcknowledgeInput.update_forward_refs()
EventFilter.update_forward_refs()
EventSendInput.update_forward_refs()
EventSilenceInput.update_forward_refs()
EventUnsilenceInput.update_forward_refs()
FacetCreateInput.update_forward_refs()
FacetFilter.update_forward_refs()
FacetRegistrationFilter.update_forward_refs()
FacetTerminateInput.update_forward_refs()
FacetUpdateInput.update_forward_refs()
FacetsBoundClassFilter.update_forward_refs()
FileFilter.update_forward_refs()
FullEventFilter.update_forward_refs()
HealthFilter.update_forward_refs()
ITAssociationCreateInput.update_forward_refs()
ITAssociationTerminateInput.update_forward_refs()
ITAssociationUpdateInput.update_forward_refs()
ITSystemCreateInput.update_forward_refs()
ITSystemFilter.update_forward_refs()
ITSystemRegistrationFilter.update_forward_refs()
ITSystemTerminateInput.update_forward_refs()
ITSystemUpdateInput.update_forward_refs()
ITUserCreateInput.update_forward_refs()
ITUserFilter.update_forward_refs()
ITUserRegistrationFilter.update_forward_refs()
ITUserTerminateInput.update_forward_refs()
ITUserUpdateInput.update_forward_refs()
ItSystemboundclassfilter.update_forward_refs()
ItuserBoundAddressFilter.update_forward_refs()
ItuserBoundRoleBindingFilter.update_forward_refs()
KLECreateInput.update_forward_refs()
KLEFilter.update_forward_refs()
KLERegistrationFilter.update_forward_refs()
KLETerminateInput.update_forward_refs()
KLEUpdateInput.update_forward_refs()
LeaveCreateInput.update_forward_refs()
LeaveFilter.update_forward_refs()
LeaveRegistrationFilter.update_forward_refs()
LeaveTerminateInput.update_forward_refs()
LeaveUpdateInput.update_forward_refs()
ListenerCreateInput.update_forward_refs()
ListenerDeleteInput.update_forward_refs()
ListenerFilter.update_forward_refs()
ListenersBoundFullEventFilter.update_forward_refs()
ManagerCreateInput.update_forward_refs()
ManagerFilter.update_forward_refs()
ManagerRegistrationFilter.update_forward_refs()
ManagerTerminateInput.update_forward_refs()
ManagerUpdateInput.update_forward_refs()
ModelsUuidsBoundRegistrationFilter.update_forward_refs()
NamespaceCreateInput.update_forward_refs()
NamespaceDeleteInput.update_forward_refs()
NamespaceFilter.update_forward_refs()
NamespacesBoundListenerFilter.update_forward_refs()
OrgUnitsboundaddressfilter.update_forward_refs()
OrgUnitsboundassociationfilter.update_forward_refs()
OrgUnitsboundengagementfilter.update_forward_refs()
OrgUnitsboundituserfilter.update_forward_refs()
OrgUnitsboundklefilter.update_forward_refs()
OrgUnitsboundleavefilter.update_forward_refs()
OrgUnitsboundmanagerfilter.update_forward_refs()
OrgUnitsboundrelatedunitfilter.update_forward_refs()
OrganisationCreate.update_forward_refs()
OrganisationUnitCreateInput.update_forward_refs()
OrganisationUnitFilter.update_forward_refs()
OrganisationUnitRegistrationFilter.update_forward_refs()
OrganisationUnitTerminateInput.update_forward_refs()
OrganisationUnitUpdateInput.update_forward_refs()
OwnerCreateInput.update_forward_refs()
OwnerFilter.update_forward_refs()
OwnerTerminateInput.update_forward_refs()
OwnerUpdateInput.update_forward_refs()
OwnersBoundListenerFilter.update_forward_refs()
OwnersBoundNamespaceFilter.update_forward_refs()
ParentBoundOrganisationUnitFilter.update_forward_refs()
ParentsBoundClassFilter.update_forward_refs()
ParentsBoundFacetFilter.update_forward_refs()
RAOpenValidityInput.update_forward_refs()
RAValidityInput.update_forward_refs()
RegistrationFilter.update_forward_refs()
RelatedUnitFilter.update_forward_refs()
RelatedUnitsUpdateInput.update_forward_refs()
RoleBindingCreateInput.update_forward_refs()
RoleBindingFilter.update_forward_refs()
RoleBindingTerminateInput.update_forward_refs()
RoleBindingUpdateInput.update_forward_refs()
RoleRegistrationFilter.update_forward_refs()
UuidsBoundClassFilter.update_forward_refs()
UuidsBoundEmployeeFilter.update_forward_refs()
UuidsBoundEngagementFilter.update_forward_refs()
UuidsBoundFacetFilter.update_forward_refs()
UuidsBoundITSystemFilter.update_forward_refs()
UuidsBoundITUserFilter.update_forward_refs()
UuidsBoundLeaveFilter.update_forward_refs()
UuidsBoundOrganisationUnitFilter.update_forward_refs()
ValidityInput.update_forward_refs()
