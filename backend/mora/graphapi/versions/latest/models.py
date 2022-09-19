# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import logging
from enum import Enum
from typing import Any
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import Field

from mora import common
from mora import exceptions
from mora import mapping
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY
from ramodels.mo import OpenValidity
from ramodels.mo import Validity as RAValidity
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import UUIDBase

logger = logging.getLogger(__name__)


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


class Address(UUIDBase):
    """Address (detail) model."""


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
        )

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afsluttet",
        }


# Associations
# ------------

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


class EmployeeCreate(BaseModel):
    """Model representing an employee creation."""

    name: str = Field(description="Full name of the employee.")

    cpr_no: str = Field(description="Danish CPR number of the employee.")
    org: Organisation = Field(
        Organisation(),
        description="The organization the new employee will be created under.",
    )


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


class EngagementModel(UUIDBase):
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


# EngagementsAssociations
# -----------------------

# Facets
# ------

# ITSystems
# ---------

# ITUsers
# -------
class ITUserModel(UUIDBase):
    """Model representing an Engagement."""

    pass


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
        )


# KLEs
# ----

# Leave
# -----

# Managers
# --------

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
