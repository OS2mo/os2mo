# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import logging
from enum import Enum
from typing import Any
from uuid import UUID

import dateutil
import strawberry
from pydantic import BaseModel
from pydantic import ConstrainedStr
from pydantic import Field
from pydantic import validator

from mora import common
from mora import exceptions
from mora import lora
from mora import mapping
from mora.service.org import get_configured_organisation
from mora.util import NEGATIVE_INFINITY
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY
from ramodels.base import RABase
from ramodels.mo import OpenValidity
from ramodels.mo import Validity as RAValidity
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import UUIDBase

logger = logging.getLogger(__name__)


# Various
# -------


class NonEmptyString(ConstrainedStr):
    min_length: int = 1


# --------------------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------------------


class Validity(OpenValidity):
    """Model representing an entities validity range."""

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def get_termination_effect(self) -> dict:
        if self.from_date and self.to_date:
            return common._create_virkning(
                self.get_terminate_effect_from_date(),
                self.get_terminate_effect_to_date(),
            )

        if not self.from_date and self.to_date:
            logger.warning(
                'terminate org unit called without "from" in "validity"',
            )
            return common._create_virkning(
                self.get_terminate_effect_to_date(), "infinity"
            )
        raise exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
            key="Organization Unit must be set with either 'to' or both 'from' "
            "and 'to'",
            unit={
                "from": self.from_date.isoformat() if self.from_date else None,
                "to": self.to_date.isoformat() if self.to_date else None,
            },
        )

    def get_terminate_effect_from_date(self) -> datetime.datetime:
        if not self.from_date or not isinstance(self.from_date, datetime.datetime):
            raise exceptions.ErrorCodes.V_MISSING_START_DATE()

        if self.from_date.time() != datetime.time.min:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                f"{self.from_date.isoformat()!r} is not at midnight!",
            )

        return self.from_date

    def get_terminate_effect_to_date(self) -> datetime.datetime:
        if not self.to_date:
            return POSITIVE_INFINITY

        if self.to_date.time() != datetime.time.min:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                f"{self.to_date.isoformat()!r} is not at midnight!",
            )

        return self.to_date + ONE_DAY


class ValidityTerminate(Validity):
    to_date: datetime.datetime = Field(
        alias="to",
        description="When the validity should end " "- required when terminating",
    )


class MoraTriggerRequest(BaseModel):
    """Model representing a MoRa Trigger Request."""

    type: str = Field(description="Type of the request, ex. 'org_unit'.")

    uuid: UUID = Field(
        description="UUID for the entity accessed in the request. "
        "Ex type=ORG_UNIT, then this UUID will be the UUID of the ORG_UNIT"
    )

    validity: Validity = Field(description="Type of the request, ex. 'org_unit'.")


class MoraTrigger(BaseModel):
    """Model representing a MoRa Trigger."""

    request_type: str = Field(
        description="Request type to do, ex CREATE, EDIT, TERMINATE or REFRESH. "
        "Ref: mora.mapping.RequestType"
    )

    request: MoraTriggerRequest = Field(description="The Request for the trigger.")

    role_type: str = Field(description="Role type for the trigger, ex 'org_unit'.")

    event_type: str = Field(
        description="Trigger event-type. " "Ref: mora.mapping.EventType"
    )

    uuid: UUID = Field(
        description="UUID of the entity being handled in the trigger. "
        "Ex. type=ORG_UNIT, this this is the org-unit-uuid."
    )

    result: Any = Field(description="Result of the trigger", default=None)

    def to_trigger_dict(self) -> dict:
        trigger_dict = self.dict(by_alias=True)
        return MoraTrigger.convert_trigger_dict_fields(trigger_dict)

    @staticmethod
    def convert_trigger_dict_fields(trigger_dict: dict) -> dict:
        for key in trigger_dict.keys():
            if isinstance(trigger_dict[key], dict):
                trigger_dict[key] = MoraTrigger.convert_trigger_dict_fields(
                    trigger_dict[key]
                )
                continue

            if isinstance(trigger_dict[key], UUID):
                trigger_dict[key] = str(trigger_dict[key])
                continue

            if isinstance(trigger_dict[key], datetime.datetime):
                trigger_dict[key] = trigger_dict[key].isoformat()
                continue

        return trigger_dict


class Triggerless(BaseModel):
    triggerless: bool | None = Field(
        description="Flag specifying if triggers should not be invoked, if true.",
        default=False,
    )


class GenericUUIDModel(UUIDBase):
    """Generic UUID model for return types."""


