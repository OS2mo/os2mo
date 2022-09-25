# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal
from uuid import UUID

from fastapi import Body
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from ...auth.keycloak import oidc
from .errors import handle_gql_error
from .util import filter_data
from mora import exceptions
from mora import util
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.graphapi.shim import MOOrgUnit
from mora.graphapi.shim import OrganisationUnitCount
from mora.graphapi.shim import UUIDObject
from mora.graphapi.versions.latest.models import OrganisationUnitRefreshRead
from mora.service.orgunit import router as org_unit_router
from mora.service.util import get_configuration
from ramodels.mo.organisation_unit import OrganisationUnitTerminate


@org_unit_router.get(
    "/ou/{unitid}/",
    response_model=MOOrgUnit | UUIDObject,
    response_model_exclude_unset=True,
    responses={404: {"description": "Org unit not found"}},
)
async def get_orgunit(
    unitid: UUID = Path(..., description="UUID of the unit to retrieve."),
    only_primary_uuid: bool
    | None = Query(None, description="Only retrieve the UUID of the organisation unit"),
    at: date
    | datetime
    | None = Query(
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
    at: date
    | datetime
    | None = Query(
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
    org_unit_hierarchy: UUID
    | None = Query(
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
        f"mutation($uuid: UUID!, $from: DateTime, $to: DateTime!, $triggerless: Boolean) "
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
