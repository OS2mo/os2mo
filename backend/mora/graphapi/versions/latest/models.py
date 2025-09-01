# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime
import logging
from enum import Enum
from textwrap import dedent
from typing import Any
from typing import Literal
from uuid import UUID

import strawberry
from oio_rest import validate
from pydantic import Extra
from pydantic import Field
from pydantic import root_validator

from mora import common
from mora import exceptions
from mora import mapping
from mora.graphapi.gmodels.mo import ClassRead as RAClassRead
from mora.graphapi.gmodels.mo import FacetRead as RAFacetRead
from mora.graphapi.gmodels.mo import MOBase
from mora.graphapi.gmodels.mo import MORef
from mora.graphapi.gmodels.mo import OpenValidity as RAOpenValidity
from mora.graphapi.gmodels.mo import Validity as RAValidity
from mora.graphapi.gmodels.mo._shared import ITUserRef
from mora.graphapi.gmodels.mo._shared import OrgUnitRef
from mora.graphapi.gmodels.mo._shared import UUIDBase
from mora.graphapi.gmodels.mo.details import AddressRead as RAAddressRead
from mora.util import CPR
from mora.util import NEGATIVE_INFINITY
from mora.util import ONE_DAY
from mora.util import POSITIVE_INFINITY
from mora.util import to_lora_time

logger = logging.getLogger(__name__)


# Various
# -------
def gen_uuid(uuid: UUID | None) -> dict[str, str] | None:
    if uuid is None:
        return None
    return {"uuid": str(uuid)}


class Validity(RAOpenValidity):
    """Model representing an entities validity range.

    Where both from and to dates can be optional.
    """

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def get_termination_effect(self) -> dict:
        if not self.from_date:
            # TODO: This if is legacy, and should be removed since the logic is confusing.
            #       Instead of replacing "from" with "to", it should fail and clients should
            #       use the logic correctly instead.
            if self.to_date:
                logger.warning(
                    'Validity called without "from" in "validity"',
                )
                return common._create_virkning(
                    self.get_terminate_effect_to_date(), "infinity"
                )
            # coverage: pause
            exceptions.ErrorCodes.V_MISSING_REQUIRED_VALUE(
                key="Validity must have a 'from' date",
                validity={
                    "from": self.from_date.isoformat() if self.from_date else None,
                    "to": self.to_date.isoformat() if self.to_date else None,
                },
            )
            # coverage: unpause
        # coverage: pause
        if self.from_date and self.to_date:
            return common._create_virkning(
                self.get_terminate_effect_from_date(),
                self.get_terminate_effect_to_date(),
            )

        return common._create_virkning(
            self.get_terminate_effect_from_date(), "infinity"
        )
        # coverage: unpause

    def get_terminate_effect_from_date(self) -> datetime.datetime:
        if not self.from_date or not isinstance(
            self.from_date, datetime.datetime
        ):  # pragma: no cover
            exceptions.ErrorCodes.V_MISSING_START_DATE()

        if self.from_date.time() != datetime.time.min:  # pragma: no cover
            exceptions.ErrorCodes.E_INVALID_INPUT(
                f"{self.from_date.isoformat()!r} is not at midnight!",
            )

        return self.from_date

    def get_terminate_effect_to_date(self) -> datetime.datetime:
        if not self.to_date:  # pragma: no cover
            return POSITIVE_INFINITY

        if self.to_date.time() != datetime.time.min:  # pragma: no cover
            exceptions.ErrorCodes.E_INVALID_INPUT(
                f"{self.to_date.isoformat()!r} is not at midnight!",
            )

        return self.to_date + ONE_DAY


class ValidityTerminate(Validity):
    to_date: datetime.datetime = Field(
        alias="to",
        description="When the validity should end - required when terminating",
    )

    def to_handler_dict(self) -> dict:
        validity = {}
        if self.from_date:
            validity["from"] = self.from_date
        if self.to_date:
            validity["to"] = self.to_date

        return {
            "uuid": self.uuid,  # type: ignore
            "validity": validity,
        }


