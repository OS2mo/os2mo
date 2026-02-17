# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal
from uuid import UUID

from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import ilen
from more_itertools import one
from ramodels.mo import OrganisationRead

from mora import exceptions
from mora.graphapi.shim import OrganisationLevelRead
from mora.graphapi.shim import OrganisationUnitCount
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.service.org import router as org_router

from .errors import handle_gql_error


@org_router.get(
    "/o/",
    response_model=list[OrganisationRead],
    response_model_exclude_unset=True,
)
async def list_organisations() -> list[OrganisationRead]:
    """List displayable organisations.

    This endpoint is retained for backwards compatibility.
    It will always return a list of only one organisation as only one organisation
    is currently allowed.

    """
    query = """
    query OrganisationQuery {
      org {
        uuid, user_key, name
      }
    }
    """
    r = await execute_graphql(query)
    if r.errors:  # pragma: no cover
        error = one(r.errors)
        if error.original_error:
            raise error.original_error
        raise ValueError(error)
    return [r.data["org"]]


@org_router.get(
    "/o/{orgid}/",
    response_model=OrganisationLevelRead,
    response_model_exclude_unset=True,
)
async def get_organisation(
    orgid: UUID = Path(..., description="UUID of the organisation"),
) -> OrganisationLevelRead:
    """Obtain the initial level of an organisation."""
    query = """
    query OrganisationQuery {
      employees {
        objects { objects { uuid } }
      }
      org_units {
        objects { objects { uuid, parent_uuid } }
      }
      associations {
        objects { objects { uuid } }
      }
      engagements {
        objects { objects { uuid } }
      }
      leaves {
        objects { objects { uuid } }
      }
      rolebindings {
        objects { objects { uuid } }
      }
      managers {
        objects { objects { uuid } }
      }
      org {
        uuid, user_key, name
      }
    }
    """
    # Execute GraphQL query to fetch required data
    response = await execute_graphql(query)
    handle_gql_error(response)

    if response.data["org"]["uuid"] != str(orgid):  # pragma: no cover
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    def filter_data(data: Iterable, key: str, value: Any) -> filter:
        return filter(lambda obj: obj[key] == value, data)

    org_units = flatten_data(response.data["org_units"]["objects"])
    child_count = ilen(filter_data(org_units, "parent_uuid", None))
    return {
        "uuid": response.data["org"]["uuid"],
        "user_key": response.data["org"]["user_key"],
        "name": response.data["org"]["name"],
        "child_count": child_count,
        "person_count": len(response.data["employees"]["objects"]),
        "unit_count": len(response.data["org_units"]["objects"]),
        "engagement_count": len(response.data["engagements"]["objects"]),
        "association_count": len(response.data["associations"]["objects"]),
        "leave_count": len(response.data["leaves"]["objects"]),
        "role_count": len(response.data["rolebindings"]["objects"]),
        "manager_count": len(response.data["managers"]["objects"]),
    }


@org_router.get(
    "/o/{parentid}/children",
    response_model=list[OrganisationUnitCount],
    response_model_exclude_unset=True,
)
async def get_org_children(
    parentid: UUID = Path(..., description="UUID of the parent"),
    at: date | datetime | None = Query(
        None,
        description="Show the children valid at this point in time, in ISO-8601 format",
    ),
    count: set[Literal["engagement", "association"]] = Query(
        set(),
        description="The name(s) of related objects to count. "
        "If `count=association`, each organisational unit in the tree is annotated "
        "with an additional `association_count` key which contains the number of "
        "associations in the unit. `count=engagement` is also allowed. "
        "It is allowed to pass more than one `count` query parameter.",
    ),
    org_unit_hierarchy: UUID | None = Query(
        None,
        description="The tree returned is filtered to contain "
        "only organisational units which belong to the given hierarchy.",
    ),
) -> list[OrganisationUnitCount]:
    """Obtain the list of nested units within an organisation."""
    # Check org exists
    query = """
    query CheckOrg {
        org {
            uuid
        }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)

    if response.data["org"]["uuid"] != str(parentid):
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    query = """
    query OrganisationChildrenQuery(
        $parents: [UUID!]
        $from_date: DateTime,
        $engagements: Boolean!,
        $associations: Boolean!,
        $hierarchies: [UUID!]
    ) {
        org_units(
            filter: {
                parents: $parents,
                hierarchies: $hierarchies,
                from_date: $from_date,
            },
        ) {
            objects {
                objects {
                    name
                    user_key
                    uuid
                    validity {
                        from
                        to
                    }
                    child_count(filter: {hierarchies: $hierarchies})
                    associations @include(if: $associations) {
                        uuid
                    }
                    engagements @include(if: $engagements) {
                        uuid
                    }
                }
            }
        }
    }
    """
    variables = {
        "parents": parentid,
        "engagements": "engagement" in count,
        "associations": "association" in count,
        "hierarchies": org_unit_hierarchy,
    }
    if at is not None:  # pragma: no cover
        variables["from_date"] = at
    response = await execute_graphql(
        query,
        variable_values=jsonable_encoder(variables),
    )
    handle_gql_error(response)

    org_units = flatten_data(response.data["org_units"]["objects"])
    for unit in org_units:
        unit |= (
            {"engagement_count": len(unit.pop("engagements", []))}
            if "engagement" in count
            else {}
        )
        unit |= (
            {"association_count": len(unit.pop("associations", []))}
            if "association" in count
            else {}
        )

    return org_units
