# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry input types for the filters in `filter_models`."""

# Strawberry gives each filter a `from_pydantic` taking its own model, which
# mypy reads as an invalid override wherever one filter inherits another
# mypy: disable-error-code="override"

from textwrap import dedent
from typing import Annotated

import strawberry

from mora.graphapi.models import FileStore

from . import filter_models
from .filter_docs import gen_filter_string

LazyAddressRegistrationFilter = Annotated[
    "AddressRegistrationFilter", strawberry.lazy(__name__)
]
LazyAssociationRegistrationFilter = Annotated[
    "AssociationRegistrationFilter", strawberry.lazy(__name__)
]
LazyClassFilter = Annotated["ClassFilter", strawberry.lazy(__name__)]
LazyClassOwnerFilter = Annotated["ClassOwnerFilter", strawberry.lazy(__name__)]
LazyClassRegistrationFilter = Annotated[
    "ClassRegistrationFilter", strawberry.lazy(__name__)
]
LazyEmployeeFilter = Annotated["EmployeeFilter", strawberry.lazy(__name__)]
LazyEmployeeRegistrationFilter = Annotated[
    "EmployeeRegistrationFilter", strawberry.lazy(__name__)
]
LazyEngagementFilter = Annotated["EngagementFilter", strawberry.lazy(__name__)]
LazyEngagementRegistrationFilter = Annotated[
    "EngagementRegistrationFilter", strawberry.lazy(__name__)
]
LazyFacetFilter = Annotated["FacetFilter", strawberry.lazy(__name__)]
LazyFacetRegistrationFilter = Annotated[
    "FacetRegistrationFilter", strawberry.lazy(__name__)
]
LazyITSystemFilter = Annotated["ITSystemFilter", strawberry.lazy(__name__)]
LazyITSystemRegistrationFilter = Annotated[
    "ITSystemRegistrationFilter", strawberry.lazy(__name__)
]
LazyITUserFilter = Annotated["ITUserFilter", strawberry.lazy(__name__)]
LazyITUserRegistrationFilter = Annotated[
    "ITUserRegistrationFilter", strawberry.lazy(__name__)
]
LazyKLERegistrationFilter = Annotated[
    "KLERegistrationFilter", strawberry.lazy(__name__)
]
LazyLeaveRegistrationFilter = Annotated[
    "LeaveRegistrationFilter", strawberry.lazy(__name__)
]
LazyManagerRegistrationFilter = Annotated[
    "ManagerRegistrationFilter", strawberry.lazy(__name__)
]
LazyOrganisationUnitFilter = Annotated[
    "OrganisationUnitFilter", strawberry.lazy(__name__)
]
LazyOrganisationUnitRegistrationFilter = Annotated[
    "OrganisationUnitRegistrationFilter", strawberry.lazy(__name__)
]
LazyOwnerFilter = Annotated["OwnerFilter", strawberry.lazy(__name__)]
LazyRoleBindingFilter = Annotated["RoleBindingFilter", strawberry.lazy(__name__)]
LazyRoleRegistrationFilter = Annotated[
    "RoleRegistrationFilter", strawberry.lazy(__name__)
]


@strawberry.experimental.pydantic.input(model=filter_models.BaseFilter)
class BaseFilter:
    uuids: strawberry.auto
    user_keys: strawberry.auto
    from_date: strawberry.auto
    to_date: strawberry.auto
    registration_time: strawberry.auto


@strawberry.experimental.pydantic.input(model=filter_models.EmployeeFiltered)
class EmployeeFiltered:
    employee: LazyEmployeeFilter | None
    employees: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'employee' filter",
    )


@strawberry.experimental.pydantic.input(model=filter_models.OrganisationUnitFiltered)
class OrganisationUnitFiltered:
    org_unit: LazyOrganisationUnitFilter | None
    org_units: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'org_unit' filter",
    )


