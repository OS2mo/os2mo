# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import Dict
from typing import get_args
from typing import get_origin
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from pydantic import BaseModel
from pydantic import create_model
from pydantic.fields import Field
from pydantic.fields import ModelField
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import MORef
from ramodels.mo._shared import Validity


class Facet(MOBase):
    user_key: str
    description: str


class SmallKlasse(MOBase):
    name: str
    user_key: str
    example: Optional[str]
    scope: Optional[str]
    owner: Optional[str]


class Klasse(SmallKlasse):
    full_name: str
    top_level_facet: Facet
    facet: Facet


class OrganisationUnit(MOBase):
    name: str
    user_key: str
    validity: Validity


class Person(MOBase):
    givenname: str
    surname: str
    name: str
    nickname_givenname: str
    nickname_surname: str
    nickname: str
    seniority: Optional[str]


class Manager(MOBase):
    user_key: str
    validity: Validity
    responsibility: List[Klasse]
    org_unit: OrganisationUnit
    person: Person
    manager_type: Klasse
    manager_level: Klasse


class Role(MOBase):
    user_key: str
    validity: Validity
    person: Person
    org_unit: OrganisationUnit
    role_type: Klasse


class ITSystem(MOBase):
    name: str
    reference: Optional[str]
    system_type: Optional[str]
    user_key: str
    validity: Validity


class ITSystemBinding(MOBase):
    user_key: str
    validity: Validity
    itsystem: ITSystem
    person: Optional[Person]
    org_unit: Optional[OrganisationUnit]


class Association(MOBase):
    user_key: str
    validity: Validity
    person: Person
    org_unit: OrganisationUnit
    association_type: Klasse
    primary: Optional[Klasse]
    dynamic_classes: Optional[List[Klasse]]
    substitute: Optional[Dict[str, str]]


class Engagement(MOBase):
    user_key: str
    validity: Validity
    person: Person
    org_unit: OrganisationUnit
    job_function: Klasse
    engagement_type: Klasse
    primary: Optional[Klasse]
    is_primary: Optional[bool]
    fraction: Optional[float]
    extension_1: Optional[str]
    extension_2: Optional[str]
    extension_3: Optional[str]
    extension_4: Optional[str]
    extension_5: Optional[str]
    extension_6: Optional[str]
    extension_7: Optional[str]
    extension_8: Optional[str]
    extension_9: Optional[str]
    extension_10: Optional[str]
    integration_data: Optional[Dict[str, str]]


class Address(MOBase):
    user_key: str
    validity: Validity
    address_type: Klasse
    href: Optional[str]
    name: str
    value: str
    value2: Optional[str]
    visibility: Optional[SmallKlasse]
    person: Optional[Person]
    org_unit: Optional[OrganisationUnit]
    engagement: Optional[Engagement]


class Organisation(MOBase):
    name: str
    user_key: str


class OrganisationUnitFull(OrganisationUnit):
    location: str
    user_settings: Dict[str, Union[str, bool, Dict[str, Optional[Union[str, bool]]]]]
    parent: Optional["OrganisationUnitFull"]
    org: Organisation
    org_unit_type: Klasse
    time_planning: Optional[Klasse]
    org_unit_level: Optional[Klasse]


OrganisationUnitFull.update_forward_refs()


class Employee(Person):
    cpr_no: Optional[str]
    org: Organisation
    user_key: str
    validity: Validity


class Leave(MOBase):
    user_key: str
    validity: Validity
    person: Person
    leave_type: SmallKlasse
    engagement: Engagement


class KLE(MOBase):
    user_key: str
    validity: Validity
    kle_aspect: List[Klasse]
    kle_number: Klasse
    org_unit: Optional[OrganisationUnit]


class Owner(MOBase):
    user_key: str
    validity: Validity
    owner_inference_priority: Optional[str]
    owner: Person
    org_unit: Optional[OrganisationUnit]
    person: Optional[Person]


class RelatedUnit(MOBase):
    user_key: str
    validity: Validity
    org_unit: Tuple[OrganisationUnit, OrganisationUnit]


class EngagementAssociation(MOBase):
    user_key: str
    validity: Validity
    engagement: Engagement
    org_unit: OrganisationUnit
    engagement_association_type: Optional[Klasse]


def optional(model_type: Type) -> Tuple[Optional[Type], None]:
    return (Optional[model_type], None)


def required(model_type: Type) -> Tuple[Type, ...]:
    return (model_type, ...)


def mark_required(
    model_type: Type, is_required: bool
) -> Union[Tuple[Optional[Type], None], Tuple[Type, ...]]:
    if is_required:
        return required(model_type)
    return optional(model_type)


def is_model_reference(field: Field):
    if not isinstance(field, ModelField):
        return False
    if not issubclass(field.type_, BaseModel):
        return False
    return True


def is_validity(name: str) -> bool:
    return name == "validity"


def to_only_uuid_model(model: BaseModel) -> BaseModel:
    """Convert a normal model into an "only_primary_uuid" model."""

    def decide_subtype(field):
        subtypes = get_args(field.type_)
        origin = get_origin(field.type_)
        # TODO: Should probably handle Sets, Dict, and such eventually
        if origin is tuple:
            # TODO: Should probably inspect element types
            return Tuple[tuple(MORef for _ in subtypes)]
        raise ValueError("Unknown combined type")

    def decide_type(name, field):
        subtypes = get_args(field.type_)
        if subtypes:
            return decide_subtype(field)
        if is_model_reference(field) and not is_validity(name):
            return MORef
        return field.type_

    fields = {}
    for name, field in model.__fields__.items():
        fields[name] = mark_required(decide_type(name, field), field.required)

    return create_model(model.__name__ + "OnlyPrimaryUUID", **fields)