# Root Organisation
# -----------------
class Organisation(UUIDBase):
    """Model representing an Organization."""

    pass


# Addresses
# ---------
class AddressRead(RAAddressRead):
    it_user_uuid: UUID | None = Field(description="Optional UUID of connected IT user")


class AddressUpsert(UUIDBase):
    """Model representing an address creation/update commonalities."""

    # OBS: Only one of the two UUIDs are allowed to be set for the old logic to work
    org_unit: UUID | None = Field(description="UUID for the related org unit.")
    person: UUID | None = Field(description="UUID for the related person.")
    # TODO: Remove employee in a future version of GraphQL
    employee: UUID | None = Field(description="UUID for the related person.")

    engagement: UUID | None = Field(description="UUID for the related engagement.")
    ituser: UUID | None = Field(description="UUID for the related ituser.")

    visibility: UUID | None = Field(description="Visibility for the address.")
    validity: RAValidity = Field(description="Validity range for the org-unit.")
    user_key: str | None = Field(
        description="User key of the address. If None, defaults to value"
    )

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
            "it": gen_uuid(self.ituser),
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

        if number_of_uuids != 1:  # pragma: no cover
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
        return {k: v for k, v in data_dict.items() if v is not None}


class AddressTerminate(ValidityTerminate):
    """Model representing an address-termination."""

    uuid: UUID = Field(description="UUID for the address we want to terminate.")