class OrgFuncTrigger(MoraTrigger):
    """General model for Mora-Organization-Function triggers."""

    org_unit_uuid: UUID = Field(
        description="UUID for the organization unit in question."
    )

    employee_id: UUID | None = Field(None, description="OrgFunc Related employee UUID.")


# Root Organisation
# -----------------
class Organisation(UUIDBase):
    """Model representing an Organization."""

    pass


# Addresses
# ---------
class AddressTrigger(OrgFuncTrigger):
    """Model representing a mora-trigger, specific for addresses."""


class AddressCreateResponse(UUIDBase):
    """Response from GraphQL when creating addresses."""


class AddressTerminateResponse(UUIDBase):
    """Response from GraphQL when terminating addresses."""


class AddressTerminate(ValidityTerminate, Triggerless):
    """Model representing an address-termination."""

    uuid: UUID = Field(description="UUID for the address we want to terminate.")

    def get_address_trigger(self) -> AddressTrigger:
        return AddressTrigger(
            org_unit_uuid=self.uuid,
            request_type=mapping.RequestType.TERMINATE,
            request=MoraTriggerRequest(
                type=mapping.ADDRESS,
                uuid=self.uuid,
                validity=Validity(
                    from_date=self.from_date,
                    to_date=self.to_date,
                ),
            ),
            role_type=mapping.ADDRESS,
            event_type=mapping.EventType.ON_BEFORE,
            uuid=self.uuid,
        )  # type: ignore

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afsluttet",
        }


class AddressType(MOBase):
    name: str = Field("", description="Name of the address type, ex. 'Email'.")

    scope: str = Field("", description="Scopeof the address type, ex. 'EMAIL'.")

    example: str | None = Field(None, description="Example value for the address.")


class AddressVisibility(MOBase):
    name: str = Field(
        "", description="Name for the visibility, ex. 'M\\u00e5 vises eksternt'."
    )

    scope: str = Field("", description="Scopeof the address type, ex. 'EMAIL'.")

    example: str | None = Field(None, description="Example value for the address.")


class AddressRelation(RABase):
    type: str = Field(
        description="The type of the address relation, ex 'org_unit' or 'person'."
    )

    relation_uuid: UUID = Field(
        description="UUID to be created. Will be autogenerated if not specified."
    )

    @validator("type")
    def validate_type(cls, value: str) -> str:
        if len(value) < 1:
            raise ValueError("AddressRelation.type, must have a value longer than 0.")

        supported_types = [mapping.ORG_UNIT, mapping.PERSON, mapping.ENGAGEMENT]

        if value not in supported_types:
            raise ValueError(
                f"AddressRelation.type only supports: {', '.join(supported_types)}"
            )

        return value


