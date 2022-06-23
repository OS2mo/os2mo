#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import Optional
from uuid import UUID

from pydantic.config import Extra
from pydantic.main import BaseModel
from ramodels.mo._shared import Validity


class OrgUnitBase(BaseModel):
    uuid: UUID
    user_key: str

    class Config:
        extra = Extra.forbid


class Facet(OrgUnitBase):
    description: Optional[str]


class OrgUnitLevel(OrgUnitBase):
    name: Optional[str]
    user_key: Optional[str]
    scope: Optional[str]
    example: Optional[UUID]
    owner: Optional[UUID]
    facet: Optional[Facet]
    top_level_facet: Optional[Facet]
    full_name: Optional[str]


class Org(OrgUnitBase):
    name: str


class OrgUnitHierarchy(OrgUnitBase):
    ...


class OrgUnitType(OrgUnitBase):
    name: Optional[str]
    user_key: Optional[str]
    scope: Optional[str]
    example: Optional[UUID]
    owner: Optional[UUID]
    facet: Optional[Facet]
    top_level_facet: Optional[Facet]
    full_name: Optional[str]


class OrgUnitSettings(BaseModel):
    show_roles: bool
    show_kle: bool
    show_user_key: bool
    show_location: bool
    show_time_planning: bool
    show_level: bool
    show_primary_engagement: bool
    show_primary_association: bool
    show_org_unit_button: bool
    inherit_manager: bool
    association_dynamic_facets: Optional[str]
    substitute_roles: Optional[str]
    show_cpr_no: bool
    show_user_key_in_search: bool
    extension_field_ui_labels: Optional[str]
    show_engagement_hyperlink: bool
    show_seniority: bool
    show_owner: bool
    show_custom_logo: Optional[str]
    autocomplete_use_new_api: bool
    autocomplete_attrs_employee: Optional[UUID]
    autocomplete_attrs_orgunit: Optional[UUID]

    class Config:
        extra = Extra.forbid


class UserSettings(BaseModel):
    orgunit: OrgUnitSettings


class Parent(OrgUnitBase):
    user_key: Optional[str]
    name: Optional[str]
    validity: Optional[Validity]
    location: Optional[str]
    parent: Optional[UUID]
    org: Optional[Org]
    org_unit_level: Optional[OrgUnitLevel]
    org_unit_type: Optional[OrgUnitType]
    time_planning: Optional[UUID]
    user_settings: Optional[UserSettings]


class AddressType(OrgUnitBase):
    user_key: Optional[str]
    name: Optional[str]
    scope: Optional[str]
    example: Optional[str]


class Address(BaseModel):
    address_type: AddressType
    uuid: Optional[UUID]
    value: Optional[str]


class Detail(BaseModel):
    type: str
    address_type: AddressType
    org: Optional[Org]
    validity: Validity
    value: str


class MOOrgUnitWrite(BaseModel):
    type: Optional[str]
    uuid: Optional[UUID]
    validity: Validity
    user_key: Optional[str]
    name: str
    parent: Optional[Parent]
    org_unit_level: Optional[OrgUnitLevel]
    org_unit_type: OrgUnitType
    details: Optional[list[Detail]]  # TODO/FIXME ???
    integration_data: Optional[dict[str, int]]
    org_unit_hierarchy: Optional[dict[str, UUID]]
    time_planning: Optional[dict[str, UUID]]
    addresses: Optional[list[Address]]

    class Config:
        extra = Extra.forbid

        schema_extra = {
            "example": {
                "name": "Name",
                "parent": {"uuid": "329e42ce-0357-446a-8767-140cb249f789"},
                "org_unit_type": {"uuid": "3ef81e52-0deb-487d-9d0e-a69bbe0277d8"},
                "validity": {"from": "2016-01-01", "to": None},
            }
        }