# Associations
# ------------
class AssociationUpsert(UUIDBase):
    user_key: str | None = Field(description="Extra info or uuid.")
    primary: UUID | None = Field(description="Primary field of the association")
    validity: RAValidity = Field(description="Validity range for the org-unit.")

    person: UUID | None = Field(description="Employee uuid.")
    # TODO: Remove employee in a future version of GraphQL
    employee: UUID | None = Field(description="Employee uuid.")
    substitute: UUID | None = Field(description="Substitute uuid.")
    trade_union: UUID | None = Field(description="Trade union uuid.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "user_key": self.user_key,
            "primary": gen_uuid(self.primary),
            "person": gen_uuid(self.person) or gen_uuid(self.employee),
            "substitute": gen_uuid(self.substitute),
            # TODO: This should probably just return `gen_uuid(self.trade_union)`, when we've gotten rid of the service-api.
            "trade_union": [gen_uuid(self.trade_union)] if self.trade_union else [],
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
        # Substitute doesn't use `gen_uuid` since `None` will result in the
        # "update substitute" not running in `service/association`, which means
        # that substitute can't be changed to vacant
        data_dict["substitute"] = {"uuid": self.substitute}
        return {k: v for k, v in data_dict.items() if v is not None}


class AssociationTerminate(ValidityTerminate):
    """Model representing an association termination(or rather end-date update)."""

    uuid: UUID = Field(description="UUID for the association we want to terminate.")


# Classes
# -------
class ClassCreate(UUIDBase):
    """Model representing a Class creation."""

    name: str = Field(description="Mo-class name.")
    user_key: str = Field(description="Extra info or uuid")
    facet_uuid: UUID = Field(description="UUID of the related facet.")
    scope: str | None = Field(description="Scope of the class.")
    published: str = Field(
        "Publiceret", description="Published state of the class object."
    )
    parent_uuid: UUID | None = Field(description="UUID of the parent class.")
    example: str | None = Field(description="Example usage.")
    owner: UUID | None = Field(description="Owner of class")
    validity: Validity = Field(description="Validity range for the class.")
    it_system_uuid: UUID | None = Field(description="UUID of the associated IT-system.")
    description: str | None = Field(description="Description of class.")

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid

    def to_registration(self, organisation_uuid: UUID) -> dict:
        from_time = to_lora_time(
            self.validity.from_date or to_lora_time(NEGATIVE_INFINITY)
        )
        to_time = to_lora_time(self.validity.to_date or to_lora_time(POSITIVE_INFINITY))

        klasseegenskaber = {
            "brugervendtnoegle": self.user_key,
            "titel": self.name,
            "virkning": {"from": from_time, "to": to_time},
        }
        if self.example is not None:  # pragma: no cover
            klasseegenskaber["eksempel"] = self.example
        if self.scope is not None:
            klasseegenskaber["omfang"] = self.scope
        if self.description is not None:
            klasseegenskaber["beskrivelse"] = self.description

        relations = {
            "facet": [
                {
                    "uuid": str(self.facet_uuid),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "Facet",
                }
            ],
            "ansvarlig": [
                {
                    "uuid": str(organisation_uuid),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "Organisation",
                }
            ],
        }
        if self.parent_uuid is not None:
            relations["overordnetklasse"] = [
                {
                    "uuid": str(self.parent_uuid),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "klasse",
                }
            ]
        else:
            relations["overordnetklasse"] = [
                {
                    "uuid": "",
                    "urn": "",
                    "virkning": {"from": from_time, "to": to_time},
                }
            ]
        if self.owner is not None:
            relations["ejer"] = [
                {
                    "uuid": str(self.owner),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "organisationenhed",
                }
            ]

        if self.it_system_uuid is not None:
            relations["mapninger"] = [
                {
                    "uuid": str(self.it_system_uuid),
                    "virkning": {"from": from_time, "to": to_time},
                    "objekttype": "itsystem",
                }
            ]

        lora_registration = {
            "tilstande": {
                "klassepubliceret": [
                    {
                        "publiceret": self.published,
                        "virkning": {"from": from_time, "to": to_time},
                    }
                ]
            },
            "attributter": {"klasseegenskaber": [klasseegenskaber]},
            "relationer": relations,
        }
        validate.validate(lora_registration, "klasse")

        return lora_registration


class ClassUpdate(ClassCreate):
    """Model representing a class update."""

    uuid: UUID = Field(description="UUID of the class to update.")


class ClassTerminate(ValidityTerminate):
    uuid: UUID = Field(description="UUID for the class we want to terminate.")

    def to_registration(self) -> dict:
        return {
            "tilstande": {
                "klassepubliceret": [
                    {
                        "publiceret": "IkkePubliceret",
                        "virkning": self.get_termination_effect(),
                    }
                ]
            },
            "note": "Afslut klasse",
        }


class ClassRead(RAClassRead):
    validity: Validity = Field(description="Validity of the class.")
    it_system_uuid: UUID | None = Field(description="UUID of the associated IT-system.")


# Employees
# ---------
class EmployeeUpsert(UUIDBase):
    user_key: str | None = Field(
        description="Short, unique key for the employee (defaults to object UUID on creation)."
    )

    nickname_given_name: str | None = Field(
        None,
        description="Nickname givenname (firstname) of the employee.",
    )
    nickname_surname: str | None = Field(
        None,
        description="Nickname surname (lastname) of the employee.",
    )

    seniority: datetime.date | None = Field(
        # OBS: backend/mora/service/employee.py:96 for why type is datetime.date
        None,
        description="New seniority value of the employee.",
    )

    cpr_number: CPR | None = Field(
        None, description="Danish CPR number of the employee."
    )

    def to_handler_dict(self) -> dict:
        data_dict = {
            mapping.UUID: self.uuid,
            mapping.USER_KEY: self.user_key,
            mapping.NICKNAME_GIVENNAME: self.nickname_given_name,
            mapping.NICKNAME_SURNAME: self.nickname_surname,
            mapping.SENIORITY: self.seniority.isoformat() if self.seniority else None,
            mapping.CPR_NO: self.cpr_number,
        }
        return data_dict


class EmployeeCreate(EmployeeUpsert):
    """Model representing an employee creation."""

    given_name: str = Field(description="Givenname (firstname) of the employee.")
    surname: str = Field(description="Surname (lastname) of the employee.")

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict[mapping.GIVENNAME] = self.given_name
        data_dict[mapping.SURNAME] = self.surname
        return data_dict


class EmployeeUpdate(EmployeeUpsert):
    uuid: UUID = Field(description="UUID of the employee to be updated.")

    given_name: str | None = Field(
        None,
        description="New first-name value of the employee nickname.",
    )
    surname: str | None = Field(
        None,
        description="New last-name value of the employee nickname.",
    )
    validity: RAValidity = Field(description="Validity range for the change.")

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict[mapping.GIVENNAME] = self.given_name
        data_dict[mapping.SURNAME] = self.surname
        data_dict[mapping.VALIDITY] = {
            "from": self.validity.from_date.date().isoformat(),
            "to": self.validity.to_date.date().isoformat()
            if self.validity.to_date
            else None,
        }
        return {k: v for k, v in data_dict.items() if v is not None}


class EmployeeTerminate(ValidityTerminate):
    """Model representing an employee termination."""

    uuid: UUID = Field(description="UUID for the employee we want to terminate.")
    vacate: bool = Field(
        False,
        description="Mark related manager functions as vacated",
        deprecation_reason="Deal with relations seperately. Will be removed in a future version of OS2mo.",
    )


# Engagements
# -----------
class EngagementTerminate(ValidityTerminate):
    """Model representing an engagement termination(or rather end-date update)."""

    uuid: UUID = Field(description="UUID for the engagement we want to terminate.")


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
    fraction: int | None = Field(
        description="Worktime between 0-1000000 for the engagement object.",
        le=1000000,
        ge=0,
        default=None,
    )

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
            "fraction": self.fraction,
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
        if person_uuid and employee_uuid:  # pragma: no cover
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Can only set one of 'person' and 'employee'"
            )
        if person_uuid is None and employee_uuid is None:  # pragma: no cover
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
        return {k: v for k, v in data_dict.items() if v is not None}


