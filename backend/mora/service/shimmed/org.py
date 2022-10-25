# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Literal
from uuid import UUID

from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import ilen
from more_itertools import one

from .errors import handle_gql_error
from .util import filter_data
from mora import exceptions
from mora.common import _create_graphql_connector
from mora.graphapi.middleware import set_graphql_dates
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.shim import OrganisationLevelRead
from mora.graphapi.shim import OrganisationUnitCount
from mora.service.org import router as org_router
from ramodels.mo import OpenValidity
from ramodels.mo import OrganisationRead


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
    if r.errors:
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
    orgid: UUID = Path(..., description="UUID of the organisation")
) -> OrganisationLevelRead:
    """Obtain the initial level of an organisation."""
    query = """
    query OrganisationQuery {
      employees {
        objects { uuid }
      }
      org_units {
        objects { uuid, parent_uuid }
      }
      associations {
        objects { uuid }
      }
      engagements {
        objects { uuid }
      }
      leaves {
        objects { uuid }
      }
      roles {
        objects { uuid }
      }
      managers {
        objects { uuid }
      }
      org {
        uuid, user_key, name
      }
    }
    """
    # Execute GraphQL query to fetch required data
    response = await execute_graphql(query)
    handle_gql_error(response)

    if response.data["org"]["uuid"] != str(orgid):
        exceptions.ErrorCodes.E_NO_SUCH_ENDPOINT()

    org_units = flatten_data(response.data["org_units"])
    child_count = ilen(filter_data(org_units, "parent_uuid", str(orgid)))
    return {
        "uuid": response.data["org"]["uuid"],
        "user_key": response.data["org"]["user_key"],
        "name": response.data["org"]["name"],
        "child_count": child_count,
        "person_count": len(response.data["employees"]),
        "unit_count": len(response.data["org_units"]),
        "engagement_count": len(response.data["engagements"]),
        "association_count": len(response.data["associations"]),
        "leave_count": len(response.data["leaves"]),
        "role_count": len(response.data["roles"]),
        "manager_count": len(response.data["managers"]),
    }


@org_router.get(
    "/o/{parentid}/children",
    response_model=list[OrganisationUnitCount],
    response_model_exclude_unset=True,
)
async def get_org_children(
    parentid: UUID = Path(..., description="UUID of the parent"),
    at: date
    | datetime
    | None = Query(
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
    org_unit_hierarchy: UUID
    | None = Query(
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

    # This sucks! We should port this parent functionality to our
    # GraphQL loaders instead
    if at is not None:
        if isinstance(at, date):
            at = datetime.combine(at, datetime.min.time())
        set_graphql_dates(
            OpenValidity(from_date=at, to_date=at + timedelta(milliseconds=1))
        )
    connector = _create_graphql_connector()
    children = await connector.organisationenhed.load_uuids(
        overordnet=parentid,
        gyldighed="Aktiv",
    )
    query = """
    query OrganisationChildrenQuery(
        $uuids: [UUID!]
        $from_date: String,
        $engagements: Boolean!,
        $associations: Boolean!,
        $hierarchy: Boolean!) {
            org_units(uuids: $uuids, from_date: $from_date) {
                objects {
                    name
                    user_key
                    uuid
                    validity {
                        from
                        to
                    }
                    children {
                        uuid
                        org_unit_hierarchy @include(if: $hierarchy)
                    }
                    associations @include(if: $associations) {
                        uuid
                    }
                    engagements @include(if: $engagements) {
                        uuid
                    }
                }
            }
        }
    """
    variables = {
        "uuids": children,
        "engagements": "engagement" in count,
        "associations": "association" in count,
        "hierarchy": bool(org_unit_hierarchy),
    }
    if at is not None:
        variables["from_date"] = at
    response = await execute_graphql(
        query,
        variable_values=jsonable_encoder(variables),
    )
    handle_gql_error(response)

    org_units = flatten_data(response.data["org_units"])
    if not org_units:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=str(parentid))

    for unit in org_units:
        ou_children = unit.pop("children")
        if org_unit_hierarchy is not None:
            ou_children = list(
                filter_data(ou_children, "org_unit_hierarchy", str(org_unit_hierarchy))
            )
        unit |= {"child_count": len(ou_children)}
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
