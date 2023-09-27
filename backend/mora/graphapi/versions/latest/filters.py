# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from textwrap import dedent
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


@strawberry.input(description="Address filter.")
class AddressFilter(BaseFilter):
    address_types: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Address type UUID", "address_types"),
    )
    address_type_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Address type user-key", "address_type_user_keys"
        ),
    )
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    engagements: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Engagement UUID", "engagements")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )


@strawberry.input(description="Association filter.")
class AssociationFilter(BaseFilter):
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )
    association_types: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Association type UUID", "association_types"),
    )
    association_type_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Association type user-key", "association_type_user_keys"
        ),
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
    facets: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Facet UUID", "facets")
    )

    facet_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Facet user-key", "facet_user_keys"),
    )

    parents: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Parent UUID", "parents")
    )
    parent_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Parent user-key", "parent_user_keys"),
    )


@strawberry.input(description="Configuration filter.")
class ConfigurationFilter:
    identifiers: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Key", "identifiers"),
    )


@strawberry.input(description="Employee filter.")
class EmployeeFilter(BaseFilter):
    cpr_numbers: list[CPR] | None = strawberry.field(
        default=None, description=gen_filter_string("CPR number", "cpr_numbers")
    )


@strawberry.input(description="Engagement filter.")
class EngagementFilter(BaseFilter):
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )


@strawberry.input(description="Facet filter.")
class FacetFilter(BaseFilter):
    parents: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Parent UUID", "parents")
    )
    parent_user_keys: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Parent user-key", "parent_user_keys"),
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
    pass


@strawberry.input(description="IT user filter.")
class ITUserFilter(BaseFilter):
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )
    itsystem_uuids: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Only return IT users of ITSystem with these UUIDs", "itsystem_uuids"
        ),
    )


@strawberry.input(description="KLE filter.")
class KLEFilter(BaseFilter):
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )


@strawberry.input(description="Leave filter.")
class LeaveFilter(BaseFilter):
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )


@strawberry.input(description="Manager filter.")
class ManagerFilter(BaseFilter):
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )


@strawberry.input(description="Organisation unit filter.")
class OrganisationUnitFilter(BaseFilter):
    parents: list[UUID] | None = strawberry.field(
        default=UNSET, description=gen_filter_string("Parent UUID", "parents")
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
    )


@strawberry.input(description="Owner filter.")
class OwnerFilter(BaseFilter):
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
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


@strawberry.input(description="Related unit filter.")
class RelatedUnitFilter(BaseFilter):
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )


@strawberry.input(description="Role filter.")
class RoleFilter(BaseFilter):
    employees: list[UUID] | None = strawberry.field(
        default=None, description=gen_filter_string("Employee UUID", "employees")
    )
    org_units: list[UUID] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Organisational Unit UUID", "org_units"),
    )
