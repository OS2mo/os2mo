# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import logging
from enum import Enum
from typing import Any
from typing import Optional
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import Field
from pydantic import validator

from mora import common
from mora import exceptions
from mora import lora
from mora import mapping
from mora import util
from mora.util import NEGATIVE_INFINITY
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY
from ramodels.mo import OpenValidity
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import UUIDBase

logger = logging.getLogger(__name__)


@strawberry.enum
class FileStore(Enum):
    EXPORTS = 1
    INSIGHTS = 2


class HealthRead(BaseModel):
    """Payload model for health."""

    identifier: str = Field(description="Short, unique key.")


class FileRead(BaseModel):
    """Payload model for file download."""

    file_store: FileStore = Field(description="The file store the file is stored in.")
    file_name: str = Field(description="Name of the export file.")


class OrganisationUnitRefreshRead(BaseModel):
    """Payload model for organisation unit refresh mutation."""

    message: str = Field(description="Refresh message containing trigger responses.")


class ConfigurationRead(BaseModel):
    """Payload model for configuration."""

    key: str = Field(description="Settings key.")


class Validity(OpenValidity):
    """Model representing an entities validity range."""

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class ValidityTerminate(Validity):
    to_date: datetime.datetime = Field(
        util.NEGATIVE_INFINITY,
        # OBS: Above line should not be necessary, but due to mypy and strawberry not
        # working together properly, this is required in order to prevent mypy from
        # complaining about the strawberry inputs in "mora.graphapi.inputs" (and types)
        alias="to",
        description="When the validity should end " "- required when terminating",
    )

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
                "{!r} is not at midnight!".format(self.from_date.isoformat()),
            )

        return self.from_date

    def get_terminate_effect_to_date(self) -> datetime.datetime:
        if not self.to_date:
            return POSITIVE_INFINITY

        if self.to_date.time() != datetime.time.min:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "{!r} is not at midnight!".format(self.to_date.isoformat()),
            )

        return self.to_date + ONE_DAY


class MoraTriggerRequest(BaseModel):
    """Model representing a MoRa Trigger Request."""

    type: str = Field(description="Type of the request, ex. 'org_unit'.")

    uuid: UUID = Field(
        description="UUID for the entity accessed in the request. "
        "Ex type=ORG_UNIT, then this UUID will be the UUID of the ORG_UNIT"
    )

    validity: Validity = Field(description="Validity for the specified UUID.")


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
    triggerless: Optional[bool] = Field(
        description="Flag specifying if triggers should not be invoked, if true.",
        default=False,
    )


class OrgFuncTrigger(MoraTrigger):
    """General model for Mora-Organization-Function triggers."""

    org_unit_uuid: UUID = Field(
        description="UUID for the organization unit in question."
    )

    employee_id: Optional[UUID] = Field(
        None, description="OrgFunc Related employee UUID."
    )


class OrgUnitTrigger(OrgFuncTrigger):
    """Model representing a mora-trigger, specific for organization-units."""

    pass


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

    pass


class Organisation(UUIDBase):
    """Model representing an Organization."""

    pass


class OrganisationUnit(UUIDBase):
    """Model representing a Organization-Unit."""

    pass


class OrganisationUnitTerminate(OrganisationUnit, ValidityTerminate, Triggerless):
    """Model representing a organization-unit termination."""

    def get_lora_payload(self) -> dict:
        return {
            "tilstande": {
                "organisationenhedgyldighed": [
                    {"gyldighed": "Inaktiv", "virkning": self.get_termination_effect()}
                ]
            },
            "note": "Afslut enhed",
        }


class EngagementModel(UUIDBase):
    """Model representing an Engagement."""

    pass


class EngagementTerminate(EngagementModel, ValidityTerminate, Triggerless):
    """Model representing an engagement termination(or rather end-date update)."""

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


class AddressTrigger(OrgFuncTrigger):
    """Model representing a mora-trigger, specific for addresses."""

    pass


class Address(UUIDBase):
    """Address (detail) model."""

    pass


class AddressType(MOBase):
    name: str = Field("", description="Name of the address type, ex. 'Email'.")

    scope: str = Field("", description="Scopeof the address type, ex. 'EMAIL'.")

    example: Optional[str] = Field(None, description="Example value for the address.")

    owner: Optional[UUID] = Field(None, description="UUID of the owner")


class AddressVisibility(MOBase):
    name: str = Field(
        "", description="Name for the visibility, ex. 'M\\u00e5 vises eksternt'."
    )

    scope: str = Field("", description="Scopeof the address type, ex. 'EMAIL'.")

    example: Optional[str] = Field(None, description="Example value for the address.")

    owner: Optional[UUID] = Field(None, description="UUID of the owner")


