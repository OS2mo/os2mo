# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pydantic models backing the GraphQL filters.

The Strawberry inputs in `filters` are generated from these. Descriptions live
here, because that is where Strawberry reads them from.
"""

from __future__ import annotations

from datetime import datetime
from textwrap import dedent
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from pydantic import Extra
from pydantic import Field
from pydantic import root_validator
from strawberry import UNSET

from mora.util import CPR


def gen_filter_string(title: str, key: str) -> str:
    return dedent(
        f"""\
        {title} filter limiting which entries are returned.
        """
    ) + gen_filter_table(key)


def gen_filter_table(key: str) -> str:
    return dedent(
        f"""\

        | `{key}`      | Elements returned                            |
        |--------------|----------------------------------------------|
        | not provided | All                                          |
        | `null`       | All                                          |
        | `[]`         | None                                         |
        | `"x"`        | `["x"]` or `[]` (`*`)                        |
        | `["x", "y"]` | `["x", "y"]`, `["x"]`, `["y"]` or `[]` (`*`) |

        `*`: Elements returned depends on which elements were found.
        """
    )


def unset(description: str | None = None) -> Any:
    """A field distinguishing unset from null. Defaults are not validated."""
    return Field(default_factory=lambda: UNSET, description=description)


class FilterModel(BaseModel):
    class Config:
        # A mistyped field would otherwise be dropped, leaving a filter that
        # matches everything, and an access rule that grants everything
        extra = Extra.forbid

    @root_validator(pre=True)
    def drop_unset(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Fall back to the default, as `to_pydantic()` passes every field."""
        return {key: value for key, value in values.items() if value is not UNSET}


class BaseFilter(FilterModel):
    uuids: list[UUID] | None = Field(
        None, description=gen_filter_string("UUID", "uuids")
    )
    user_keys: list[str] | None = Field(
        None, description=gen_filter_string("User-key", "user_keys")
    )

    from_date: datetime | None = unset(
        description="Limit the elements returned by their starting validity.",
    )
    to_date: datetime | None = unset(
        description="Limit the elements returned by their ending validity.",
    )
    registration_time: datetime | None = Field(
        None,
        description="Show elements as they were at the provided registration time",
    )


class EmployeeFiltered(FilterModel):
    employee: EmployeeFilter | None = unset(
        description=dedent(
            """\
            Employee filter limiting which entries are returned.
            """
        ),
    )
    employees: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Employee UUID", "employees"),
    )


class OrganisationUnitFiltered(FilterModel):
    org_unit: OrganisationUnitFilter | None = Field(
        None,
        description=dedent(
            """\
            Organisation Unit filter limiting which entries are returned.
            """
        ),
    )
    org_units: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )


class AddressFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: AddressRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    address_type: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Address type filter limiting which entries are returned.
            """
        ),
    )
    address_types: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Address type UUID", "address_types"),
    )
    address_type_user_keys: list[str] | None = Field(
        None,
        description=gen_filter_string(
            "Address type user-key", "address_type_user_keys"
        ),
    )

    engagement: EngagementFilter | None = Field(
        None,
        description=dedent(
            """\
            Engagement filter limiting which entries are returned.
            """
        ),
    )
    engagements: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Engagement UUID", "engagements"),
    )

    ituser: ITUserFilter | None = Field(
        None,
        description="ITUser filter limiting which entries are returned.",
    )

    visibility: ClassFilter | None = Field(
        None,
        description="Visibility filter limiting which entries are returned.",
    )


class AssociationFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: AssociationRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    association_type: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Address type filter limiting which entries are returned.
            """
        ),
    )
    association_types: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Association type UUID", "association_types"),
    )
    association_type_user_keys: list[str] | None = Field(
        None,
        description=gen_filter_string(
            "Association type user-key", "association_type_user_keys"
        ),
    )
    it_association: bool | None = Field(
        None,
        description=dedent(
            """\
            Query for either IT-Associations or "normal" Associations. `None` returns all.

            This field is needed to replicate the functionality in the service API:
            `?it=1`
            """
        ),
    )