class AddressCreate(Validity, AddressRelation):
    """Model representing an address creation."""

    value: str = Field(description="The actual address value.")
    address_type: UUID = Field(description="Type of the address.")
    visibility: UUID = Field(description="Visibility for the address.")

    async def to_handler_dict(self) -> dict:
        legacy_dict = {
            mapping.TYPE: mapping.ADDRESS,
            mapping.VALUE: self.value,
            mapping.ADDRESS_TYPE: {mapping.UUID: str(self.address_type)},
            mapping.VISIBILITY: {mapping.UUID: str(self.visibility)},
            mapping.ORG: await get_configured_organisation(),
        }

        validity = {}
        if self.from_date:
            validity[mapping.FROM] = self.from_date.date().isoformat()

        if self.to_date:
            validity[mapping.TO] = self.to_date.date().isoformat()

        # Set the relation of the address
        match self.type:
            case mapping.ORG_UNIT:
                legacy_dict[mapping.ORG_UNIT] = {
                    mapping.UUID: str(self.relation_uuid),
                    mapping.VALIDITY: await self._get_org_unit_validity(
                        self.relation_uuid
                    ),
                }
            case mapping.PERSON:
                legacy_dict[mapping.PERSON] = {
                    mapping.UUID: str(self.relation_uuid),
                    mapping.VALIDITY: await self._get_person_validity(
                        self.relation_uuid
                    ),
                }
            case mapping.ENGAGEMENT:
                engagement_dict = {mapping.UUID: str(self.relation_uuid)}
                legacy_dict[mapping.ENGAGEMENT] = engagement_dict
            case _:
                supported_types = ", ".join(
                    [mapping.ORG_UNIT, mapping.PERSON, mapping.ENGAGEMENT]
                )
                raise ValueError(
                    f"Invalid address relation type, we only support: {supported_types}"
                )

        return {
            **legacy_dict,
            mapping.VALIDITY: validity,
        }

    @staticmethod
    async def _get_org_unit_validity(org_unit_uuid: UUID) -> dict | None:
        validity_dict = AddressCreate._get_lora_validity(
            await lora.Connector().organisationenhed.get(uuid=org_unit_uuid)
        )

        if not validity_dict:
            return None

        validity_from = validity_dict.get(mapping.FROM, None)
        validity_to = validity_dict.get(mapping.TO, None)

        return {
            mapping.FROM: validity_from.date().isoformat() if validity_from else None,
            mapping.TO: validity_to.date().isoformat() if validity_to else None,
        }

    @staticmethod
    async def _get_person_validity(person_uuid: UUID) -> dict | None:
        validity_dict = AddressCreate._get_lora_validity(
            await lora.Connector(
                virkningfra="-infinity", virkningtil="infinity"
            ).bruger.get(uuid=person_uuid)
        )

        if not validity_dict:
            return None

        validity_from = validity_dict.get(mapping.FROM, None)
        validity_to = validity_dict.get(mapping.TO, None)

        if not validity_dict:
            return None

        return {
            mapping.FROM: validity_from.date().isoformat() if validity_from else None,
            mapping.TO: validity_to.date().isoformat() if validity_to else None,
        }

    @staticmethod
    def _get_lora_validity(lora_object: dict | None) -> dict | None:
        if not isinstance(lora_object, dict):
            return None

        from_date: datetime.datetime | None = None
        to_date: datetime.datetime | None = None

        if "fratidspunkt" in lora_object.keys():
            from_date_current_value = lora_object.get("fratidspunkt", {}).get(
                "tidsstempeldatotid"
            )

            if from_date_current_value == "infinity":
                from_date = POSITIVE_INFINITY
            elif from_date_current_value == "-infinity":
                from_date = NEGATIVE_INFINITY
            else:
                from_date = dateutil.parser.isoparse(from_date_current_value)

        if "tiltidspunkt" in lora_object.keys():
            to_date_current_value = lora_object.get("tiltidspunkt", {}).get(
                "tidsstempeldatotid"
            )

            if to_date_current_value == "infinity":
                to_date = POSITIVE_INFINITY
            elif to_date_current_value == "-infinity":
                to_date = NEGATIVE_INFINITY
            else:
                to_date = datetime.datetime.fromisoformat(to_date_current_value)

        if not from_date and not to_date:
            return None

        return {
            mapping.FROM: from_date,
            mapping.TO: to_date,
        }


# Associations
# ------------
class Association(UUIDBase):
    """OS2mo association model."""


