# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import logging
from enum import Enum
from textwrap import dedent
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
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY
from ramodels.mo import OpenValidity
from ramodels.mo import Validity as RAValidity
from ramodels.mo._shared import UUIDBase

logger = logging.getLogger(__name__)


# Various
# -------
def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
    if uuid is None:
        return None
    return {"uuid": str(uuid)}


class NonEmptyString(ConstrainedStr):
    min_length: int = 1


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
        exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
            key="Organisation unit must be set with either 'to' or both 'from' "
            "and 'to'",
            unit={
                "from": self.from_date.isoformat() if self.from_date else None,
                "to": self.to_date.isoformat() if self.to_date else None,
            },
        )

    def get_terminate_effect_from_date(self) -> datetime.datetime:
        if not self.from_date or not isinstance(self.from_date, datetime.datetime):
            exceptions.ErrorCodes.V_MISSING_START_DATE()

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


class AddressUpsert(UUIDBase):
    """Model representing an address creation/update commonalities."""

    # OBS: Only one of the two UUIDs are allowed to be set for the old logic to work
    org_unit: UUID | None = Field(description="UUID for the related org unit.")
    person: UUID | None = Field(description="UUID for the related person.")
    # TODO: Remove employee in a future version of GraphQL
    employee: UUID | None = Field(description="UUID for the related person.")

    engagement: UUID | None = Field(description="UUID for the related engagement.")

    visibility: UUID | None = Field(description="Visibility for the address.")
    validity: RAValidity = Field(description="Validity range for the org-unit.")
    user_key: str | None = Field(description="Extra info or uuid.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "user_key": self.user_key,
            "visibility": gen_uuid(self.visibility),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
            "org_unit": gen_uuid(self.org_unit),
            "person": gen_uuid(self.person) or gen_uuid(self.employee),
            "engagement": gen_uuid(self.engagement),
        }


class AddressCreate(AddressUpsert):
    """Model representing an address creation."""

    value: str = Field(description="The actual address value.")
    address_type: UUID = Field(description="Type of the address.")

    @root_validator
    def verify_addr_relation(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Verifies that at exactly one address relation field has been set."""
        number_of_uuids = len(
            list(
                filter(
                    lambda x: x is not None,
                    [
                        values.get("org_unit"),
                        values.get("person"),
                        values.get("employee"),
                    ],
                )
            )
        )

        if number_of_uuids != 1:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                f"Must supply exactly one {mapping.ORG_UNIT} or {mapping.PERSON} UUID"
            )

        return values

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["value"] = self.value
        data_dict["address_type"] = gen_uuid(self.address_type)
        return data_dict


class AddressUpdate(AddressUpsert):
    """Model representing an association update."""

    uuid: UUID = Field(description="UUID of the address we want to update.")
    value: str | None = Field(description="The actual address value.")
    address_type: UUID | None = Field(description="Type of the address.")

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["value"] = self.value
        data_dict["address_type"] = gen_uuid(self.address_type)
        return {k: v for k, v in data_dict.items() if v}


class AddressTerminate(ValidityTerminate):
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


# Associations
# ------------
class AssociationUpsert(UUIDBase):
    user_key: str | None = Field(description="Extra info or uuid.")
    primary: UUID | None = Field(description="Primary field of the association")
    validity: RAValidity = Field(description="Validity range for the org-unit.")

    person: UUID | None = Field(description="Employee uuid.")
    # TODO: Remove employee in a future version of GraphQL
    employee: UUID | None = Field(description="Employee uuid.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "user_key": self.user_key,
            "primary": gen_uuid(self.primary),
            "person": gen_uuid(self.person) or gen_uuid(self.employee),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


class AssociationCreate(AssociationUpsert):
    """Model representing an association creation."""

    org_unit: UUID = Field(description="org-unit uuid.")
    association_type: UUID = Field(description="Association type uuid.")

    @root_validator
    def verify_person_or_employee(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Verifies that either person or employee is set."""
        person_uuid = values.get("person")
        employee_uuid = values.get("employee")
        if person_uuid and employee_uuid:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Can only set one of 'person' and 'employee'"
            )
        if person_uuid is None and employee_uuid is None:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Must set one of 'person' and 'employee'"
            )
        return values

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["org_unit"] = gen_uuid(self.org_unit)
        data_dict["association_type"] = gen_uuid(self.association_type)
        return data_dict


