#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date
from datetime import datetime
from operator import itemgetter
from typing import Any
from typing import Literal
from typing import Optional
from typing import Union
from uuid import UUID

from fastapi import Body
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from more_itertools import unzip
from pydantic import BaseModel
from pydantic import Field

from ...auth.keycloak import oidc
from .errors import handle_gql_error
from .util import filter_data
from mora import exceptions
from mora import util
from mora.graphapi.models import OrganisationUnitRefreshRead
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.shim import MOOrgUnit
from mora.graphapi.shim import OrganisationUnitCount
from mora.graphapi.shim import UUIDObject
from mora.service.orgunit import router as org_unit_router
from mora.service.util import get_configuration
from ramodels.mo.organisation_unit import OrganisationUnitTerminate


# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class ListOrgunitsValidity(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "from": "1960-01-01",
                "to": None
            }
        }

    from_date: str = Field(alias="from", description="Validity from date")
    to_date: Optional[str] = Field(alias="to", description="Validity to date")


class ListOrgunitsEntry(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "name": "Hj\u00f8rring b\u00f8rnehus",
                "user_key": "Hj\u00f8rring b\u00f8rnehus",
                "uuid": "391cf990-31a0-5104-8944-6bdc4c934b7a",
                "validity": {
                    "from": "1960-01-01",
                    "to": None
                }
            }
        }

    name: str = Field(description="Human-readable name.")
    uuid: str = Field(description="Machine-friendly UUID.")
    user_key: str = Field(description="Short, unique key identifying the unit.")
    validity: ListOrgunitsValidity = Field(description="Validity range of the organisational unit.")


class ListOrgunitsReturn(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "name": "Hj\u00f8rring b\u00f8rnehus",
                        "user_key": "Hj\u00f8rring b\u00f8rnehus",
                        "uuid": "391cf990-31a0-5104-8944-6bdc4c934b7a",
                        "validity": {
                            "from": "1960-01-01",
                            "to": None
                        }
                    }
                ],
                "offset": 0,
                "total": 1
            }
        }

    items: list[ListOrgunitsEntry] = Field(description="The returned items.")
    offset: int = Field(description="Pagination offset.")
    total: int = Field(description="Total number of items available on this query.")


@org_unit_router.get(
    "/o/{orgid}/ou/",
    response_model=ListOrgunitsReturn,
    response_model_exclude_unset=True,
    responses={404: {"description": "Org unit not found"}},
)
async def list_orgunits(
    orgid: UUID = Path(
        ...,
        description="UUID of the organisation to retrieve facets from.",
        example="3b866d97-0b1f-48e0-8078-686d96f430b3",
    ),
    start: int = Query(0, description="Index of the first item for paging."),
    limit: Optional[int] = Query(
        0, description="Maximum number of items to return."
    ),
    query: Optional[str] = Query(None, description="Filter by units matching this string."),
    root: Optional[str] = Query(None, description="Filter by units in the subtree under this root."),
    hierarchy_uuids: Optional[list[UUID]] = Query(None, description="Filter units having one of these hierchies."),
    only_primary_uuid: Optional[bool] = Query(
        None, description="Only retrieve the UUID of the class unit."
    ),
    at: Optional[Union[date, datetime]] = Query(
        None, description="Show the units valid at this point in time, in ISO-8601 format."
    ),
    details: Optional[str] = Query(
        None, description="Level of details to return."
    ),
):
    """Query organisational units in an organisation."""
    gql_query = """
    query ListOrgUnits($from_date: DateTime, $query: String, $hierarchy_uuids: [UUID!]) {
      org_units(from_date: $from_date, query: $query, hierarchy_uuids: $hierarchy_uuids) {
        objects {
          uuid,
          user_key,
          org_unit_hierarchy,
          parent_uuid,
          name,
          validity {
            from,
            to
          }
        }
      }
      org {
        uuid
      }
    }
    """
    variables = {}
    if at is not None:
        variables["from_date"] = at
    if query is not None:
        variables["query"] = query
    if hierarchy_uuids is not None:
        variables["hierarchy_uuids"] = hierarchy_uuids

    response = await execute_graphql(gql_query, variable_values=jsonable_encoder(variables))
    handle_gql_error(response)
    
    org_uuid = response.data["org"]["uuid"]
    if org_uuid != str(orgid):
        return {
            "offset": start or 0,
            "total": 0,
            "items": []
        }

    objects = sorted(
        map(one, map(itemgetter("objects"), response.data["org_units"])),
        key=lambda obj: obj["uuid"]
    )
    uuids = list(map(itemgetter("uuid"), objects))

    uuid_filters = []
    if root:
        # Fetch parent_uuid from objects
        parent_uuids = map(itemgetter("parent_uuid"), objects)
        # Create map from uuid --> parent_uuid
        parent_map = dict(zip(uuids, parent_uuids))

        def entry_under_root(uuid: str) -> bool:
            """Check whether the given uuid is in the subtree under 'root'.

            Works by recursively ascending the parent_map.

            If the specified root is found, we must have started in its subtree.
            If the specified root is not found, we will stop searching at the
                root of the organisation tree.
            """
            if uuid not in parent_map:
                return False
            return uuid == root or entry_under_root(parent_map[uuid])

        uuid_filters.append(entry_under_root)

    for uuid_filter in uuid_filters:
        uuids = filter(uuid_filter, uuids)
    uuids = set(uuids)

    objects = list(filter(lambda obj: obj["uuid"] in uuids, objects))
    objects = objects[start:]
    if limit:
        objects = objects[:limit]

    details = details or "minimal"

    def construct_time(time):
        if time is None:
            return None
        return time.split("T")[0]

    def construct(obj):
        return {
            "name": obj["name"],
            "user_key": obj["user_key"],
            "uuid": obj["uuid"],
            "validity": {
                "from": construct_time(obj["validity"]["from"]),
                "to": construct_time(obj["validity"].get("to")),
            }
        }

    result = {
        "offset": start or 0,
        "total": len(objects),
        "items": list(map(construct, objects))
    }
    print(result)
    return result


