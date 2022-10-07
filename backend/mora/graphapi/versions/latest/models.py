# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import logging
from enum import Enum
from typing import Any
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import ConstrainedStr
from pydantic import Field
from pydantic import root_validator

from mora import common
from mora import exceptions
from mora import mapping
from mora.util import CPR
from mora.service.org import get_configured_organisation
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY
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
    """Model representing an entities validity range.

    Where both from and to dates can be optional.
    """

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
            key="Organisation unit must be set with either 'to' or both 'from' "
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


class AddressCreate(RAValidity):
    """Model representing an address creation.

    OBS: RAValidity is the validity where "from_date" is required.
    """

    value: str = Field(description="The actual address value.")
    address_type: UUID = Field(description="Type of the address.")
    visibility: UUID | None = Field(description="Visibility for the address.")

    # OBS: Only one of the 3 UUIDs are allowed to be set for the old logic to work
    org_unit: UUID | None = Field(description="UUID for the related org unit.")
    person: UUID | None = Field(description="UUID for the related person.")
    engagement: UUID | None = Field(description="UUID for the related engagement.")

    async def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None

            return {"uuid": str(uuid)}

        return {
            mapping.VALUE: self.value,
            mapping.ADDRESS_TYPE: gen_uuid(self.address_type),
            mapping.VISIBILITY: gen_uuid(self.visibility),
            mapping.VALIDITY: {
                mapping.FROM: self.from_date.date().isoformat(),
                mapping.TO: self.to_date.date().isoformat() if self.to_date else None,
            },
            mapping.ORG_UNIT: gen_uuid(self.org_unit),
            mapping.PERSON: gen_uuid(self.person),
            mapping.ENGAGEMENT: gen_uuid(self.engagement),
            mapping.ORG: await get_configured_organisation(),
        }


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


class AddressUpdate(Address):
    """Model representing an association update."""

    uuid: UUID = Field(description="UUID of the association we want to update.")
    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID | None = Field(description="Org-unit uuid.")
    employee: UUID | None = Field(description="Employee uuid.")
    address_type: UUID | None = Field(description="Address type uuid.")
    engagement: UUID | None = Field(description="Engagement uuid.")
    value: str | None = Field(description="Info related to the specific addresstype.")
    visibility: UUID | None = Field(description="UUID for visibility of the address.")

    validity: RAValidity = Field(description="Validity range for the address.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        data_dict = {
            "uuid": self.uuid,
            "user_key": self.user_key,
            "org_unit": gen_uuid(self.org_unit),
            "person": gen_uuid(self.employee),
            "address_type": gen_uuid(self.address_type),
            "engagement": gen_uuid(self.engagement),
            "value": self.value,
            "visibility": gen_uuid(self.visibility),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }
        return {k: v for k, v in data_dict.items() if v}


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


class AssociationUpdate(Association):
    """Model representing an association update."""

    uuid: UUID = Field(description="UUID of the association we want to update.")
    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID | None = Field(description="org-unit uuid.")
    employee: UUID | None = Field(description="Employee uuid.")
    association_type: UUID | None = Field(description="Association type uuid.")

    validity: RAValidity = Field(description="Validity range for the org-unit.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        data_dict = {
            "uuid": self.uuid,
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
        return {k: v for k, v in data_dict.items() if v}


class AssociationTerminate(ValidityTerminate, Triggerless):
    """Model representing an association termination(or rather end-date update)."""

    uuid: UUID = Field(description="UUID for the association we want to terminate.")

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afsluttet",
        }

    def get_association_trigger(self) -> OrgFuncTrigger:
        return OrgFuncTrigger(
            role_type=mapping.ASSOCIATION,
            event_type=mapping.EventType.ON_BEFORE,
            uuid=self.uuid,
            org_unit_uuid=self.uuid,
            request_type=mapping.RequestType.TERMINATE,
            request=MoraTriggerRequest(
                type=mapping.ASSOCIATION,
                uuid=self.uuid,
                validity=Validity(from_date=self.from_date, to_date=self.to_date),
            ),
        )


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


