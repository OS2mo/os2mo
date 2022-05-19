#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from uuid import UUID

from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from pydantic import BaseModel
from pydantic import Field

from .errors import handle_gql_error
from mora import exceptions
from mora.graphapi.shim import execute_graphql
from mora.graphapi.shim import MOFacetRead
from mora.graphapi.shim import UUIDObject
from mora.service.facet import router as facet_router

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------


class MOClassReturn(BaseModel):
    uuid: UUID
    name: str
    user_key: str
    example: Optional[str]
    scope: Optional[str]
    owner: Optional[UUID]
    # Optional fields
    full_name: Optional[str]
    facet: Optional[MOFacetRead]
    top_level_facet: Optional[MOFacetRead]


@facet_router.get(
    "/c/{classid}/",
    response_model=Union[MOClassReturn, UUIDObject],
    response_model_exclude_unset=True,
    responses={404: {"description": "Class not found."}},
)
async def get_class(
    classid: UUID = Path(..., description="UUID of the class to retrieve."),
    only_primary_uuid: Optional[bool] = Query(
        None, description="Only retrieve the UUID of the class unit."
    ),
    full_name: Optional[bool] = Query(
        None, description="Include full name in response."
    ),
    top_level_facet: Optional[bool] = Query(
        None, description="Include top-level facet in response."
    ),
    facet: Optional[bool] = Query(None, description="Include facet in response."),
) -> dict[str, Any]:
    """Get a class."""
    variables = {
        "uuid": classid,
        "full_name": bool(full_name),
        "top_level_facet": bool(top_level_facet),
        "facet": bool(facet),
    }
    if only_primary_uuid:
        query = """
        query ClassQuery($uuid: UUID!)
        {
            classes(uuids: [$uuid]) {
                uuid
            }
        }
        """
    else:
        query = """
        query ClassQuery(
            $uuid: UUID!,
            $full_name: Boolean!,
            $top_level_facet: Boolean!,
            $facet: Boolean!,
        ) {
            classes(uuids: [$uuid]) {
                uuid
                name
                user_key
                example
                scope
                owner

                full_name @include(if: $full_name)

                top_level_facet @include(if: $top_level_facet) {
                    ...facet_fields
                }

                facet @include(if: $facet) {
                    ...facet_fields
                }
            }
        }
        fragment facet_fields on Facet {
            uuid
            user_key
            description
        }
        """
    response = await execute_graphql(query, variable_values=jsonable_encoder(variables))
    handle_gql_error(response)

    # Handle org unit data
    class_list = response.data["classes"]
    if not class_list:
        exceptions.ErrorCodes.E_CLASS_NOT_FOUND(class_uuid=classid)
    try:
        clazz: dict[str, Any] = one(class_list)
    except ValueError:
        raise ValueError("Wrong number of classes returned, expected one.")
    return clazz


class MOFacetReturn(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "uuid": "182df2a8-2594-4a3f-9103-a9894d5e0c36",
                "user_key": "engagement_type",
                "description": "",
                "path": "/o/3b866d97-0b1f-48e0-8078-686d96f430b3/f/engagement_type/",
            }
        }

    uuid: UUID = Field(description="The UUID of the facet.")
    user_key: str = Field(description="Short, unique key.")
    description: str = Field(description="Description of the facet object.", default="")
    path: str = Field(description="The location on the web server.")


@facet_router.get(
    "/o/{orgid}/f/",
    response_model=List[MOFacetReturn],
    response_model_exclude_unset=True,
    responses={500: {"description": "Unknown Error."}},
)
async def list_facets(
    orgid: UUID = Path(
        ...,
        description="UUID of the organisation to retrieve facets from.",
        example="3b866d97-0b1f-48e0-8078-686d96f430b3",
    ),
):
    """List the facet types available in a given organisation."""
    query = """
    query FacetQuery {
      facets {
        uuid
        user_key
        description
        org_uuid
      }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)

    # Handle org unit data
    facets = response.data["facets"]
    if not facets:
        exceptions.ErrorCodes.E_UNKNOWN()

    def filter_by_orgid(facet: Dict[str, Any]) -> bool:
        return UUID(facet["org_uuid"]) == orgid

    def remove_org_uuid(facet: Dict[str, Any]) -> Dict[str, Any]:
        del facet["org_uuid"]
        return facet

    def add_path(facet: Dict[str, Any]) -> Dict[str, Any]:
        facet["path"] = facet_router.url_path_for(
            "get_classes", orgid=orgid, facet=facet["user_key"]
        )
        return facet

    facets = filter(filter_by_orgid, facets)
    facets = map(remove_org_uuid, facets)
    facets = map(add_path, facets)
    return list(facets)