@org_unit_router.get(
    "/ou/{unitid}/",
    response_model=Union[MOOrgUnit, UUIDObject],
    response_model_exclude_unset=True,
    responses={404: {"description": "Org unit not found"}},
)
async def get_orgunit(
    unitid: UUID = Path(..., description="UUID of the unit to retrieve."),
    only_primary_uuid: Optional[bool] = Query(
        None, description="Only retrieve the UUID of the organisation unit"
    ),
    at: Optional[Union[date, datetime]] = Query(
        None,
        description='The "at date" to use, e.g. `2020-01-31`. '
        "Results are only included if they are active at the specified date.",
    ),
    count: set[Literal["engagement", "association"]] = Query(
        set(),
        description="The name(s) of related objects to count. "
        "If `count=association`, each organisational unit in the tree is annotated "
        "with an additional `association_count` key which contains the number of "
        "associations in the unit. `count=engagement` is also allowed. "
        "It is allowed to pass more than one `count` query parameter.",
    ),
) -> dict[str, Any]:
    """Get an organisational unit."""
    # Create query variables
    variables = {
        "uuid": unitid,
        "engagements": "engagement" in count,
        "associations": "association" in count,
    }
    if at is not None:
        variables["from_date"] = at
    unitid = str(unitid)
    if only_primary_uuid:
        query = """
        query OrganisationUnitQuery($uuid: UUID!)
        {
            org_units(uuids: [$uuid]) {
                objects {
                    uuid
                }
            }
        }
        """
    else:
        query = """
        query OrganisationUnitQuery(
            $uuid: UUID!,
            $from_date: DateTime,
            $engagements: Boolean!,
            $associations: Boolean!,
        ) {
            org_units(uuids: [$uuid], from_date: $from_date) {
                objects {
                    name
                    user_key
                    uuid
                    parent_uuid
                    unit_type {
                        ...class_fields
                    }
                    time_planning {
                        ...class_fields
                    }
                    org_unit_level {
                        ...class_fields
                    }
                    validity {
                        from
                        to
                    }
                    associations @include(if: $associations) {
                        uuid
                    }
                    engagements @include(if: $engagements) {
                        uuid
                    }
                }
            }
            org {
                name
                user_key
                uuid
            }
        }
        fragment class_fields on Class {
            uuid
            name
            full_name
            user_key
            example
            scope
            owner
            top_level_facet {
                uuid
                user_key
                description
            }
            facet {
                uuid
                user_key
                description
            }
        }
        """
    response = await execute_graphql(query, variable_values=jsonable_encoder(variables))
    handle_gql_error(response)

    # Handle org unit data
    org_unit_list = flatten_data(response.data["org_units"])
    if not org_unit_list:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=unitid)
    try:
        org_unit: dict[str, Any] = one(org_unit_list)
    except ValueError:
        raise ValueError("Wrong number of org units returned, expected one.")

    if only_primary_uuid:
        return org_unit

    # Add counts if present
    if "engagements" in org_unit:
        org_unit["engagement_count"] = len(org_unit.pop("engagements", []))
    if "associations" in org_unit:
        org_unit["association_count"] = len(org_unit.pop("associations", []))

    # The following is basically a reimplementation of get_one_orgunit
    # with details = FULL.
    org = response.data["org"]
    org_unit["org"] = org
    org_unit["location"] = ""
    org_unit["org_unit_type"] = org_unit.pop("unit_type", None)
    settings = {}
    parent_uuid = org_unit.pop("parent_uuid", None)

    # Recurse to get parents
    if parent_uuid and parent_uuid != org["uuid"]:
        parent = await get_orgunit(
            parent_uuid, only_primary_uuid=only_primary_uuid, count=count, at=at
        )
        # Settings
        parent_settings = parent["user_settings"]["orgunit"]
        for setting, value in parent_settings.items():
            settings.setdefault(setting, value)

        # Parent location
        if parent["location"]:
            org_unit["location"] = parent["location"] + "\\" + parent["name"]
        else:
            org_unit["location"] = parent["name"]

        # Update org unit
        org_unit["parent"] = parent

    org_unit.setdefault("parent", None)
    global_settings = await get_configuration()
    for setting, value in global_settings.items():
        settings.setdefault(setting, value)

    org_unit["user_settings"] = {"orgunit": settings}
    return org_unit