class AssociationCreate(Association):
    """Model representing an association creation."""

    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID
    employee: UUID
    association_type: UUID

    validity: RAValidity = Field(description="Validity range for the org-unit.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        return {
            "user_key": self.user_key,
            "org_unit": gen_uuid(self.org_unit),
            "person": gen_uuid(self.employee),
            "association_type": gen_uuid(self.association_type),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


# Classes
# -------
class ClassCreate(MOBase):
    """A MO Class create object."""

    type_: str = Field(
        "class", alias="type", description="The object type"
    )  # type is always "class"

    name: str = Field(description="Mo-class name.")
    user_key: str = Field(description="Extra info or uuid")
    org_uuid: UUID = Field(description="UUID of the related organisation.")
    facet_uuid: UUID = Field(description="UUID of the related facet.")

    scope: str | None = Field(description="Scope of the class.")
    published: str | None = Field(description="Published state of the class object.")
    parent_uuid: UUID | None = Field(description="UUID of the parent class.")
    example: str | None = Field(description="Example usage.")
    owner: UUID | None = Field(description="Owner of class")


# Employees
# ---------
class Employee(UUIDBase):
    """OS2Mo employee model."""


class EmployeeCreate(Employee):
    """Model representing an employee creation."""

    user_key: str | None = Field(description="Extra info or uuid.")
    givenname: NonEmptyString = Field(
        description="Givenname (firstname) of the employee."
    )
    surname: NonEmptyString = Field(description="Surname (lastname) of the employee.")

    cpr_number: str | None = Field(
        None, description="Danish CPR number of the employee."
    )

    def to_handler_dict(self) -> dict:
        return {
            "user_key": self.user_key,
            "givenname": self.givenname,
            "surname": self.surname,
            "cpr_no": self.cpr_number,
        }


class EmployeeTerminate(ValidityTerminate, Triggerless):
    """Model representing an employee termination."""

    uuid: UUID = Field(description="UUID for the employee we want to terminate.")


class EmployeeUpdate(UUIDBase):
    # name
    name: str | None = Field(None, description="New value for the name of the employee")

    # nickname_givenname
    nickname_firstname: str | None = Field(
        None,
        alias="nickname_givenname",
        description="New first-name value of the employee nickname.",
    )

    # nickname_surname
    nickname_lastname: str | None = Field(
        None,
        alias="nickname_surname",
        description="New last-name value of the employee nickname.",
    )

    # seniority
    seniority: str | None = Field(
        None, description="New seniority value of the employee."
    )

    # cpr_no
    cpr_no: str | None = Field(None, description="New seniority value of the employee.")

    # org
    org: Organisation | None = Field(
        None, description="Organization the employee belongs to."
    )

    # validity
    validity: Validity | None = Field(
        None,
        description="Validity range for the employee, "
        "for when the employee is accessible",
    )

    # user_key


# Engagements
# -----------
class EngagementTrigger(OrgFuncTrigger):
    """Model representing a mora-trigger, specific for engagements.

    Has the folling fields:
        request_type: str "Request type to do, ex CREATE, EDIT, TERMINATE or REFRESH. "

        request: MoraTriggerRequest  description="The Request for the trigger."

        role_type: str  description="Role type for the trigger, ex 'org_unit'."

        event_type: str  description="Trigger event-type. " "Ref: mora.mapping.EventType"

        uuid: UUID

        org_unit_uuid: UUID

        employee_id: Optional[UUID]
    """


class Engagement(UUIDBase):
    """Model representing an Engagement."""


class EngagementTerminate(ValidityTerminate, Triggerless):
    """Model representing an engagement termination(or rather end-date update)."""

    uuid: UUID = Field(description="UUID for the engagement we want to terminate.")

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afsluttet",
        }

    def get_engagement_trigger(self) -> EngagementTrigger:
        return EngagementTrigger(
            role_type=mapping.ENGAGEMENT,
            event_type=mapping.EventType.ON_BEFORE,
            uuid=self.uuid,
            org_unit_uuid=self.uuid,
            request_type=mapping.RequestType.TERMINATE,
            request=MoraTriggerRequest(
                type=mapping.ENGAGEMENT,
                uuid=self.uuid,
                validity=Validity(from_date=self.from_date, to_date=self.to_date),
            ),
        )