@strawberry.experimental.pydantic.input(
    model=filter_models.AddressFilter, description="Address filter."
)
class AddressFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LazyAddressRegistrationFilter | None
    address_type: LazyClassFilter | None
    address_types: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'address_type' filter",
    )
    address_type_user_keys: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'address_type' filter",
    )
    engagement: LazyEngagementFilter | None
    engagements: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'engagement' filter",
    )
    ituser: LazyITUserFilter | None
    visibility: LazyClassFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.AssociationFilter, description="Association filter."
)
class AssociationFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LazyAssociationRegistrationFilter | None
    association_type: LazyClassFilter | None
    association_types: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'association_type' filter",
    )
    association_type_user_keys: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'association_type' filter",
    )
    it_association: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.ClassFilter, description="Class filter."
)
class ClassFilter(BaseFilter):
    registration: LazyClassRegistrationFilter | None
    name: strawberry.auto
    facet: LazyFacetFilter | None
    facets: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'facet' filter",
    )
    facet_user_keys: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'facet' filter",
    )
    parent: LazyClassFilter | None
    parents: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'parent' filter",
    )
    parent_user_keys: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'parent' filter",
    )
    it_system: LazyITSystemFilter | None
    owner: LazyClassOwnerFilter | None
    scope: strawberry.auto


@strawberry.input(description="Configuration filter.")
class ConfigurationFilter:
    identifiers: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Key", "identifiers"),
    )