@org_unit_router.get(
    "/ou/{parentid}/children",
    response_model=list[OrganisationUnitCount],
    response_model_exclude_unset=True,
    responses={"404": {"description": "Org unit not found"}},
)
async def get_org_unit_children(
    parentid: UUID = Path(..., description="The UUID of the parent."),
    at: Optional[Union[date, datetime]] = Query(
        None,
        description='The "at date" to use, e.g. `2020-01-31`. '
        "Results are only included if they are active at the specified date.",
    ),
    count: set[Literal["engagement", "association"]] = Query(
        set(),
        description="The name(s) of related objects to count. "
        "If `count=association`, each organisational unit in the tree is annotated "
        "with an additional `association_count` key which contains the number of "
        "associations in the unit. `count=engagement` is also allowed. "
        "It is allowed to pass more than one `count` query parameter.",
    ),
    org_unit_hierarchy: Optional[UUID] = Query(
        None,
        description="The tree returned is filtered to contain "
        "only organisational units which belong to the given hierarchy.",
    ),
):
    """Obtain the list of nested units within an organisational unit."""
    query = """
    query OrganisationUnitChildrenQuery(
        $uuid: UUID!, $from_date: DateTime,
        $engagements: Boolean!, $associations: Boolean!, $hierarchy: Boolean!
    )
    {
        org_units(uuids: [$uuid], from_date: $from_date) {
            objects {
                children {
                    uuid
                    child_count
                    org_unit_hierarchy @include(if: $hierarchy)
                    name
                    user_key
                    associations @include(if: $associations) {
                        uuid
                    }
                    engagements @include(if: $engagements) {
                        uuid
                    }
                    validity {
                        from
                        to
                    }
                }
            }
        }
    }

    """
    variables = {
        "uuid": parentid,
        "engagements": "engagement" in count,
        "associations": "association" in count,
        "hierarchy": bool(org_unit_hierarchy),
    }
    if at is not None:
        variables["from_date"] = at

    response = await execute_graphql(query, variable_values=jsonable_encoder(variables))
    handle_gql_error(response)

    org_unit_list = flatten_data(response.data["org_units"])
    if not org_unit_list:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=str(parentid))
    try:
        org_unit: dict[str, Any] = one(org_unit_list)
    except ValueError:
        raise ValueError("Wrong number of parent units returned, expected one.")

    ou_children = org_unit["children"]
    if org_unit_hierarchy is not None:
        ou_children = list(
            filter_data(ou_children, "org_unit_hierarchy", str(org_unit_hierarchy))
        )
    for child in ou_children:
        if "engagements" in child:
            child["engagement_count"] = len(child.pop("engagements"))
        if "associations" in child:
            child["association_count"] = len(child.pop("associations"))

    return ou_children


@org_unit_router.get(
    "/ou/{unitid}/refresh",
    response_model=OrganisationUnitRefreshRead,
    response_model_exclude_unset=True,
    responses={"404": {"description": "Org unit not found"}},
)
async def trigger_external_integration(
    unitid: UUID = Path(..., description="UUID of the org unit to trigger for."),
    only_primary_uuid: bool = Query(False, description="Unused argument"),
) -> OrganisationUnitRefreshRead:
    """Trigger external integration for a given org unit UUID."""
    query = """
    mutation($uuid: UUID!) {
      org_unit_refresh(uuid: $uuid) { message }
    }
    """
    response = await execute_graphql(query, variable_values={"uuid": str(unitid)})
    handle_gql_error(response)
    result = response.data["org_unit_refresh"]
    return OrganisationUnitRefreshRead(**result)


@org_unit_router.post(
    "/ou/{uuid}/terminate",
    responses={
        200: {
            "description": "The termination succeeded",
            "model": UUID,
        },
        404: {"description": "No such unit found"},
        409: {"description": "Validation failed"},
    },
)
async def terminate_org_unit(
    uuid: UUID,
    request: OrganisationUnitTerminate = Body(...),
    permissions=Depends(oidc.rbac_owner),
):
    mutation_func = "org_unit_terminate"
    query = (
        f"mutation($uuid: UUID!, $from: DateTime, $to: DateTime, $triggerless: Boolean) "
        f"{{ {mutation_func}"
        f"(unit: {{uuid: $uuid, from: $from, to: $to, triggerless: $triggerless}}) "
        f"{{ uuid }} }}"
    )

    response = await execute_graphql(
        query,
        variable_values={
            "uuid": str(uuid),
            "from": request.validity.from_date.isoformat()
            if request.validity.from_date
            else None,
            "to": request.validity.to_date.isoformat()
            if request.validity.to_date
            else None,
            "triggerless": util.get_args_flag("triggerless"),
        },
    )
    handle_gql_error(response)

    # result = response.data[mutation_func]
    result_uuid = response.data.get(mutation_func, {}).get("uuid", None)
    if not result_uuid:
        raise Exception("Did not get a valid UUID from GraphQL response")

    return UUID(result_uuid)