# EngagementsAssociations
# -----------------------


# Facets
# -----------------------
class FacetCreate(UUIDBase):
    """Model representing a facet creation."""

    user_key: str = Field(description="Facet name.")
    published: str = Field(
        "Publiceret", description="Published state of the facet object."
    )

    validity: Validity = Field(
        description="Validity range for the facet. Default to ['-infinity', 'infinity']",
    )

    class Config:
        frozen = True
        extra = Extra.forbid

    def to_registration(self, organisation_uuid: UUID) -> dict:
        from_time = to_lora_time(
            self.validity.from_date or to_lora_time(NEGATIVE_INFINITY)
        )
        to_time = to_lora_time(self.validity.to_date or to_lora_time(POSITIVE_INFINITY))

        lora_registration = {
            "tilstande": {
                "facetpubliceret": [
                    {
                        "publiceret": self.published,
                        "virkning": {"from": from_time, "to": to_time},
                    }
                ]
            },
            "attributter": {
                "facetegenskaber": [
                    {
                        "brugervendtnoegle": self.user_key,
                        "virkning": {"from": from_time, "to": to_time},
                    }
                ]
            },
            "relationer": {
                "ansvarlig": [
                    {
                        "uuid": str(organisation_uuid),
                        "virkning": {"from": from_time, "to": to_time},
                        "objekttype": "Organisation",
                    }
                ],
            },
        }
        validate.validate(lora_registration, "facet")

        return lora_registration


class FacetUpdate(FacetCreate):
    """Model representing a facet updates."""

    uuid: UUID = Field(description="UUID of the facet to update.")


class FacetTerminate(ValidityTerminate):
    uuid: UUID = Field(description="UUID for the facet we want to terminate.")

    def to_registration(self) -> dict:
        return {
            "tilstande": {
                "facetpubliceret": [
                    {
                        "publiceret": "IkkePubliceret",
                        "virkning": self.get_termination_effect(),
                    }
                ]
            },
            "note": "Afslut klasse",
        }


class FacetRead(RAFacetRead):
    validity: Validity = Field(description="Validity of the facet.")


