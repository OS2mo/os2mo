# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from typing import Any
from typing import Literal
from uuid import UUID

from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import one

from mora import exceptions
from mora.graphapi.shim import MOOrgUnit
from mora.graphapi.shim import UUIDObject
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import flatten_data
from mora.service.orgunit import router as org_unit_router

from .errors import handle_gql_error


@org_unit_router.get(
    "/ou/{unitid}/",
    response_model=MOOrgUnit | UUIDObject,
    response_model_exclude_unset=True,
    responses={404: {"description": "Org unit not found"}},
)
async def get_orgunit(
    unitid: UUID = Path(..., description="UUID of the unit to retrieve."),
    only_primary_uuid: bool | None = Query(
        None, description="Only retrieve the UUID of the organisation unit"
    ),
    at: date | datetime | None = Query(
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
    if only_primary_uuid:  # pragma: no cover
        query = """
        query OrganisationUnitQuery($uuid: UUID!)
        {
            org_units(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                    }
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
            org_units(filter: {uuids: [$uuid], from_date: $from_date}) {
                objects {
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
    org_unit_list = flatten_data(response.data["org_units"]["objects"])
    if not org_unit_list:
        exceptions.ErrorCodes.E_ORG_UNIT_NOT_FOUND(org_unit_uuid=unitid)
    try:
        org_unit: dict[str, Any] = one(org_unit_list)
    except ValueError:  # pragma: no cover
        raise ValueError("Wrong number of org units returned, expected one.")

    if only_primary_uuid:  # pragma: no cover
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
    parent_uuid = org_unit.pop("parent_uuid", None)

    # Recurse to get parents
    if parent_uuid and parent_uuid != org["uuid"]:
        parent = await get_orgunit(
            parent_uuid, only_primary_uuid=only_primary_uuid, count=count, at=at
        )

        # Parent location
        if parent["location"]:  # pragma: no cover
            org_unit["location"] = parent["location"] + "\\" + parent["name"]
        else:
            org_unit["location"] = parent["name"]

        # Update org unit
        org_unit["parent"] = parent

    org_unit.setdefault("parent", None)
    org_unit["user_settings"] = {"orgunit": {}}
    return org_unit