class AddressRelation(UUIDBase):
    type: str = Field(
        description="The type of the address relation, ex 'org_unit' or 'person'."
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


class AddressCreate(Validity):
    """Model representing an address creation."""

    value: str = Field(description="The actual address value.")
    address_type: UUID = Field(description="Type of the address.")
    visibility: UUID = Field(description="Visibility for the address.")
    relation: AddressRelation = Field(
        description="Field representing the relation the address belongs to."
    )

    # OBS: organization UUID is optional based on the logic at:
    # backend/mora/service/address.py:52
    org: Optional[UUID] = Field(
        None, description="Organization the address belongs to."
    )

    async def get_legacy_request(self) -> dict:
        legacy_dict = {
            mapping.TYPE: mapping.ADDRESS,
            mapping.VALUE: self.value,
            mapping.ADDRESS_TYPE: {mapping.UUID: str(self.address_type)},
            mapping.VISIBILITY: {mapping.UUID: str(self.visibility)},
        }

        validity = {}
        if self.from_date:
            validity[mapping.FROM] = self.from_date.date().isoformat()

        if self.to_date:
            validity[mapping.TO] = self.to_date.date().isoformat()

        # Set the relation of the address
        match self.relation.type:
            case mapping.ORG_UNIT:
                legacy_dict[mapping.ORG_UNIT] = {
                    mapping.UUID: str(self.relation.uuid),
                    mapping.VALIDITY: await self._get_org_unit_validity(
                        self.relation.uuid
                    ),
                }
            case mapping.PERSON:
                legacy_dict[mapping.PERSON] = {
                    mapping.UUID: str(self.relation.uuid),
                    mapping.VALIDITY: await self._get_person_validity(
                        self.relation.uuid
                    ),
                }
            case mapping.ENGAGEMENT:
                engagement_dict = {mapping.UUID: str(self.relation.uuid)}
                legacy_dict[mapping.ENGAGEMENT] = engagement_dict

        # Set the organisation
        legacy_dict[mapping.ORG] = {mapping.UUID: str(self.org)}

        return {
            **legacy_dict,
            mapping.VALIDITY: validity,
        }

    @staticmethod
    async def _get_org_unit_validity(org_unit_uuid: UUID) -> Optional[dict]:
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
    async def _get_person_validity(person_uuid: UUID) -> Optional[dict]:
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
    def _get_lora_validity(lora_object: Optional[dict]) -> Optional[dict]:
        if not isinstance(lora_object, dict):
            return None

        from_date: Optional[datetime.datetime] = None
        to_date: Optional[datetime.datetime] = None

        if "fratidspunkt" in lora_object.keys():
            from_date_current_value = lora_object.get("fratidspunkt", {}).get(
                "tidsstempeldatotid"
            )

            if from_date_current_value == "infinity":
                from_date = POSITIVE_INFINITY
            elif from_date_current_value == "-infinity":
                from_date = NEGATIVE_INFINITY
            else:
                from_date = datetime.datetime.fromisoformat(from_date_current_value)

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


class AddressTerminate(Address, ValidityTerminate, Triggerless):
    """Model representing an address-termination."""

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


class Employee(UUIDBase):
    """OS2Mo employee model."""

    pass


class EmployeeCreate(BaseModel):
    """Model representing an employee creation."""

    name: str = Field(description="Full name of the employee.")

    cpr_no: str = Field(description="Danish CPR number of the employee.")
    org: Organisation = Field(
        Organisation(),
        description="The organization the new employee will be created under.",
    )


class EmployeeTerminate(Employee, ValidityTerminate, Triggerless):
    """Model representing an employee termination."""

    pass


class EmployeeUpdate(UUIDBase):
    # name
    name: Optional[str] = Field(
        None, description="New value for the name of the employee"
    )

    # nickname_givenname
    nickname_firstname: Optional[str] = Field(
        None,
        alias="nickname_givenname",
        description="New first-name value of the employee nickname.",
    )

    # nickname_surname
    nickname_lastname: Optional[str] = Field(
        None,
        alias="nickname_surname",
        description="New last-name value of the employee nickname.",
    )

    # seniority
    seniority: Optional[str] = Field(
        None, description="New seniority value of the employee."
    )

    # cpr_no
    cpr_no: Optional[str] = Field(
        None, description="New seniority value of the employee."
    )

    # org
    org: Optional[Organisation] = Field(
        None, description="Organization the employee belongs to."
    )

    # validity
    validity: Optional[Validity] = Field(
        None,
        description="Validity range for the employee, "
        "for when the employee is accessible",
    )

    # user_key


class ITUserTerminate(UUIDBase, ValidityTerminate, Triggerless):
    """Model representing termination of it-user."""

    """(or rather end-date update for access to IT-system)."""

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


class GenericUUIDModel(UUIDBase):
    """Generic UUID model for return types."""

    pass