class AssociationUpdate(AssociationUpsert):
    """Model representing an association update."""

    uuid: UUID = Field(description="UUID of the association we want to update.")
    org_unit: UUID | None = Field(description="org-unit uuid.")
    association_type: UUID | None = Field(description="Association type uuid.")

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["org_unit"] = gen_uuid(self.org_unit)
        data_dict["association_type"] = gen_uuid(self.association_type)
        return {k: v for k, v in data_dict.items() if v}


class AssociationTerminate(ValidityTerminate):
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


# Employees
# ---------
class EmployeeUpsert(UUIDBase):
    _ERR_INVALID_NICKNAME = "'nickname' is only allowed to be set, if 'nickname_given_name' & 'nickname_surname' are None."
    _ERR_INVALID_CPR_NUMBER = (
        "'cpr_number' is only allowed to be set, if 'cpr_no' is None."
    )

    user_key: str | None = Field(
        description="Short, unique key for the employee (defaults to object UUID on creation)."
    )

    # TODO: Remove this in the future
    name: str | None = Field(None, description="Combined name of the employee")

    # TODO: Remove this in the future
    nickname: str | None = Field(
        None,
        description="Nickname (combined) of the employee.",
    )
    nickname_given_name: str | None = Field(
        None,
        description="Nickname givenname (firstname) of the employee.",
    )
    nickname_surname: str | None = Field(
        None,
        description="Nickname surname (lastname) of the employee.",
    )

    @root_validator
    def combined_or_split_nickname(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("nickname") and (
            values.get("nickname_given_name") or values.get("nickname_surname")
        ):
            raise ValueError(cls._ERR_INVALID_NICKNAME)

        return values

    seniority: datetime.date | None = Field(
        # OBS: backend/mora/service/employee.py:96 for why type is datetime.date
        None,
        description="New seniority value of the employee.",
    )

    # TODO: This should fit the create, not cpr_no vs cpr_number
    cpr_no: CPR | None = Field(None, description="New danish CPR No. of the employee.")

    # TODO: This should take the CPR scalar type
    cpr_number: str | None = Field(
        None, description="Danish CPR number of the employee."
    )

    @root_validator
    def combined_or_split_name(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("cpr_no") and values.get("cpr_number"):
            raise ValueError(cls._ERR_INVALID_CPR_NUMBER)

        return values

    def to_handler_dict(self) -> dict:
        data_dict = {
            mapping.UUID: self.uuid,
            mapping.USER_KEY: self.user_key,
            mapping.NAME: self.name,
            mapping.NICKNAME: self.nickname,
            mapping.NICKNAME_GIVENNAME: self.nickname_given_name,
            mapping.NICKNAME_SURNAME: self.nickname_surname,
            mapping.SENIORITY: self.seniority.isoformat() if self.seniority else None,
            mapping.CPR_NO: self.cpr_number or self.cpr_no,
        }
        return data_dict


class EmployeeCreate(EmployeeUpsert):
    """Model representing an employee creation."""

    _ERR_INVALID_GIVEN_NAME = (
        "'given_name' is only allowed to be set, if 'given_name' is None."
    )
    _ERR_INVALID_NAME = (
        "'name' is only allowed to be set, if 'given_name' & 'surname' are None."
    )

    given_name: NonEmptyString | None = Field(
        None, description="Givenname (firstname) of the employee."
    )
    # TODO: Remove this in the future
    givenname: NonEmptyString | None = Field(
        description="Givenname (firstname) of the employee."
    )
    surname: NonEmptyString = Field(description="Surname (lastname) of the employee.")

    @root_validator
    def only_one_givenname(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("given_name") and values.get("givenname"):
            raise ValueError(cls._ERR_INVALID_GIVEN_NAME)

        return values

    @root_validator
    def combined_or_split_name(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("name") and (
            values.get("given_name") or values.get("givenname") or values.get("surname")
        ):
            raise ValueError(cls._ERR_INVALID_NAME)

        return values

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict[mapping.GIVENNAME] = self.given_name or self.givenname
        data_dict[mapping.SURNAME] = self.surname
        return data_dict


class EmployeeUpdate(EmployeeUpsert, OpenValidity):
    # Error messages returned by the @root_validator
    _ERR_INVALID_NAME = (
        "EmployeeUpdate.name is only allowed to be set, if "
        '"given_name" & "surname" are None.'
    )

    uuid: UUID = Field(description="UUID of the employee to be updated.")

    given_name: str | None = Field(
        None,
        description="New first-name value of the employee nickname.",
    )
    # TODO: Remove this in the future
    givenname: str | None = Field(description="Givenname (firstname) of the employee.")
    surname: str | None = Field(
        None,
        description="New last-name value of the employee nickname.",
    )
    validity: RAValidity | None = Field(description="Validity range for the change.")

    @root_validator
    def combined_or_split_name(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("name") and (
            values.get("given_name") or values.get("givenname") or values.get("surname")
        ):
            raise ValueError(cls._ERR_INVALID_NAME)

        return values

    @root_validator
    def validity_check(cls, values: dict[str, Any]) -> dict[str, Any]:
        validity = values.get("validity")
        dates = values.get("from_date") or values.get("to_date")
        if validity and dates:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Can only set one of 'validity' and 'from_date' / 'to_date'"
            )
        if validity is None and dates is None:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Must set one of 'validity' and 'from_date' / 'to_date'"
            )
        return values

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict[mapping.GIVENNAME] = self.given_name or self.givenname
        data_dict[mapping.SURNAME] = self.surname
        data_dict[mapping.VALIDITY] = self.validity or {
            mapping.FROM: self.from_date.date().isoformat() if self.from_date else None,
            mapping.TO: self.to_date.date().isoformat() if self.to_date else None,
        }
        return {k: v for k, v in data_dict.items() if v}


class EmployeeTerminate(ValidityTerminate):
    """Model representing an employee termination."""

    uuid: UUID = Field(description="UUID for the employee we want to terminate.")


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


class EngagementTerminate(ValidityTerminate):
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


EXTENSION_FIELD_DESCRIPTION: str = dedent(
    """\
            Arbitrary value extension fields.

            A collection of field for storing arbitrary extra data.
            Can be used for extraordinary occasions when no standardized field to model the data exists.

        """
)


class EngagementUpsert(UUIDBase):
    user_key: str | None = Field(description="Name or UUID of the related engagement.")
    primary: UUID | None = Field(description="Primary field of the engagement")
    validity: RAValidity = Field(description="Validity of the engagement object.")

    extension_1: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_2: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_3: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_4: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_5: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_6: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_7: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_8: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_9: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)
    extension_10: str | None = Field(description=EXTENSION_FIELD_DESCRIPTION)

    # TODO: Remove employee in a future version of GraphQL
    employee: UUID | None = Field(description="UUID of the related employee.")
    person: UUID | None = Field(description="UUID of the related employee.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "user_key": self.user_key,
            "primary": gen_uuid(self.primary),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
            "person": gen_uuid(self.person) or gen_uuid(self.employee),
            "extension_1": self.extension_1,
            "extension_2": self.extension_2,
            "extension_3": self.extension_3,
            "extension_4": self.extension_4,
            "extension_5": self.extension_5,
            "extension_6": self.extension_6,
            "extension_7": self.extension_7,
            "extension_8": self.extension_8,
            "extension_9": self.extension_9,
            "extension_10": self.extension_10,
        }


class EngagementCreate(EngagementUpsert):
    org_unit: UUID = Field(description="The related org-unit object.")
    engagement_type: UUID
    job_function: UUID

    @root_validator
    def verify_person_or_employee(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Verifies that either person or employee is set."""
        person_uuid = values.get("person")
        employee_uuid = values.get("employee")
        if person_uuid and employee_uuid:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Can only set one of 'person' and 'employee'"
            )
        if person_uuid is None and employee_uuid is None:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Must set one of 'person' and 'employee'"
            )
        return values

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["org_unit"] = gen_uuid(self.org_unit)
        data_dict["engagement_type"] = gen_uuid(self.engagement_type)
        data_dict["job_function"] = gen_uuid(self.job_function)
        return data_dict


class EngagementUpdate(EngagementUpsert):
    uuid: UUID = Field(description="UUID of the Engagement you want to update.")
    org_unit: UUID | None = Field(description="The related org-unit object.")
    engagement_type: UUID | None = Field(description="UUID of the engagement type.")
    job_function: UUID | None = Field(description="UUID of the job function.")

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["org_unit"] = gen_uuid(self.org_unit)
        data_dict["engagement_type"] = gen_uuid(self.engagement_type)
        data_dict["job_function"] = gen_uuid(self.job_function)
        return {k: v for k, v in data_dict.items() if v}


# EngagementsAssociations
# -----------------------


# ITSystems
# ---------


# ITUsers
# -------
class ITUserUpsert(UUIDBase):
    primary: UUID | None = Field(description="Primary field of the IT user object")
    person: UUID | None = Field(
        description="Reference to the employee for the IT user (if any)."
    )
    org_unit: UUID | None = Field(
        description="Reference to the organisation unit of the IT user (if any)."
    )
    engagement: UUID | None = Field(
        description="Reference to the engagement of the IT user (if any)."
    )
    validity: RAValidity = Field(description="Validity of the created IT user object.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "primary": gen_uuid(self.primary),
            "person": gen_uuid(self.person),
            "org_unit": gen_uuid(self.org_unit),
            "engagement": gen_uuid(self.engagement),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


class ITUserCreate(ITUserUpsert):
    """Model representing a IT-user creation."""

    user_key: str = Field(description="The IT user account name.")
    itsystem: UUID = Field(description="Reference to the IT system for the IT user.")

    @root_validator
    def validation(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Verifies that at only one of org_unit and employee field has been set."""
        if (values.get("person") and values.get("org_unit")) or (
            not values.get("person") and not values.get("org_unit")
        ):
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Exactly 1 of the fields {mapping.ORG_UNIT} or {mapping.PERSON} must be set"
            )
        return values

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["type"] = "it"
        data_dict["user_key"] = self.user_key
        data_dict["itsystem"] = gen_uuid(self.itsystem)
        return data_dict


class ITUserUpdate(ITUserUpsert):
    """Model representing a IT-user creation."""

    uuid: UUID = Field(description="UUID of the IT-user you want to update.")

    user_key: str | None = Field(description="The IT user account name.")
    itsystem: UUID | None = Field(
        description="Reference to the IT system for the IT user."
    )

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["user_key"] = self.user_key
        data_dict["itsystem"] = gen_uuid(self.itsystem)
        return {k: v for k, v in data_dict.items() if v}


class ITUserTerminate(ValidityTerminate):
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
# --------
class KLECreate(UUIDBase):
    """Model for creating a KLE annotation."""

    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID = Field(description="UUID of the organisation unit of the KLE.")
    kle_aspects: list[UUID] = Field(description="List of UUIDs of the KLE aspects.")
    kle_number: UUID = Field(description="UUID of the KLE number.")
    validity: RAValidity = Field(description="Validity range for the KLE.")

    def to_handler_dict(self) -> dict:
        aspects = [{"uuid": str(aspect)} for aspect in self.kle_aspects]
        return {
            "uuid": str(self.uuid),
            "user_key": self.user_key,
            "kle_number": gen_uuid(self.kle_number),
            "kle_aspect": aspects,
            "org_unit": gen_uuid(self.org_unit),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


class KLEUpdate(UUIDBase):
    """Model for updating a KLE annotation."""

    uuid: UUID = Field(description="UUID of the manager to be updated.")

    user_key: str | None = Field(description="Extra info or uuid.")

    kle_number: UUID | None = Field(
        description="UUID of the manager as person to be updated."
    )

    kle_aspects: list[UUID] | None = Field(
        description="UUID of the managers responsibilities to be updated."
    )

    org_unit: UUID | None = Field(
        description="UUID of the managers organisation unit to be updated."
    )

    validity: RAValidity = Field(
        description="Validity range for the manager to be updated."
    )

    def to_handler_dict(self) -> dict:
        data_dict: dict = {
            "user_key": self.user_key,
            "kle_number": gen_uuid(self.kle_number),
            "kle_aspect": self.kle_aspects,
            "org_unit": gen_uuid(self.org_unit),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }
        if self.kle_aspects:
            data_dict["kle_aspect"] = [
                {"uuid": str(aspect)} for aspect in self.kle_aspects
            ]

        return {k: v for k, v in data_dict.items() if v}


class KLETerminate(ValidityTerminate):
    """Model representing a KLE termination."""

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

    def get_kle_trigger(self) -> OrgFuncTrigger:
        return OrgFuncTrigger(
            role_type=mapping.KLE,
            event_type=mapping.EventType.ON_BEFORE,
            uuid=self.uuid,
            org_unit_uuid=self.uuid,
            request_type=mapping.RequestType.TERMINATE,
            request=MoraTriggerRequest(
                type=mapping.KLE,
                uuid=self.uuid,
                validity=Validity(from_date=self.from_date, to_date=self.to_date),
            ),
        )


# Leaves
# --------
class LeaveCreate(UUIDBase):
    """Model for creating a leave."""

    person: UUID = Field(description="UUID of the person.")
    # Engagement seems to be optional, but it's not possible to create a Leave without it.
    # Therefore it's set to required
    engagement: UUID = Field(description="UUID of the related engagement.")
    leave_type: UUID = Field(description="UUID of the leave type")
    validity: RAValidity = Field(description="Validity range for the leave.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": str(self.uuid),
            "person": gen_uuid(self.person),
            "engagement": gen_uuid(self.engagement),
            "leave_type": gen_uuid(self.leave_type),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


# Managers
# --------
class ManagerCreate(UUIDBase):
    """Model for creating an employee of manager type."""

    user_key: str | None = Field(description="Extra info or uuid.")
    person: UUID | None = Field(description="UUID of the manager as person.")
    responsibility: list[UUID] = Field(
        description="UUID of the managers responsibilities."
    )
    org_unit: UUID = Field(description="UUID of the managers organisation unit.")
    manager_level: UUID = Field(description="UUID of the managers level.")
    manager_type: UUID = Field(description="UUID of the managers type..")
    validity: RAValidity = Field(description="Validity range for the manager.")

    def to_handler_dict(self) -> dict:
        responsibilities = [
            {"uuid": str(responsib)} for responsib in self.responsibility
        ]

        return {
            "uuid": str(self.uuid),
            "user_key": self.user_key,
            "type": "manager",
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


class ManagerUpdate(UUIDBase):
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


class ManagerTerminate(ValidityTerminate):
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


class OrganisationUnitTerminate(ValidityTerminate):
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


class OrganisationUnitCreate(UUIDBase):
    """Model for creating org-units."""

    name: str = Field(description="Org-unit name.")
    user_key: str | None = Field(description="Extra info or uuid.")
    parent: UUID | None = Field(None, description="UUID of the related parent.")
    org_unit_type: UUID = Field(description="UUID of the type.")
    time_planning: UUID | None = Field(description="UUID of time planning.")
    org_unit_level: UUID | None = Field(description="UUID of unit level.")
    org_unit_hierarchy: UUID | None = Field(description="UUID of the unit hierarchy.")
    validity: RAValidity = Field(description="Validity range for the org-unit.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": str(self.uuid),
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


class OrganisationUnitUpdate(UUIDBase):
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


# Roles
# -----


class RoleCreate(UUIDBase):
    """Model for creating role."""

    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID = Field(description="UUID of the org_unit")
    person: UUID = Field(description="UUID of the person")
    role_type: UUID = Field(description="UUID of the role type")
    validity: RAValidity = Field(description="Validity range for the role.")

    def to_handler_dict(self) -> dict:
        return {
            "user_key": self.user_key,
            "org_unit": gen_uuid(self.org_unit),
            "person": gen_uuid(self.person),
            "role_type": gen_uuid(self.role_type),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


# Files
# -----
@strawberry.enum(
    description=dedent(
        """\
    Enum for all the supported file stores.

    File stores can be thought of a separate folders or drives in desktop computing.
    """
    )
)
class FileStore(Enum):
    EXPORTS = strawberry.enum_value(
        1,
        description=dedent(
            """\
        The exports file store.

        Used to hold files uploaded by export jobs.
        """
        ),
    )
    INSIGHTS = strawberry.enum_value(
        2,
        description=dedent(
            """\
        The insights file store.

        Used to hold data-files supporting the insights functionality in OS2mo.
        """
        ),
    )
