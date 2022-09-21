# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Optional

import strawberry
from more_itertools import one
from more_itertools import only
from strawberry.types import Info

from ..latest.permissions import gen_read_permission
from ..latest.schema import OrganisationUnit as LatestOrganisationUnit
from ..v2.version import GraphQLVersion2
from mora.graphapi.shim import execute_graphql  # type: ignore[attr-defined]
from ramodels.mo import OrganisationUnitRead


# Organisation Unit
# -----------------
@strawberry.experimental.pydantic.type(
    model=OrganisationUnitRead,
    all_fields=True,
    description="Hierarchical unit within the organisation tree",
)
class OrganisationUnit(LatestOrganisationUnit):
    @strawberry.field(
        description="The immediate ancestor in the organisation tree",
        permission_classes=[gen_read_permission("org_units")],
    )
    async def parent(
        self, root: OrganisationUnitRead, info: Info
    ) -> Optional[list["OrganisationUnit"]]:
        """Implements backwards-compatibility of org unit parent.

        Returns an optional list of exactly one element, instead of an optional element.
        """
        if root.parent_uuid is None:
            return None
        response = await execute_graphql(
            """
            query OrgUnitParentQuery($uuid: UUID!) {
              org_units(uuids: [$uuid]) {
                objects {
                  uuid
                  user_key
                  type
                  name
                  parent_uuid
                  org_unit_hierarchy
                  unit_type_uuid
                  org_unit_level_uuid
                  time_planning_uuid
                  validity {
                    to
                    from
                  }
                }
              }
            }
            """,
            graphql_version=GraphQLVersion2,
            variable_values={"uuid": str(root.parent_uuid)},
            context_value=info.context,
        )
        parent: dict | None = only(response.data["org_units"])
        if parent is None:
            return []
        parent_object = one(parent["objects"])
        return [OrganisationUnitRead(**parent_object)]  # type: ignore[list-item]