class EmployeeUpdate(RAValidity):
    # Error messages returned by the @root_validator
    _ERR_INVALID_NAME = (
        "EmployeeUpdate.name is only allowed to be set, if "
        '"given_name" & "surname" are None.'
    )
    _ERR_INVALID_NICKNAME = (
        "EmployeeUpdate.nickname is only allowed to be set, if "
        '"nickname_given_name" & "nickname_surname" are None.'
    )

    uuid: UUID = Field(description="UUID of the employee to be updated.")

    user_key: str | None = Field(
        description="Short, unique key for the employee (defaults to object UUID on creation)."
    )

    name: str | None = Field(None, description="New value for the name of the employee")

    given_name: str | None = Field(
        None,
        description="New first-name value of the employee nickname.",
    )

    surname: str | None = Field(
        None,
        description="New last-name value of the employee nickname.",
    )

    nickname: str | None = Field(
        None,
        description="New nickname value of the employee nickname.",
    )

    nickname_given_name: str | None = Field(
        None,
        description="New nickname given-name value of the employee nickname.",
    )

    nickname_surname: str | None = Field(
        None,
        description="New nickname sur-name value of the employee nickname.",
    )

    seniority: datetime.date | None = Field(
        # OBS: backend/mora/service/employee.py:96 for why type is datetime.date
        None,
        description="New seniority value of the employee.",
    )

    cpr_no: CPR | None = Field(None, description="New danish CPR No. of the employee.")

    @root_validator
    def validation(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("name") and (values.get("given_name") or values.get("surname")):
            raise ValueError(cls._ERR_INVALID_NAME)

        if values.get("nickname") and (
            values.get("nickname_given_name") or values.get("nickname_surname")
        ):
            raise ValueError(cls._ERR_INVALID_NICKNAME)

        return values

    def no_values(self) -> bool:
        if self.to_date:
            return False

        if self.name or self.given_name or self.surname:
            return False

        if self.nickname or self.nickname_given_name or self.nickname_surname:
            return False

        if self.seniority or self.cpr_no:
            return False

        return True

    def to_handler_dict(self) -> dict:
        data_dict = {
            mapping.USER_KEY: self.user_key,
            mapping.VALIDITY: {
                mapping.FROM: self.from_date.date().isoformat(),
                mapping.TO: self.to_date.date().isoformat() if self.to_date else None,
            },
            mapping.NAME: self.name,
            mapping.GIVENNAME: self.given_name,
            mapping.SURNAME: self.surname,
            mapping.NICKNAME: self.nickname,
            mapping.NICKNAME_GIVENNAME: self.nickname_given_name,
            mapping.NICKNAME_SURNAME: self.nickname_surname,
            mapping.SENIORITY: self.seniority.isoformat() if self.seniority else None,
            mapping.CPR_NO: self.cpr_no,
        }

        return {
            mapping.TYPE: mapping.EMPLOYEE,
            mapping.UUID: str(self.uuid),
            mapping.DATA: {k: v for k, v in data_dict.items() if v},
        }


class EmployeeUpdateResponse(UUIDBase):
    pass


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


class EngagementUpdate(Engagement):
    uuid: UUID = Field(description="UUID of the Engagement you want to update.")
    user_key: str | None = Field(description="Name or UUID of the related engagement.")
    org_unit: UUID | None = Field(description="The related org-unit object.")
    employee: UUID | None = Field(description="UUID of the related employee.")
    engagement_type: UUID | None = Field(description="UUID of the engagement type.")
    job_function: UUID | None = Field(description="UUID of the job function.")
    validity: RAValidity = Field(description="Validity of the engagement object.")

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        data_dict = {
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
        return {k: v for k, v in data_dict.items() if v}


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

    manager_level: UUID = Field(description="UUID of the managers level.")

    manager_type: UUID = Field(description="UUID of the managers type..")

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
            "manager_level": gen_uuid(self.manager_level),
            "manager_type": gen_uuid(self.manager_type),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


class ManagerUpdate(Manager):
    """Model for updating a manager."""

    uuid: UUID = Field(description="UUID of the manager to be updated.")

    validity: RAValidity = Field(
        description="Validity range for the manager to be updated."
    )

    user_key: str | None = Field(description="Extra info or uuid.")

    person: UUID | None = Field(
        description="UUID of the manager as person to be updated."
    )

    responsibility: list[UUID] | None = Field(
        description="UUID of the managers responsibilities to be updated."
    )

    org_unit: UUID | None = Field(
        description="UUID of the managers organisation unit to be updated."
    )
    manager_type: UUID | None = Field(
        description="UUID of the managers type to be updated."
    )

    manager_level: UUID | None = Field(
        description="UUID of the managers level to be updated."
    )

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        data_dict: dict = {
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
            "user_key": self.user_key,
            "person": gen_uuid(self.person),
            "responsibility": self.responsibility,
            "org_unit": gen_uuid(self.org_unit),
            "manager_type": gen_uuid(self.manager_type),
            "manager_level": gen_uuid(self.manager_level),
        }
        if self.responsibility:
            data_dict["responsibility"] = [
                {"uuid": str(responsib)} for responsib in self.responsibility
            ]

        return {k: v for k, v in data_dict.items() if v}


class ManagerTerminate(ValidityTerminate, Triggerless):
    """Model representing a manager termination."""

    uuid: UUID = Field(description="UUID of the manager we want to terminate.")

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationfunktiongyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afsluttet",
        }

    def get_manager_trigger(self) -> OrgFuncTrigger:
        return OrgFuncTrigger(
            role_type=mapping.MANAGER,
            event_type=mapping.EventType.ON_BEFORE,
            uuid=self.uuid,
            org_unit_uuid=self.uuid,
            request_type=mapping.RequestType.TERMINATE,
            request=MoraTriggerRequest(
                type=mapping.MANAGER,
                uuid=self.uuid,
                validity=Validity(from_date=self.from_date, to_date=self.to_date),
            ),
        )


# Organisational Units
# --------------------
class OrganisationUnitRefreshRead(BaseModel):
    """Payload model for organisation unit refresh mutation."""

    message: str = Field(description="Refresh message containing trigger responses.")


class OrgUnitTrigger(OrgFuncTrigger):
    """Model representing a mora-trigger, specific for organisation units."""


class OrganisationUnit(UUIDBase):
    """Model representing an organisation unit."""


class OrganisationUnitTerminate(ValidityTerminate, Triggerless):
    """Model representing an organisation unit termination."""

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


class OrganisationUnitUpdate(OrganisationUnit):
    """Model for updating an organisation unit."""

    uuid: UUID = Field(description="UUID of the organisation unit to be updated.")

    validity: RAValidity = Field(
        description="Validity range for the organisation unit to be updated."
    )

    name: str | None = Field(description="Name of the organisation unit to be updated.")

    user_key: str | None = Field(description="Extra info or uuid.")

    parent: UUID | None = Field(
        description="UUID of the organisation units related parent to be updated."
    )

    org_unit_type: UUID | None = Field(
        description="UUID of the organisation units type to be updated."
    )

    org_unit_level: UUID | None = Field(
        description="UUID of the organisation units level to be updated."
    )

    org_unit_hierarchy: UUID | None = Field(
        description="UUID of organisation units hierarchy to be updated."
    )

    time_planning: UUID | None = Field(
        description="UUID of organisation units time planning to be updated."
    )

    def to_handler_dict(self) -> dict:
        def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
            if uuid is None:
                return None
            return {"uuid": str(uuid)}

        data_dict: dict = {
            "uuid": str(self.uuid),
            "name": self.name,
            "user_key": self.user_key,
            "parent": gen_uuid(self.parent),
            "org_unit_type": gen_uuid(self.org_unit_type),
            "org_unit_level": gen_uuid(self.org_unit_level),
            "org_unit_hierarchy": gen_uuid(self.org_unit_hierarchy),
            "time_planning": gen_uuid(self.time_planning),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }

        return {k: v for k, v in data_dict.items() if v}


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