class EngagementCreate(Engagement):
    user_key: str | None = Field(description="Name or UUID of the related engagement.")
    org_unit: UUID = Field(description="The related org-unit object.")
    employee: UUID = Field(description="UUID of the related employee.")
    engagement_type: UUID
    job_function: UUID
    validity: RAValidity = Field(description="Validity of the engagement object.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        return {
            "user_key": self.user_key,
            "org_unit": gen_uuid(self.org_unit),
            "person": gen_uuid(self.employee),
            "engagement_type": gen_uuid(self.engagement_type),
            "job_function": gen_uuid(self.job_function),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


# EngagementsAssociations
# -----------------------

# Facets
# ------
class FacetCreate(UUIDBase):
    """Model representing a facet creation/update."""

    """Inherets uuid from UUIDBase"""

    user_key: str = Field(description="Facet name.")
    type_: str = Field(
        "facet", alias="type", description="The object type"
    )  # type is always "facet"

    org_uuid: UUID = Field(description="UUID of the related organisation.")
    parent_uuid: UUID | None = Field(description="UUID of the parent facet.")
    published: str | None = Field(description="Published state of the facet object.")


# ITSystems
# ---------

# ITUsers
# -------
class ITUser(UUIDBase):
    """OS2Mo IT-User model."""


class ITUserCreate(ITUser):
    """Model representing a IT-user creation."""

    # org_unit removed since it's never used and the usecase doesn't seem to be there.
    # Instead `person` is now required.

    type_: str = Field("it", alias="type", description="The object type.")
    user_key: str = Field(description="The IT user account name.")
    primary: UUID | None = Field(description="Primary field of the IT user object")
    itsystem: UUID = Field(description="Reference to the IT system for the IT user.")
    person: UUID = Field(description="Reference to the employee for the IT user.")
    validity: RAValidity = Field(description="Validity of the created IT user object.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        return {
            "type": self.type_,
            "user_key": self.user_key,
            "primary": gen_uuid(self.primary),
            "itsystem": gen_uuid(self.itsystem),
            "person": gen_uuid(self.person),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


class ITUserUpdate(ITUser):
    """Model representing a IT-user creation."""

    uuid: UUID = Field(description="UUID of the IT-user you want to update.")
    user_key: str | None = Field(description="The IT user account name.")
    primary: UUID | None = Field(description="Primary field of the IT user object")
    itsystem: UUID | None = Field(
        description="Reference to the IT system for the IT user."
    )
    validity: RAValidity = Field(description="Validity of the created IT user object.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        data_dict = {
            "user_key": self.user_key,
            "primary": gen_uuid(self.primary),
            "itsystem": gen_uuid(self.itsystem),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }
        return {k: v for k, v in data_dict.items() if v}


class ITUserTerminate(ValidityTerminate, Triggerless):
    """Model representing termination of it-user."""

    """(or rather end-date update for access to IT-system)."""

    uuid: UUID = Field(description="UUID for the it-user we want to terminate.")

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afsluttet",
        }

    def get_trigger(self) -> OrgFuncTrigger:
        return OrgFuncTrigger(
            role_type=mapping.IT,
            event_type=mapping.EventType.ON_BEFORE,
            uuid=self.uuid,
            org_unit_uuid=self.uuid,
            request_type=mapping.RequestType.TERMINATE,
            request=MoraTriggerRequest(
                type=mapping.IT,
                uuid=self.uuid,
                validity=Validity(from_date=self.from_date, to_date=self.to_date),
            ),
        )  # type: ignore


# KLEs
# ----

# Leave
# -----

# Managers
# --------


class Manager(UUIDBase):
    """Model representing a manager."""


class ManagerCreate(Manager):
    """Model for creating an employee of manager type."""

    user_key: str | None = Field(description="Extra info or uuid.")

    type_: str = Field("manager", alias="type", description="The object type.")

    person: UUID = Field(description="UUID of the manager as person.")

    responsibility: list[UUID] = Field(
        description="UUID of the managers responsibilities."
    )

    org_unit: UUID = Field(description="UUID of the managers organisation unit.")

    manager_type: UUID = Field(description="UUID of the managers type..")

    manager_level: UUID = Field(description="UUID of the managers level.")

    validity: RAValidity = Field(description="Validity range for the manager.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        responsibilities = [
            {"uuid": str(responsib)} for responsib in self.responsibility
        ]

        return {
            "user_key": self.user_key,
            "type": self.type_,
            "person": gen_uuid(self.person),
            "responsibility": responsibilities,
            "org_unit": gen_uuid(self.org_unit),
            "manager_type": gen_uuid(self.manager_type),
            "manager_level": gen_uuid(self.manager_level),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


# Organisational Units
# --------------------
class OrganisationUnitRefreshRead(BaseModel):
    """Payload model for organisation unit refresh mutation."""

    message: str = Field(description="Refresh message containing trigger responses.")


class OrgUnitTrigger(OrgFuncTrigger):
    """Model representing a mora-trigger, specific for organization-units."""


class OrganisationUnit(UUIDBase):
    """Model representing a Organization-Unit."""


class OrganisationUnitTerminate(ValidityTerminate, Triggerless):
    """Model representing a organization-unit termination."""

    uuid: UUID = Field(description="UUID for the org-unit we want to terminate.")

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationenhedgyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afslut enhed",
        }


class OrganisationUnitCreate(OrganisationUnit):
    """Model for creating org-units."""

    name: str = Field(description="Org-unit name.")
    user_key: str | None = Field(description="Extra info or uuid.")
    parent: UUID | None = Field(None, description="UUID of the related parent.")
    org_unit_type: UUID | None = Field(description="UUID of the type.")
    time_planning: UUID | None = Field(description="UUID of time planning.")
    org_unit_level: UUID | None = Field(description="UUID of unit level.")
    org_unit_hierarchy: UUID | None = Field(description="UUID of the unit hierarchy.")
    validity: RAValidity = Field(description="Validity range for the org-unit.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        return {
            "name": self.name,
            "user_key": self.user_key,
            "time_planning": gen_uuid(self.time_planning),
            "parent": gen_uuid(self.parent),
            "org_unit_type": gen_uuid(self.org_unit_type),
            "org_unit_level": gen_uuid(self.org_unit_level),
            "org_unit_hierarchy": gen_uuid(self.org_unit_hierarchy),
            "details": [],
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


# Related Units
# -------------

# Roles
# -----

# Health
# ------
class HealthRead(BaseModel):
    """Payload model for health."""

    identifier: str = Field(description="Short, unique key.")


# Files
# -----
@strawberry.enum
class FileStore(Enum):
    EXPORTS = 1
    INSIGHTS = 2


class FileRead(BaseModel):
    """Payload model for file download."""

    file_store: FileStore = Field(description="The file store the file is stored in.")
    file_name: str = Field(description="Name of the export file.")


# Configuration
# -------------


class ConfigurationRead(BaseModel):
    """Payload model for configuration."""

    key: str = Field(description="Settings key.")
