# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations

from datetime import datetime
from textwrap import dedent
from typing import Any
from uuid import UUID

import strawberry
from strawberry import UNSET

from mora.graphapi.versions.latest.models import FileStore
from mora.util import CPR


def gen_filter_string(title: str, key: str) -> str:
    return (
        dedent(
            f"""\
        {title} filter limiting which entries are returned.
        """
        )
        + gen_filter_table(key)
    )


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


@strawberry.input
class BaseFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    user_keys: list[str] | None = strawberry.field(
        default=None, description=gen_filter_string("User-key", "user_keys")
    )

    from_date: datetime | None = strawberry.field(
        default=UNSET,
        description="Limit the elements returned by their starting validity.",
    )
    to_date: datetime | None = strawberry.field(
        default=UNSET,
        description="Limit the elements returned by their ending validity.",
    )


@strawberry.interface
class EmployeeFiltered:
    employee: EmployeeFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Employee filter limiting which entries are returned.
            """
        ),
    )
    employees: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Employee UUID", "employees"),
        deprecation_reason="Replaced by the 'employee' filter",
    )


@strawberry.interface
class OrganisationUnitFiltered:
    org_unit: OrganisationUnitFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Organisation Unit filter limiting which entries are returned.
            """
        ),
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
        deprecation_reason="Replaced by the 'org_unit' filter",
    )


@strawberry.input(description="Address filter.")
class AddressFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: AddressRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    address_type: ClassFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Address type filter limiting which entries are returned.
            """
        ),
    )
    address_types: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Address type UUID", "address_types"),
        deprecation_reason="Replaced by the 'address_type' filter",
    )
    address_type_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Address type user-key", "address_type_user_keys"
        ),
        deprecation_reason="Replaced by the 'address_type' filter",
    )

    engagement: EngagementFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Engagement filter limiting which entries are returned.
            """
        ),
    )
    engagements: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Engagement UUID", "engagements"),
        deprecation_reason="Replaced by the 'engagement' filter",
    )

    ituser: ITUserFilter | None = strawberry.field(
        default=None,
        description="ITUser filter limiting which entries are returned.",
    )


@strawberry.input(description="Association filter.")
class AssociationFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: AssociationRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    association_type: ClassFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Address type filter limiting which entries are returned.
            """
        ),
    )
    association_types: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Association type UUID", "association_types"),
        deprecation_reason="Replaced by the 'association_type' filter",
    )
    association_type_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Association type user-key", "association_type_user_keys"
        ),
        deprecation_reason="Replaced by the 'association_type' filter",
    )
    it_association: bool | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Query for either IT-Associations or "normal" Associations. `None` returns all.

            This field is needed to replicate the functionality in the service API:
            `?it=1`
            """
        ),
    )


@strawberry.input(description="Class filter.")
class ClassFilter(BaseFilter):
    registration: ClassRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    facet: FacetFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Facet filter limiting which entries are returned.
            """
        ),
    )
    facets: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Facet UUID", "facets"),
        deprecation_reason="Replaced by the 'facet' filter",
    )
    facet_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Facet user-key", "facet_user_keys"),
        deprecation_reason="Replaced by the 'facet' filter",
    )

    parent: ClassFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Parent filter limiting which entries are returned.
            """
        ),
    )
    parents: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Parent UUID", "parents"),
        deprecation_reason="Replaced by the 'parent' filter",
    )
    parent_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Parent user-key", "parent_user_keys"),
        deprecation_reason="Replaced by the 'parent' filter",
    )

    it_system: ITSystemFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            IT-System filter limiting which entries are returned.
            """
        ),
    )

    scope: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Scope", "scope"),
    )


@strawberry.input(description="Configuration filter.")
class ConfigurationFilter:
    identifiers: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Key", "identifiers"),
    )


@strawberry.input(description="Employee filter.")
class EmployeeFilter(BaseFilter):
    registration: EmployeeRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    query: str | None = strawberry.field(
        default=UNSET,
        description=dedent(
            """\
            Free text search.

            Does best effort lookup to find entities matching the query string.
            No quarantees are given w.r.t. the entries returned.
            """
        ),
    )
    cpr_numbers: list[CPR] | None = strawberry.field(
        default=None, description=gen_filter_string("CPR number", "cpr_numbers")
    )


@strawberry.input(description="Engagement filter.")
class EngagementFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: EngagementRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    job_function: ClassFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Job function filter limiting which entries are returned.
            """
        ),
    )


@strawberry.input(description="Facet filter.")
class FacetFilter(BaseFilter):
    registration: FacetRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    parent: FacetFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Parent filter limiting which entries are returned.
            """
        ),
    )
    parents: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Parent UUID", "parents"),
        deprecation_reason="Replaced by the 'parent' filter",
    )
    parent_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Parent user-key", "parent_user_keys"),
        deprecation_reason="Replaced by the 'parent' filter",
    )


@strawberry.input(description="File filter.")
class FileFilter:
    file_store: FileStore = strawberry.field(
        description="File Store enum deciding which file-store to fetch files from.",
    )
    file_names: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Filename", "file_names"),
    )


@strawberry.input(description="Health filter.")
class HealthFilter:
    identifiers: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Healthcheck identifiers", "identifiers"),
    )


@strawberry.input(description="IT system filter.")
class ITSystemFilter(BaseFilter):
    registration: ITSystemRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )


@strawberry.input(description="IT user filter.")
class ITUserFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: ITUserRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    itsystem: ITSystemFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            ITSystem filter limiting which entries are returned.
            """
        ),
    )
    itsystem_uuids: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Only return IT users of ITSystem with these UUIDs", "itsystem_uuids"
        ),
        deprecation_reason="Replaced by the 'itsystem' filter",
    )

    engagement: EngagementFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Engagement filter limiting which entries are returned.
            """
        ),
    )

    external_ids: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Only return IT users with this `external_id`", "external_id"
        ),
    )


@strawberry.input(description="KLE filter.")
class KLEFilter(BaseFilter, OrganisationUnitFiltered):
    registration: KLERegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )


@strawberry.input(description="Leave filter.")
class LeaveFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LeaveRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )


@strawberry.input(description="Manager filter.")
class ManagerFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: ManagerRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    responsibility: ClassFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Responsibility filter limiting which entries are returned.
            """
        ),
    )


