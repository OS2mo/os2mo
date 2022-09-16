# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import logging
import typing
from enum import Enum
from typing import Optional
from uuid import UUID

import strawberry
from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator

from mora import common
from mora import exceptions
from mora import mapping
from mora import util
from mora.graphapi.utils import CprNo
from mora.graphapi.utils import SafeString
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY
from ramodels.mo import OpenValidity
from ramodels.mo import Validity as ValidityFromRequired
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


class ValidityTerminate(Validity):
    to_date: datetime.datetime = Field(
        util.NEGATIVE_INFINITY,
        # OBS: Above line should not be necessary, but due to mypy and strawberry not
        # working together properly, this is required in order to prevent mypy from
        # complaining about the strawberry inputs in ".inputs" (and types)
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

    result: typing.Any = Field(description="Result of the trigger", default=None)

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


class EmployeeUpdate(UUIDBase, ValidityFromRequired):
    name: Optional[SafeString] = Field(None, description="something")

    given_name: Optional[SafeString] = Field(
        None,
        description="New first-name value of the employee nickname.",
    )

    sur_name: Optional[SafeString] = Field(
        None,
        description="New last-name value of the employee nickname.",
    )

    nickname: Optional[SafeString] = Field(
        None,
        description="New nickname value of the employee nickname.",
    )

    nickname_given_name: Optional[SafeString] = Field(
        None,
        description="New nickname given-name value of the employee nickname.",
    )

    nickname_sur_name: Optional[SafeString] = Field(
        None,
        description="New nickname sur-name value of the employee nickname.",
    )

    seniority: Optional[SafeString] = Field(
        None, description="New seniority value of the employee."
    )

    cpr_no: Optional[CprNo] = Field(
        None, description="New danish CPR No. of the employee."
    )

    @root_validator
    def validate_name_with_given_name_and_sur_name(cls, values: dict) -> dict:
        """Validate name's and nickname's.

        If "name" is set, "given_name" and "sur_name" are not allowed to be set.
        same goes for nickname.
        """
        if values.get("name") and (values.get("given_name") or values.get("sur_name")):
            raise ValueError(
                "EmployeeUpdate.name is only allowed to be set, if "
                '"given_name" & "sur_name" are None.'
            )

        if values.get("nickname") and (
            values.get("nickname_given_name") or values.get("nickname_sur_name")
        ):
            raise ValueError(
                "EmployeeUpdate.nickname is only allowed to be set, if "
                '"nickname_given_name" & "nickname_sur_name" are None.'
            )

        return values

    def get_legacy_dict(self) -> dict:
        validity_dict = {}
        if self.from_date:
            validity_dict[mapping.FROM] = self.from_date.date().isoformat()

        if self.to_date:
            validity_dict[mapping.FROM] = self.to_date.date().isoformat()

        data_dict = {
            mapping.UUID: str(self.uuid),
            mapping.VALIDITY: validity_dict,
        }

        if self.name:
            data_dict[mapping.NAME] = self.name
        if self.given_name:
            data_dict[mapping.GIVENNAME] = self.given_name
        if self.sur_name:
            data_dict[mapping.SURNAME] = self.sur_name

        if self.nickname:
            data_dict[mapping.NICKNAME] = self.nickname
        if self.nickname_given_name:
            data_dict[mapping.NICKNAME_GIVENNAME] = self.nickname_given_name
        if self.nickname_sur_name:
            data_dict[mapping.NICKNAME_SURNAME] = self.nickname_sur_name

        if self.seniority:
            data_dict[mapping.SENIORITY] = self.seniority

        if self.cpr_no:
            data_dict[mapping.CPR_NO] = self.cpr_no

        return {
            mapping.TYPE: mapping.EMPLOYEE,
            mapping.UUID: str(self.uuid),
            mapping.DATA: data_dict,
        }


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