@strawberry.experimental.pydantic.input(
    model=filter_models.EmployeeFilter, description="Employee filter."
)
class EmployeeFilter(BaseFilter):
    registration: LazyEmployeeRegistrationFilter | None
    query: strawberry.auto
    cpr_numbers: strawberry.auto
    owner: LazyOwnerFilter | None
    ituser: LazyITUserFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.EngagementFilter, description="Engagement filter."
)
class EngagementFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LazyEngagementRegistrationFilter | None
    job_function: LazyClassFilter | None
    engagement_type: LazyClassFilter | None
    ituser: LazyITUserFilter | None
    primary: LazyClassFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.FacetFilter, description="Facet filter."
)
class FacetFilter(BaseFilter):
    registration: LazyFacetRegistrationFilter | None
    parent: LazyFacetFilter | None
    parents: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'parent' filter",
    )
    parent_user_keys: strawberry.auto = strawberry.field(
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
    file_name_contains: str | None = strawberry.field(
        default=None,
        description=gen_filter_string(
            "Case-insensitive substring of the filename",
            "file_name_contains",
        ),
    )


@strawberry.input(description="Health filter.")
class HealthFilter:
    identifiers: list[str] | None = strawberry.field(
        default=None,
        description=gen_filter_string("Healthcheck identifiers", "identifiers"),
    )


@strawberry.experimental.pydantic.input(
    model=filter_models.ITSystemFilter, description="IT system filter."
)
class ITSystemFilter(BaseFilter):
    registration: LazyITSystemRegistrationFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.ITUserFilter, description="IT user filter."
)
class ITUserFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LazyITUserRegistrationFilter | None
    itsystem: LazyITSystemFilter | None
    itsystem_uuids: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'itsystem' filter",
    )
    engagement: LazyEngagementFilter | None
    rolebinding: LazyRoleBindingFilter | None
    external_ids: strawberry.auto
    binding_types: strawberry.auto
    primary: LazyClassFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.KLEFilter, description="KLE filter."
)
class KLEFilter(BaseFilter, OrganisationUnitFiltered):
    registration: LazyKLERegistrationFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.LeaveFilter, description="Leave filter."
)
class LeaveFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LazyLeaveRegistrationFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.ManagerFilter, description="Manager filter."
)
class ManagerFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    registration: LazyManagerRegistrationFilter | None
    engagement: LazyEngagementFilter | None
    responsibility: LazyClassFilter | None
    manager_type: LazyClassFilter | None
    exclude: LazyEmployeeFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.OrganisationUnitFilter,
    description=dedent(
        """\
        Organisation unit filter.

        Consider the tree:
        ```
            root
            / \\
           l   r
          /   / \\
        ll   rl  rr
        ```
        Setting a filter to `filter=value`, yields:

        filter     | value  | result                | note           |
        -----------|--------|-----------------------|----------------|
        user_keys  | `root` | `[root]`              |                |
        user_keys  | `r`    | `[r]`                 |                |
        user_keys  | `rl`   | `[rl]`                |                |
        child      | `null` | `[ll, rl, rr]`        | Leaf nodes     |
        child      | `{}`   | `[root, l, r]`        | Inner nodes    |
        child      | `r`    | `[root]`              | Parent node    |
        child      | `rl`   | `[r]`                 | Parent node    |
        descendant | `null` | `[root,l,r,ll,rl,rr]` | All nodes      |
        descendant | `{}`   | `[root,l,r,ll,rl,rr]` | All nodes      |
        descendant | `r`    | `[root, r]`           |                |
        descendant | `rl`   | `[root, r, rl]`       |                |
        parent     | `null` | `[root]`              | Root node      |
        parent     | `{}`   | `[l,r,ll,rl,rr]`      | Non-root nodes |
        parent     | `r`    | `[rl,rr]`             | Child nodes    |
        parent     | `rl`   | `[]`                  | No children    |
        ancestor   | `null` | `[root,l,r,ll,rl,rr]` | All nodes      |
        ancestor   | `{}`   | `[root,l,r,ll,rl,rr]` | All nodes      |
        ancestor   | `r`    | `[r, rl, rr]`         |                |
        ancestor   | `rl`   | `[rl]`                |                |

        These can ofcourse be combined too, such that:
        * `{child: {}, parent: {}}` returns all non-root inner nodes.
        * `{child: null, parent: null}` returns all childless roots.
        * `{child: {}, parent: null}` returns all roots with children.
        * ...
        """
    ),
)
class OrganisationUnitFilter(BaseFilter):
    registration: LazyOrganisationUnitRegistrationFilter | None
    query: strawberry.auto
    names: strawberry.auto
    parent: LazyOrganisationUnitFilter | None
    parents: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'parent' filter",
    )
    child: LazyOrganisationUnitFilter | None
    hierarchy: LazyClassFilter | None
    hierarchies: strawberry.auto = strawberry.field(
        deprecation_reason="Replaced by the 'hierarchy' filter",
    )
    subtree: LazyOrganisationUnitFilter | None = strawberry.field(
        deprecation_reason="Renamed to 'descendant'",
    )
    descendant: LazyOrganisationUnitFilter | None
    ancestor: LazyOrganisationUnitFilter | None
    engagement: LazyEngagementFilter | None
    owner: LazyOwnerFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.OwnerFilter, description="Owner filter."
)
class OwnerFilter(BaseFilter, EmployeeFiltered, OrganisationUnitFiltered):
    owner: LazyEmployeeFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.RegistrationFilter, description="Registration filter."
)
class RegistrationFilter:
    uuids: strawberry.auto
    actors: strawberry.auto
    models: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.AddressRegistrationFilter,
    description="Address registration filter.",
)
class AddressRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.AssociationRegistrationFilter,
    description="Association registration filter.",
)
class AssociationRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.ClassRegistrationFilter,
    description="Class registration filter.",
)
class ClassRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.EmployeeRegistrationFilter,
    description="Employee registration filter.",
)
class EmployeeRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.EngagementRegistrationFilter,
    description="Engagement registration filter.",
)
class EngagementRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.FacetRegistrationFilter,
    description="Facet registration filter.",
)
class FacetRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.ITSystemRegistrationFilter,
    description="ITSystem registration filter.",
)
class ITSystemRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.ITUserRegistrationFilter,
    description="ITUser registration filter.",
)
class ITUserRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.KLERegistrationFilter,
    description="KLE registration filter.",
)
class KLERegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.LeaveRegistrationFilter,
    description="Leave registration filter.",
)
class LeaveRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.ManagerRegistrationFilter,
    description="Manager registration filter.",
)
class ManagerRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.OrganisationUnitRegistrationFilter,
    description="OrganisationUnit registration filter.",
)
class OrganisationUnitRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.RoleRegistrationFilter,
    description="Role registration filter.",
)
class RoleRegistrationFilter:
    actors: strawberry.auto
    start: strawberry.auto
    end: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=filter_models.RelatedUnitFilter,
    description="Related unit filter.",
    all_fields=True,
)
class RelatedUnitFilter(BaseFilter, OrganisationUnitFiltered):
    pass


@strawberry.experimental.pydantic.input(
    model=filter_models.RoleBindingFilter, description="Rolebinding filter."
)
class RoleBindingFilter(BaseFilter, OrganisationUnitFiltered):
    registration: LazyRoleRegistrationFilter | None
    ituser: LazyITUserFilter | None
    role: LazyClassFilter | None


@strawberry.experimental.pydantic.input(
    model=filter_models.ClassOwnerFilter, description="Class owner filter"
)
class ClassOwnerFilter(OrganisationUnitFilter):
    include_none: strawberry.auto
