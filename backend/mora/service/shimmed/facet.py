#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from operator import itemgetter
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union
from uuid import UUID

from fastapi import Path
from fastapi import Query
from fastapi.encoders import jsonable_encoder
from more_itertools import one
from pydantic import BaseModel
from pydantic import Field
from pydantic.generics import GenericModel

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
    class Config:
        schema_extra = {
            "example": {
                "uuid": "51203743-f2db-4f17-a7e1-fee48c178799",
                "name": "Direktørområde",
                "user_key": "Direktørområde",
                "example": None,
                "scope": "TEXT",
                "owner": None,
            }
        }

    uuid: UUID = Field(description="The UUID of the class.")
    name: str = Field(description="Name of the class.")
    user_key: str = Field(description="Short, unique key.")
    example: Optional[str] = Field(description="Example string.")
    scope: Optional[str] = Field(description="Scope of the class.")
    owner: Optional[UUID] = Field(description="Owner of the class.")

    # Selectable fields
    full_name: Optional[str] = Field(description="Fullname of the class.")
    facet: Optional[MOFacetRead] = Field(
        description="Facet under which the class exists."
    )
    top_level_facet: Optional[MOFacetRead] = Field(
        description="Top level facet under which the class exists."
    )


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
    except ValueError as err:
        raise ValueError("Wrong number of classes returned, expected one.") from err
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

    def construct(facet: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "uuid": facet["uuid"],
            "user_key": facet["user_key"],
            "description": facet["description"],
            "path": facet_router.url_path_for(
                "get_classes", orgid=orgid, facet=facet["user_key"]
            ),
        }

    facets = filter(filter_by_orgid, facets)
    return list(map(construct, facets))


DataT = TypeVar("DataT")


class MOPaged(GenericModel, Generic[DataT]):
    class Config:
        schema_extra = {
            "example": {
                "total": 1,
                "offset": 0,
                "items": [
                    {
                        "uuid": "51203743-f2db-4f17-a7e1-fee48c178799",
                        "name": "Direktørområde",
                        "user_key": "Direktørområde",
                        "example": None,
                        "scope": "TEXT",
                        "owner": None,
                    }
                ],
            }
        }

    total: int = Field(description="Total number of results")
    offset: int = Field(description="Offset of results")
    items: List[DataT] = Field(description="Actual results")


class MOFacetAllClasses(BaseModel):
    class Config:
        schema_extra = {
            "example": {
                "uuid": "598b261e-8bd4-4fa2-964a-7d9fa2f2713d",
                "user_key": "org_unit_type",
                "description": "",
                "data": {
                    "total": 1,
                    "offset": 0,
                    "items": [
                        {
                            "uuid": "51203743-f2db-4f17-a7e1-fee48c178799",
                            "name": "Direktørområde",
                            "user_key": "Direktørområde",
                            "example": None,
                            "scope": "TEXT",
                            "owner": None,
                        }
                    ],
                },
            }
        }

    uuid: UUID = Field(description="The UUID of the facet.")
    user_key: str = Field(description="Short, unique key.")
    description: str = Field(description="Description of the facet object.", default="")
    data: MOPaged[Union[MOClassReturn, UUIDObject]] = Field(
        description="Paged listing of classes"
    )


async def facet_user_key_to_uuid(user_key: str) -> Optional[UUID]:
    """Find the UUID of a facet using its user_key.

    Args:
        user_key: The user_key to query.

    Returns:
        UUID of the facet if found.
    """
    query = """
    query FacetQuery {
      facets {
        uuid
        user_key
      }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)
    facets = response.data["facets"]
    if not facets:
        return None
    facet_map = dict(map(itemgetter("user_key", "uuid"), facets))
    return facet_map.get(user_key)


@facet_router.get(
    "/f/{facet}/",
    response_model=MOFacetAllClasses,
    response_model_exclude_unset=True,
    responses={404: {"description": "Facet not found."}},
)
async def get_all_classes(
    facet: Union[str, UUID] = Path(..., description="UUID or user_key of a facet."),
    start: int = Query(0, description="Index of the first item for paging."),
    limit: Optional[int] = Query(
        None, description="Maximum number of items to return."
    ),
    only_primary_uuid: Optional[bool] = Query(
        None, description="Only retrieve the UUID of the class unit."
    ),
):
    """List classes available in the given facet."""
    # If given a user_key we want to convert it to an UUID
    try:
        facet_uuid = UUID(facet)
    except ValueError:
        facet_uuid = await facet_user_key_to_uuid(facet)
        if facet_uuid is None:
            exceptions.ErrorCodes.E_UNKNOWN()

    query = """
    query FacetChildrenQuery(
        $uuid: UUID!,
        $only_primary_uuid: Boolean!
    ) {
      facets(uuids: [$uuid]) {
        uuid
        user_key
        description
        classes @include(if: $only_primary_uuid) {
            uuid
        }
        classes @skip(if: $only_primary_uuid) {
            uuid
            name
            user_key
            example
            scope
            owner
        }
      }
    }
    """
    response = await execute_graphql(
        query,
        {
            "uuid": str(facet_uuid),
            "only_primary_uuid": bool(only_primary_uuid),
        },
    )
    handle_gql_error(response)
    facets = response.data["facets"]
    if not facets:
        exceptions.ErrorCodes.E_UNKNOWN()
    try:
        facet: dict[str, Any] = one(facets)
    except ValueError as err:
        raise ValueError("Wrong number of facets returned, expected one.") from err
    children = facet["classes"]
    del facet["classes"]

    total = len(children)
    if start:
        children = children[start:]
    if limit:
        children = children[:limit]

    facet["data"] = {
        "total": total,
        "offset": start,
        "items": children,
    }
    return facet