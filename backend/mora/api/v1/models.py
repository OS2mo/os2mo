# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from typing import List, Optional, Any, Dict

from ramodels.mo._shared import Validity, MOBase


class Facet(MOBase):
    user_key: str
    description: str


class SmallClass(MOBase):
    name: str
    user_key: str
    example: Optional[str]
    scope: Optional[str]
    owner: Optional[str]


class Class(SmallClass):
    full_name: str
    top_level_facet: Facet
    facet: Facet


class OrganizationUnit(MOBase):
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
    seniority: str


class Manager(MOBase):
    user_key: str
    validity: Validity
    responsibility: List[Class]
    org_unit: OrganizationUnit
    person: Person
    manager_type: Class
    manager_level: Class


class Role(MOBase):
    user_key: str
    validity: Validity
    person: Person
    org_unit: OrganizationUnit
    role_type: Class


class Itsystem(MOBase):
    name: str
    reference: Optional[str]
    system_type: Optional[str]
    user_key: str
    validity: Validity


class ItsystemBinding(MOBase):
    user_key: str
    validity: Validity
    itsystem: Itsystem
    person: Person
    org_unit: Optional[OrganizationUnit]


class Association(MOBase):
    user_key: str
    validity: Validity
    person: Person
    org_unit: OrganizationUnit
    association_type: Class
    primary: Optional[Class]
    dynamic_classes: Optional[List[Class]]
    substitute: Any


class Engagement(MOBase):
    user_key: str
    validity: Validity
    integration_data: Dict[str, str]
    person: Person
    org_unit: OrganizationUnit
    job_function: Class
    engagement_type: Class
    primary: Class
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


class Address(MOBase):
    user_key: str
    validity: Validity
    address_type: Class
    href: Optional[str]
    name: str
    value: str
    value2: Optional[str]
    visibility: Optional[SmallClass]
    person: Optional[Person]
    org_unit: Optional[OrganizationUnit]


class Organization(MOBase):
    name: str
    user_key: str


class OrganizationUnitFull(OrganizationUnit):
    location: str
    user_settings: Dict[str, Any]
    parent: Optional["OrganizationUnitFull"]
    org: Organization
    org_unit_type: Class
    time_planning: Class
    org_unit_level: Class


OrganizationUnitFull.update_forward_refs()


class Employee(Person):
    cpr_no: Optional[str]
    org: Organization
    user_key: str
    validity: Validity


class Leave(MOBase):
    user_key: str
    validity: Validity
    person: Person
    leave_type: SmallClass
    engagement: Engagement


class KLE(MOBase):
    user_key: str
    validity: Validity
    kle_aspect: List[Class]
    kle_number: Class
    org_unit: Optional[OrganizationUnit]


class Owner(MOBase):
    user_key: str
    validity: Validity
    owner_inference_priority: Optional[Any]
    owner: Person
    org_unit: OrganizationUnit
    person: Optional[Person]


class RelatedUnit(MOBase):
    user_key: str
    validity: Validity
    org_unit: List[OrganizationUnit]


class EngagementAssociation(MOBase):
    user_key: str
    validity: Validity
    engagement: Engagement
    org_unit: OrganizationUnit
    engagement_association_type: Class