class ClassFilter(BaseFilter):
    registration: ClassRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    name: list[str] | None = Field(
        None,
        description=dedent(
            """\
            Name filter finding exact matches by name.
            """
        ),
    )

    facet: FacetFilter | None = Field(
        None,
        description=dedent(
            """\
            Facet filter limiting which entries are returned.
            """
        ),
    )
    facets: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Facet UUID", "facets"),
    )
    facet_user_keys: list[str] | None = Field(
        None,
        description=gen_filter_string("Facet user-key", "facet_user_keys"),
    )

    parent: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Parent filter limiting which entries are returned.
            """
        ),
    )
    parents: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Parent UUID", "parents"),
    )
    parent_user_keys: list[str] | None = Field(
        None,
        description=gen_filter_string("Parent user-key", "parent_user_keys"),
    )

    it_system: ITSystemFilter | None = Field(
        None,
        description=dedent(
            """\
            IT-System filter limiting which entries are returned.
            """
        ),
    )

    owner: ClassOwnerFilter | None = Field(
        None,
        description=dedent(
            """\
            Owner filter limiting which entries are returned.
            """
        ),
    )

    scope: list[str] | None = Field(
        None,
        description=gen_filter_string("Scope", "scope"),
    )


class EmployeeFilter(BaseFilter):
    registration: EmployeeRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    query: str | None = unset(
        description=dedent(
            """\
            Free text search.

            Does best effort lookup to find entities matching the query string.
            No quarantees are given w.r.t. the entries returned.
            """
        ),
    )
    cpr_numbers: list[CPR] | None = Field(
        None, description=gen_filter_string("CPR number", "cpr_numbers")
    )

    owner: OwnerFilter | None = Field(
        None,
        description="Owner filter limiting which entries are returned.",
    )

    ituser: ITUserFilter | None = unset(
        description=dedent(
            """\
            IT-user filter limiting which entries are returned.

            Set to `null` to only return employees without any IT-users.
            """
        ),
    )


class EngagementFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: EngagementRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    job_function: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Job function filter limiting which entries are returned.
            """
        ),
    )

    engagement_type: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Engagement type filter limiting which entries are returned.
            """
        ),
    )

    ituser: ITUserFilter | None = Field(
        None,
        description="ITUser filter limiting which entries are returned.",
    )

    primary: ClassFilter | None = unset(
        description=dedent(
            """\
            Primary class filter limiting which entries are returned.

            Set to `null` to only return engagements without a primary class.
            """
        ),
    )


class FacetFilter(BaseFilter):
    registration: FacetRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    parent: FacetFilter | None = Field(
        None,
        description=dedent(
            """\
            Parent filter limiting which entries are returned.
            """
        ),
    )
    parents: list[UUID] | None = Field(
        None,
        description=gen_filter_string("Parent UUID", "parents"),
    )
    parent_user_keys: list[str] | None = Field(
        None,
        description=gen_filter_string("Parent user-key", "parent_user_keys"),
    )


class ITSystemFilter(BaseFilter):
    registration: ITSystemRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )


class ITUserFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: ITUserRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    itsystem: ITSystemFilter | None = Field(
        None,
        description=dedent(
            """\
            ITSystem filter limiting which entries are returned.
            """
        ),
    )
    itsystem_uuids: list[UUID] | None = Field(
        None,
        description=gen_filter_string(
            "Only return IT users of ITSystem with these UUIDs", "itsystem_uuids"
        ),
    )

    engagement: EngagementFilter | None = Field(
        None,
        description=dedent(
            """\
            Engagement filter limiting which entries are returned.
            """
        ),
    )

    rolebinding: RoleBindingFilter | None = unset(
        description=dedent(
            """\
            Rolebinding filter limiting which entries are returned.

            Set to `null` to only return IT users without any rolebindings.
            """
        ),
    )

    external_ids: list[str] | None = unset(
        description=dedent(
            """\
            Only return IT users with this `external_id`.

            | `external_id` | Elements returned                            |
            |---------------|----------------------------------------------|
            | not provided  | All                                          |
            | `null`        | Only entries where `external_id` is not set  |
            | `[]`          | None                                         |
            | `"x"`         | `["x"]` or `[]` (`*`)                        |
            | `["x", "y"]`  | `["x", "y"]`, `["x"]`, `["y"]` or `[]` (`*`) |

            `*`: Elements returned depends on which elements were found.
            """
        ),
    )

    binding_types: list[str] | None = Field(
        None,
        description=gen_filter_string(
            "Only return IT users with this `binding_type`", "binding_type"
        ),
    )

    primary: ClassFilter | None = unset(
        description=dedent(
            """\
            Primary class filter limiting which entries are returned.

            Set to `null` to only return IT users without a primary class.
            """
        ),
    )


class KLEFilter(BaseFilter, OrganisationUnitFiltered):
    registration: KLERegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )


class LeaveFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LeaveRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )


class ManagerFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: ManagerRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )
    engagement: EngagementFilter | None = Field(
        None,
        description=dedent(
            """\
            Engagement filter limiting which entries are returned.
            """
        ),
    )

    responsibility: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Responsibility filter limiting which entries are returned.
            """
        ),
    )
    manager_type: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Manager_type filter limiting which entries are returned.
            """
        ),
    )
    exclude: EmployeeFilter | None = Field(
        None,
        description=dedent(
            """\
            Employee filter for managers to exclude from the result.
            """
        ),
    )


class OrganisationUnitFilter(BaseFilter):
    registration: OrganisationUnitRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    query: str | None = unset(
        description=dedent(
            """\
            Free text search.

            Does best effort lookup to find entities matching the query string.
            No quarantees are given w.r.t. the entries returned.
            """
        ),
    )
    names: list[str] | None = unset(
        description=dedent(
            """\
            Name filter finding exact matches by name.
            """
        )
        + gen_filter_table("names"),
    )

    parent: OrganisationUnitFilter | None = unset(
        description=dedent(
            """\
            Select organisation units whose parent matches the given filter.

            Set to `None` to find root units.
            Set to `{}` to find non-root units.

            This endpoint behaves to ancestor as child does to descendant.
            """
        ),
    )
    parents: list[UUID] | None = unset(
        description=gen_filter_string("Parent UUID", "parents"),
    )

    child: OrganisationUnitFilter | None = unset(
        description=dedent(
            """\
            Select organisation units whose children matches the given filter.

            Set to `None` to find leaf node units.
            Set to `{}` to find inner node units.

            This endpoint behaves to descendant as parent does to ancestor.
            """
        ),
    )

    hierarchy: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Hierarchy filter limiting which entries are returned.

            Filter organisation units by their organisational hierarchy labels.

            Can be used to extract a subset of the organisational structure.

            Examples of user-keys:
            * `"Line-management"`
            * `"Self-owned institution"`
            * `"Outside organisation"`
            * `"Hidden"`

            Note:
            The organisation-gatekeeper integration is one option to keep hierarchy labels up-to-date.
            """
        ),
    )
    hierarchies: list[UUID] | None = Field(
        None,
        description=dedent(
            """\
        Filter organisation units by their organisational hierarchy labels.

        Can be used to extract a subset of the organisational structure.

        Examples of user-keys:
        * `"Line-management"`
        * `"Self-owned institution"`
        * `"Outside organisation"`
        * `"Hidden"`

        Note:
        The organisation-gatekeeper integration is one option to keep hierarchy labels up-to-date.
        """
        )
        + gen_filter_table("hierarchies"),
    )

    subtree: OrganisationUnitFilter | None = unset()

    descendant: OrganisationUnitFilter | None = unset(
        description=dedent(
            """\
            Select organisation units which have a descendant matching the given filter.

            Note that every node is its own descendant as per [CLRS] 12.2-6.

            Given the following tree:
            ```
            A
            ├── B
            │   ├── C
            │   │   └── D
            │   └── E
            └── F
            ```
            the `descendant` filter behaves according to the following table:

            | Filter | Returned    |
            |--------|-------------|
            |      A | A           |
            |      B | A B         |
            |      C | A B C       |
            |      D | A B C D     |
            |      E | A B E       |
            |      F | A F         |
            """,
        ),
    )

    ancestor: OrganisationUnitFilter | None = unset(
        description=dedent(
            """\
            Select organisation units which have an ancestor matching the given filter.

            Note that every node is its own ancestor as per [CLRS] 12.2-6.

            Given the following tree:
            ```
            A
            ├── B
            │   ├── C
            │   │   └── D
            │   └── E
            └── F
            ```
            the `ancestor` filter behaves according to the following table:

            | Filter | Returned    |
            |--------|-------------|
            |      A | A B C D E F |
            |      B | B C D E     |
            |      C | C D         |
            |      D | D           |
            |      E | E           |
            |      F | F           |
            """
        ),
    )

    engagement: EngagementFilter | None = Field(
        None,
        description=dedent(
            """\
            Filter organisation units to only include matches pointed to by engagements.

            Can be used to find organisation units for certain engagements.
            """
        ),
    )

    owner: OwnerFilter | None = Field(
        None,
        description="Owner filter limiting which entries are returned.",
    )


class OwnerFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    owner: EmployeeFilter | None = Field(
        None,
        description=dedent(
            """\
            Owner filter limiting which entries are returned.
            """
        ),
    )


class RegistrationFilter(FilterModel):
    uuids: list[UUID] | None = Field(
        None, description=gen_filter_string("UUID", "uuids")
    )
    actors: list[UUID] | None = Field(
        None,
        description=dedent(
            """\
            Filter registrations by their changing actor.

            Can be used to select all changes made by a particular user or integration.
            """
        )
        + gen_filter_table("actors"),
    )
    # TODO: Turn this into an enum
    models: list[str] | None = Field(
        None,
        description=dedent(
            """\
            Filter registrations by their model type.

            Can be used to select all changes of a type.
            """
        )
        + gen_filter_table("models"),
    )
    start: datetime | None = Field(
        None,
        description="Limit the elements returned by their starting validity.",
    )
    end: datetime | None = Field(
        None,
        description="Limit the elements returned by their ending validity.",
    )


def model_default(model: str) -> Any:
    """Pin a registration filter to its collection. Not exposed in GraphQL."""
    return Field(default_factory=lambda: [model])


class AddressRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("address")


class AssociationRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("association")


class ClassRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("class")


class EmployeeRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("employee")


class EngagementRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("engagement")


class FacetRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("facet")


class ITSystemRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("itsystem")


class ITUserRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("ituser")


class KLERegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("kle")


class LeaveRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("leave")


class ManagerRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("manager")


class OrganisationUnitRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("org_unit")


class RoleRegistrationFilter(RegistrationFilter):
    uuids: list[UUID] | None = None
    models: list[str] | None = model_default("role")


class RelatedUnitFilter(BaseFilter, OrganisationUnitFiltered):
    # TODO: registration filter
    pass


class RoleBindingFilter(BaseFilter, OrganisationUnitFiltered):
    registration: RoleRegistrationFilter | None = Field(
        None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )
    ituser: ITUserFilter | None = Field(
        None,
        description=dedent(
            """\
            ITUser filter limiting which entries are returned.
            """
        ),
    )
    role: ClassFilter | None = Field(
        None,
        description=dedent(
            """\
            Role filter limiting which entries are returned.
            """
        ),
    )


class ClassOwnerFilter(OrganisationUnitFilter):
    include_none: bool = Field(
        False,
        description=dedent(
            """\
            Include classes with `owner=None`.
            """
        ),
    )


def _update_forward_refs() -> None:
    """Resolve the annotations, which are cyclic, now that all models exist."""
    for value in list(globals().values()):
        if isinstance(value, type) and issubclass(value, FilterModel):
            value.update_forward_refs()


_update_forward_refs()