# ITAssociations
# ---------
class ITAssociationUpsert(UUIDBase):
    user_key: str | None = Field(description="Extra info or uuid.")
    primary: UUID | None = Field(description="Primary field of the association")
    validity: RAValidity = Field(description="Validity range for the org-unit.")

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
        }


class ITAssociationCreate(ITAssociationUpsert):
    """Model representing an IT-association creation."""

    org_unit: UUID = Field(description="org-unit uuid.")
    person: UUID = Field(description="UUID of the employee")
    it_user: UUID = Field(description="IT-user UUID")
    job_function: UUID = Field(description="Job function UUID")

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["org_unit"] = gen_uuid(self.org_unit)
        data_dict["person"] = gen_uuid(self.person)
        data_dict["it"] = gen_uuid(self.it_user)
        data_dict["job_function"] = gen_uuid(self.job_function)
        return data_dict


class ITAssociationUpdate(ITAssociationUpsert):
    """Model representing an IT-association update."""

    uuid: UUID = Field(description="UUID of the ITAssociation you want to update.")
    org_unit: UUID | None = Field(description="org-unit uuid.")
    it_user: UUID | None = Field(description="IT-user UUID")
    job_function: UUID | None = Field(description="Job function UUID")

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["org_unit"] = gen_uuid(self.org_unit)
        data_dict["it"] = gen_uuid(self.it_user)
        data_dict["job_function"] = gen_uuid(self.job_function)
        return {k: v for k, v in data_dict.items() if v is not None}


class ITAssociationTerminate(ValidityTerminate):
    """Model representing an IT-association termination."""

    uuid: UUID = Field(description="UUID for the ITAssociation we want to terminate.")


# ITSystems
# ---------
class ITSystemCreate(UUIDBase):
    """Model representing an itsystem creation."""

    user_key: str
    name: str
    validity: RAOpenValidity = Field(description="Validity range for the itsystem")

    class Config:
        frozen = True
        allow_population_by_field_name = True
        extra = Extra.forbid

    def to_registration(self, organisation_uuid: UUID) -> dict:
        from_time = to_lora_time(self.validity.from_date or "-infinity")
        to_time = to_lora_time(self.validity.to_date or "infinity")

        lora_registration = {
            "attributter": {
                "itsystemegenskaber": [
                    {
                        "brugervendtnoegle": self.user_key,
                        "virkning": {
                            "from": from_time,
                            "to": to_time,
                        },
                        "itsystemnavn": self.name,
                    }
                ]
            },
            "tilstande": {
                "itsystemgyldighed": [
                    {
                        "gyldighed": "Aktiv",
                        "virkning": {
                            "from": from_time,
                            "to": to_time,
                        },
                    }
                ]
            },
            "relationer": {
                "tilknyttedeorganisationer": [
                    {
                        "uuid": str(organisation_uuid),
                        "virkning": {
                            "from": from_time,
                            "to": to_time,
                        },
                    }
                ],
            },
        }
        validate.validate(lora_registration, "itsystem")
        return lora_registration


class ITSystemUpdate(ITSystemCreate):
    uuid: UUID = Field(description="UUID for the it-system we want to edit.")


class ITSystemTerminate(ValidityTerminate):
    uuid: UUID = Field(description="UUID for the it-system we want to terminate.")

    def to_registration(self) -> dict:
        return {
            "tilstande": {
                "itsystemgyldighed": [
                    {
                        "gyldighed": "Inaktiv",
                        "virkning": self.get_termination_effect(),
                    }
                ]
            },
            "note": "Afslut enhed",
        }