@strawberry.input(description="Organisation unit filter.")
class OrganisationUnitFilter(BaseFilter):
    registration: OrganisationUnitRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )

    query: str | None = strawberry.field(
        default=UNSET,
        description=dedent(
            """\
            Free text search.

            Does best effort lookup to find entities matching the query string.
            No quarantees are given w.r.t. the entries returned.
            """
        ),
    )
    names: list[str] | None = strawberry.field(
        default=UNSET,
        description=dedent(
            """\
            Name filter finding exact matches by name.
            """
        )
        + gen_filter_table("names"),
    )

    parent: OrganisationUnitFilter | None = strawberry.field(
        default=UNSET,
        description=dedent(
            """\
            Select organisation units whose parent matches the given filter.

            Set to `None` to find root units.
            """
        ),
    )
    parents: list[UUID] | None = strawberry.field(
        default=UNSET,
        description=gen_filter_string("Parent UUID", "parents"),
        deprecation_reason="Replaced by the 'parent' filter",
    )

    hierarchy: ClassFilter | None = strawberry.field(
        default=None,
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
    hierarchies: list[UUID] | None = strawberry.field(
        default=None,
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
        deprecation_reason="Replaced by the 'hierarchy' filter",
    )

    subtree: OrganisationUnitFilter | None = strawberry.field(
        default=UNSET,
        deprecation_reason="Renamed to 'descendant'",
    )

    descendant: OrganisationUnitFilter | None = strawberry.field(
        default=UNSET,
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

    ancestor: OrganisationUnitFilter | None = strawberry.field(
        default=UNSET,
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

    engagement: EngagementFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Filter organisation units to only include matches pointed to by engagements.

            Can be used to find organisation units for certain engagements.
            """
        ),
    )


@strawberry.input(description="Owner filter.")
class OwnerFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    owner: EmployeeFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Owner filter limiting which entries are returned.
            """
        ),
    )


@strawberry.input(description="Registration filter.")
class RegistrationFilter:
    uuids: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("UUID", "uuids")
    )
    actors: list[UUID] | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Filter registrations by their changing actor.

            Can be used to select all changes made by a particular user or integration.
            """
        )
        + gen_filter_table("actors"),
    )
    # TODO: Turn this into an enum
    models: list[str] | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Filter registrations by their model type.

            Can be used to select all changes of a type.
            """
        )
        + gen_filter_table("models"),
    )
    start: datetime | None = strawberry.field(
        default=None,
        description="Limit the elements returned by their starting validity.",
    )
    end: datetime | None = strawberry.field(
        default=None,
        description="Limit the elements returned by their ending validity.",
    )
    registration_start: datetime | None = strawberry.field(
        default=None,
        description="Limit the elements returned by their registration date.",
    )
    registration_end: datetime | None = strawberry.field(
        default=None,
        description="Limit the elements returned by their registration date.",
    )


def mutable_default(value: Any) -> Any:
    return strawberry.field(default_factory=lambda: value)


@strawberry.input(description="Address registration filter.")
class AddressRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["address"])


@strawberry.input(description="Association registration filter.")
class AssociationRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["association"])


@strawberry.input(description="Class registration filter.")
class ClassRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["class"])


@strawberry.input(description="Employee registration filter.")
class EmployeeRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["employee"])


@strawberry.input(description="Engagement registration filter.")
class EngagementRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["engagement"])


@strawberry.input(description="Facet registration filter.")
class FacetRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["facet"])


@strawberry.input(description="ITSystem registration filter.")
class ITSystemRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["itsystem"])


@strawberry.input(description="ITUser registration filter.")
class ITUserRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["ituser"])


@strawberry.input(description="KLE registration filter.")
class KLERegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["kle"])


@strawberry.input(description="Leave registration filter.")
class LeaveRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["leave"])


@strawberry.input(description="Manager registration filter.")
class ManagerRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["manager"])


@strawberry.input(description="OrganisationUnit registration filter.")
class OrganisationUnitRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["org_unit"])


@strawberry.input(description="Role registration filter.")
class RoleRegistrationFilter(RegistrationFilter):
    uuids: strawberry.Private[list[UUID] | None] = None
    models: strawberry.Private[list[str] | None] = mutable_default(["role"])


@strawberry.input(description="Related unit filter.")
class RelatedUnitFilter(BaseFilter, OrganisationUnitFiltered):
    # TODO: registration filter
    pass


@strawberry.input(description="Rolebinding filter.")
class RoleBindingFilter(BaseFilter, OrganisationUnitFiltered):
    registration: RoleRegistrationFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            Registration filter limiting which entries are returned.
            """
        ),
    )
    ituser: ITUserFilter | None = strawberry.field(
        default=None,
        description=dedent(
            """\
            ITUser filter limiting which entries are returned.
            """
        ),
    )