# ITUsers
# -------
class ITUserUpsert(UUIDBase):
    external_id: str | None = Field(
        description="ID of the user account in the external system."
    )
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
            "external_id": self.external_id,
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
    note: str | None = Field(
        description="Note associated with the creation of this IT user."
    )

    @root_validator
    def validation(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Verifies that at only one of org_unit and employee field has been set."""
        if (values.get("person") and values.get("org_unit")) or (
            not values.get("person") and not values.get("org_unit")
        ):  # pragma: no cover
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Exactly 1 of the fields {mapping.ORG_UNIT} or {mapping.PERSON} must be set"
            )
        return values

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["type"] = "it"
        data_dict["user_key"] = self.user_key
        data_dict["itsystem"] = gen_uuid(self.itsystem)
        data_dict["note"] = self.note
        return data_dict


class ITUserUpdate(ITUserUpsert):
    """Model representing a IT-user creation."""

    uuid: UUID = Field(description="UUID of the IT-user you want to update.")

    user_key: str | None = Field(description="The IT user account name.")
    itsystem: UUID | None = Field(
        description="Reference to the IT system for the IT user."
    )
    note: str | None = Field(
        description="Note associated with the update of this IT user."
    )

    def to_handler_dict(self) -> dict:
        data_dict = super().to_handler_dict()
        data_dict["user_key"] = self.user_key
        data_dict["itsystem"] = gen_uuid(self.itsystem)
        data_dict["note"] = self.note
        return {k: v for k, v in data_dict.items() if v is not None}


class ITUserTerminate(ValidityTerminate):
    """Model representing termination of it-user."""

    """(or rather end-date update for access to IT-system)."""

    uuid: UUID = Field(description="UUID for the it-user we want to terminate.")


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
        aspects = list(map(gen_uuid, self.kle_aspects))
        return {
            "uuid": self.uuid,
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

    uuid: UUID = Field(description="UUID of the KLE annotation to be updated.")

    user_key: str | None = Field(description="Extra info or uuid.")

    kle_number: UUID | None = Field(description="UUID of the KLE number.")

    kle_aspects: list[UUID] | None = Field(description="UUID of the kle_aspects.")

    org_unit: UUID | None = Field(
        description="UUID of the KLE's organisation unit to be updated."
    )

    validity: RAValidity = Field(
        description="Validity range for the KLE to be updated."
    )

    def to_handler_dict(self) -> dict:
        data_dict: dict = {
            "user_key": self.user_key,
            "kle_number": gen_uuid(self.kle_number),
            "org_unit": gen_uuid(self.org_unit),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }
        if self.kle_aspects:
            data_dict["kle_aspect"] = list(map(gen_uuid, self.kle_aspects))

        return {k: v for k, v in data_dict.items() if v is not None}


class KLETerminate(ValidityTerminate):
    """Model representing a KLE termination."""

    uuid: UUID = Field(description="UUID of the KLE annotation we want to terminate.")


# Leaves
# --------
class LeaveCreate(UUIDBase):
    """Model for creating a leave."""

    user_key: str | None = Field(description="Extra info or uuid.")
    person: UUID = Field(description="UUID of the person.")
    # Engagement seems to be optional, but it's not possible to create a Leave without it.
    # Therefore it's set to required
    engagement: UUID = Field(description="UUID of the related engagement.")
    leave_type: UUID = Field(description="UUID of the leave type")
    validity: RAValidity = Field(description="Validity range for the leave.")

    def to_handler_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "user_key": self.user_key,
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


class LeaveUpdate(UUIDBase):
    """Model for updating a leave."""

    uuid: UUID = Field(description="UUID of the leave.")
    user_key: str | None = Field(description="Extra info or uuid.")
    person: UUID | None = Field(description="UUID of the person.")
    engagement: UUID | None = Field(description="UUID of the related engagement.")
    leave_type: UUID | None = Field(description="UUID of the leave type")
    validity: RAValidity = Field(description="Validity range for the leave.")

    def to_handler_dict(self) -> dict:
        data_dict: dict = {
            "uuid": self.uuid,
            "user_key": self.user_key,
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
        return {k: v for k, v in data_dict.items() if v is not None}


class LeaveTerminate(ValidityTerminate):
    """Model representing a leave termination."""

    uuid: UUID = Field(description="UUID of the leave we want to terminate.")


# Managers
# --------
class ManagerCreate(UUIDBase):
    """Model for creating an employee of manager type."""

    user_key: str | None = Field(description="Extra info or uuid.")
    person: UUID | None = Field(description="UUID of the manager as person.")
    responsibility: list[UUID] = Field(
        description="UUID of the managers responsibilities."
    )
    engagement: UUID | None = Field(description="UUID of the related engagement.")
    org_unit: UUID = Field(description="UUID of the managers organisation unit.")
    manager_level: UUID = Field(description="UUID of the managers level.")
    manager_type: UUID = Field(description="UUID of the managers type..")
    validity: RAValidity = Field(description="Validity range for the manager.")

    def to_handler_dict(self) -> dict:
        responsibilities = list(map(gen_uuid, self.responsibility))
        return {
            "uuid": self.uuid,
            "user_key": self.user_key,
            "type": "manager",
            "person": gen_uuid(self.person),
            "engagement": gen_uuid(self.engagement) if self.engagement else None,
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
    engagement: UUID | None = Field(description="UUID of the related engagement.")

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
            "engagement": gen_uuid(self.engagement) if self.engagement else None,
            "org_unit": gen_uuid(self.org_unit),
            "manager_type": gen_uuid(self.manager_type),
            "manager_level": gen_uuid(self.manager_level),
        }
        if self.responsibility:
            data_dict["responsibility"] = list(map(gen_uuid, self.responsibility))

        return {k: v for k, v in data_dict.items() if (v is not None) or k == "person"}


class ManagerTerminate(ValidityTerminate):
    """Model representing a manager termination."""

    uuid: UUID = Field(description="UUID of the manager we want to terminate.")


# Organisational Units
# --------------------
class OrganisationUnitTerminate(ValidityTerminate):
    """Model representing an organisation unit termination."""

    uuid: UUID = Field(description="UUID for the org-unit we want to terminate.")


# Owners
# -----


@strawberry.enum(
    description=dedent(
        """\
    Enum for the supported inference priorities.
    """
    )
)
class OwnerInferencePriority(Enum):
    ENGAGEMENT = strawberry.enum_value(
        "engagement_priority",
        description=dedent(
            """\
        The engagement priority.
        """
        ),
    )
    ASSOCIATION = strawberry.enum_value(
        "association_priority",
        description=dedent(
            """\
        The association priority.
        """
        ),
    )


class OwnerCreate(UUIDBase):
    """Model for creating owner."""

    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID | None = Field(description="UUID of the org unit")
    person: UUID | None = Field(description="UUID of the person")
    owner: UUID | None = Field(description="UUID of the owner")
    inference_priority: OwnerInferencePriority | None = Field(
        description="Inference priority, if set: `engagement_priority` or `association_priority`"
    )
    validity: RAValidity = Field(description="Validity range for the owner.")

    def to_handler_dict(self) -> dict:
        return {
            "user_key": self.user_key,
            "org_unit": gen_uuid(self.org_unit),
            "person": gen_uuid(self.person),
            "owner": gen_uuid(self.owner),
            "owner_inference_priority": self.inference_priority,
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


class OwnerUpdate(UUIDBase):
    """Model for updating an owner."""

    uuid: UUID = Field(description="UUID of the owner to be updated.")
    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID | None = Field(description="UUID of the org unit")
    person: UUID | None = Field(description="UUID of the person")
    owner: UUID | None = Field(description="UUID of the owner")
    inference_priority: OwnerInferencePriority | None = Field(
        description="Inference priority, if set: `engagement_priority` or `association_priority`"
    )
    validity: RAValidity = Field(description="Validity range for the owner.")

    def to_handler_dict(self) -> dict:
        data_dict = {
            "user_key": self.user_key,
            "org_unit": gen_uuid(self.org_unit),
            "person": gen_uuid(self.person),
            "owner": gen_uuid(self.owner),
            "owner_inference_priority": self.inference_priority,
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }
        # Same garbage as with `manager.person` and `org_unit.parent`
        return {k: v for k, v in data_dict.items() if (v is not None) or k == "owner"}


class OwnerTerminate(ValidityTerminate):
    """Model representing an owner termination."""

    uuid: UUID = Field(description="UUID of the owner we want to terminate.")


# Related units
# -----


class RelatedUnitsUpdate(UUIDBase):
    origin: UUID = Field(description="UUID of the unit to create relations under.")
    destination: list[UUID] | None = Field(
        description="UUID of the units to create relations to."
    )
    validity: RAValidity = Field(description="From date.")

    def to_handler_dict(self) -> dict:
        return {
            "origin": self.origin,
            "destination": self.destination or [],
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
            },
        }


# Rolebindings
# ------------

# These first few models are essentially "ramodels" rip-offs, but there is no
# need for rolebindings in ramodels as they are not exposed in the service API.


class RoleType(MORef):
    """Role type reference."""


class RoleBindingBase(MOBase):
    """A MO role object."""

    type_: str = Field("rolebinding", alias="type", description="The object type.")
    validity: RAValidity = Field(description="Validity of the role object.")


class RoleBindingRead(RoleBindingBase):
    """A MO role read object."""

    org_unit_uuid: UUID | None = Field(
        description="UUID of the organisation unit related to the association."
    )
    role: UUID = Field(description="UUID of the role type klasse.")
    it_user_uuid: UUID = Field(description="UUID of the IT user.")


class RoleBindingWrite(RoleBindingBase):
    """A MO role write object."""

    org_unit: OrgUnitRef | None = Field(
        description="Reference to the organisation unit for the role."
    )
    role: RoleType = Field(description="Reference to the role klasse.")
    it_user_uuid: ITUserRef = Field(description="Reference to the IT user.")


class RoleBinding(MOBase):
    type_: Literal["rolebinding"] = Field(
        "rolebinding", alias="type", description="The object type."
    )
    role: RoleType = Field(description="Reference to the role type facet")
    org_unit: OrgUnitRef | None = Field(
        description=(
            "Reference to the organisation unit for which the role should be created."
        )
    )
    it_user: ITUserRef = Field(description="Reference to the IT user.")
    validity: RAValidity = Field(
        description="Validity of the created rolebinding object."
    )


class RoleBindingCreate(UUIDBase):
    """Model for creating role."""

    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID | None = Field(description="UUID of the org_unit")
    ituser: UUID = Field(description="UUID of the ituser")
    role: UUID = Field(description="UUID of the role type")
    validity: RAValidity = Field(description="Validity range for the role.")

    def to_handler_dict(self) -> dict:
        return {
            "user_key": self.user_key,
            "org_unit": gen_uuid(self.org_unit),
            "it": gen_uuid(self.ituser),
            "role": gen_uuid(self.role),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }


class RoleBindingUpdate(UUIDBase):
    """Model for updating a role annotation."""

    uuid: UUID = Field(description="UUID of the role to be updated.")
    user_key: str | None = Field(description="Extra info or uuid.")
    org_unit: UUID | None = Field(
        description="UUID of the role's organisation unit to be updated."
    )
    ituser: UUID = Field(description="UUID of the ituser")
    role: UUID | None = Field(description="UUID of the role type")
    validity: RAValidity = Field(
        description="Validity range for the role to be updated."
    )

    def to_handler_dict(self) -> dict:
        data_dict: dict = {
            "uuid": self.uuid,
            "user_key": self.user_key,
            "role": gen_uuid(self.role),
            "org_unit": gen_uuid(self.org_unit),
            "it": gen_uuid(self.ituser),
            "validity": {
                "from": self.validity.from_date.date().isoformat(),
                "to": self.validity.to_date.date().isoformat()
                if self.validity.to_date
                else None,
            },
        }
        return {k: v for k, v in data_dict.items() if v is not None}


class RoleBindingTerminate(ValidityTerminate):
    """Model representing a role termination."""

    uuid: UUID = Field(description="UUID of the role we want to terminate.")


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
