# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from operator import itemgetter
from typing import Any
from typing import Generic
from typing import TypeVar
from uuid import UUID

from fastapi import Path
from fastapi import Query
from more_itertools import one
from pydantic import BaseModel
from pydantic import Field
from pydantic.generics import GenericModel

from mora import exceptions
from mora.graphapi.shim import MOFacetRead
from mora.graphapi.shim import UUIDObject
from mora.graphapi.shim import execute_graphql
from mora.service.facet import router as facet_router

from .errors import handle_gql_error


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
    example: str | None = Field(description="Example string.")
    scope: str | None = Field(description="Scope of the class.")
    owner: UUID | None = Field(description="Owner of the class.")
    published: str | None = Field(
        description="Published state of the class, represented as a string"
    )

    # Selectable fields
    full_name: str | None = Field(description="Fullname of the class.")
    facet: MOFacetRead | None = Field(description="Facet under which the class exists.")
    top_level_facet: MOFacetRead | None = Field(
        description="Top level facet under which the class exists."
    )


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
    items: list[DataT] = Field(description="Actual results")


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
    data: MOPaged[MOClassReturn | UUIDObject] = Field(
        description="Paged listing of classes"
    )


async def facet_user_key_to_uuid(user_key: str) -> UUID | None:
    """Find the UUID of a facet using its user_key.

    Args:
        user_key: The user_key to query.

    Returns:
        UUID of the facet if found.
    """
    query = """
    query FacetQuery {
      facets {
        objects {
          current {
            uuid
            user_key
          }
        }
      }
    }
    """
    response = await execute_graphql(query)
    handle_gql_error(response)
    facets = [x["current"] for x in response.data["facets"]["objects"]]
    if not facets:  # pragma: no cover
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
    facet: str | UUID = Path(..., description="UUID or user_key of a facet."),
    start: int = Query(0, description="Index of the first item for paging."),
    limit: int | None = Query(None, description="Maximum number of items to return."),
    only_primary_uuid: bool | None = Query(
        None, description="Only retrieve the UUID of the class unit."
    ),
):
    """List classes available in the given facet."""
    # If given a user_key we want to convert it to an UUID
    try:
        facet_uuid = UUID(facet)
    except ValueError:
        facet_uuid = await facet_user_key_to_uuid(facet)
        if facet_uuid is None:  # pragma: no cover
            exceptions.ErrorCodes.E_NOT_FOUND()

    query = """
    query FacetChildrenQuery(
      $uuid: UUID!,
      $only_primary_uuid: Boolean!
    ) {
      facets(filter: {uuids: [$uuid]}) {
        objects {
          current {
            uuid
            user_key
            description
            children: classes @include(if: $only_primary_uuid) {
              uuid
            }
            children: classes @skip(if: $only_primary_uuid) {
              uuid
              name
              user_key
              example
              scope
              owner
            }
          }
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
    facets = [x["current"] for x in response.data["facets"]["objects"]]
    if not facets:  # pragma: no cover
        exceptions.ErrorCodes.E_UNKNOWN()
    try:
        facet: dict[str, Any] = one(facets)
    except ValueError as err:  # pragma: no cover
        raise ValueError("Wrong number of facets returned, expected one.") from err
    children = facet.pop("children")

    total = len(children)
    if start:  # pragma: no cover
        children = children[start:]
    if limit:  # pragma: no cover
        children = children[:limit]

    facet["data"] = {
        "total": total,
        "offset": start,
        "items": children,
    }
    return facet


class MOAllClasses(MOFacetAllClasses):
    class Config:
        schema_extra = {
            "example": {
                "uuid": "598b261e-8bd4-4fa2-964a-7d9fa2f2713d",
                "user_key": "org_unit_type",
                "description": "",
                "path": "/o/3b866d97-0b1f-48e0-8078-686d96f430b3/f/org_unit_type/",
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

    path: str = Field(description="The location on the web server.")


@facet_router.get(
    "/o/{orgid}/f/{facet}/",
    response_model=MOAllClasses,
    response_model_exclude_unset=True,
    responses={404: {"description": "Facet not found."}},
)
async def get_classes(
    orgid: UUID = Path(
        ...,
        description="UUID of the organisation to retrieve facets from.",
        examples="3b866d97-0b1f-48e0-8078-686d96f430b3",
    ),
    facet: str | UUID = Path(..., description="UUID or user_key of a facet."),
    start: int = Query(0, description="Index of the first item for paging."),
    limit: int | None = Query(None, description="Maximum number of items to return."),
    only_primary_uuid: bool | None = Query(
        None, description="Only retrieve the UUID of the class unit."
    ),
    at: Any = None,
    validity: Any = None,
    full_name: bool | None = Query(None, description="Include full name in response."),
    top_level_facet: bool | None = Query(
        None, description="Include top-level facet in response."
    ),
    facet_toggle: bool | None = Query(
        None, alias="facet", description="Include facet in response."
    ),
):
    """List classes available in the given facet."""
    # If given a user_key we want to convert it to an UUID
    try:
        facet_uuid = UUID(facet)
    except ValueError:
        facet_uuid = await facet_user_key_to_uuid(facet)
        if facet_uuid is None:
            exceptions.ErrorCodes.E_NOT_FOUND()

    query = """
    query FacetChildrenQuery(
      $uuid: UUID!,
      $only_primary_uuid: Boolean!,
      $full_name: Boolean!,
      $top_level_facet: Boolean!,
      $facet: Boolean!,
    ) {
      facets(filter: {uuids: [$uuid]}) {
        objects {
          current {
            ...facet_fields
            children: classes @include(if: $only_primary_uuid) {
              uuid
            }
            children: classes @skip(if: $only_primary_uuid) {
              uuid
              name
              user_key
              example
              scope
              owner
              published

              full_name @include(if: $full_name)

              top_level_facet @include(if: $top_level_facet) {
                ...facet_fields
              }

              facet @include(if: $facet) {
                ...facet_fields
              }
            }
          }
        }
      }
    }
    fragment facet_fields on Facet {
      uuid
      user_key
      description
    }
    """
    response = await execute_graphql(
        query,
        {
            "uuid": str(facet_uuid),
            "only_primary_uuid": bool(only_primary_uuid),
            "full_name": bool(full_name),
            "top_level_facet": bool(top_level_facet),
            "facet": bool(facet_toggle),
        },
    )
    handle_gql_error(response)
    facets = [x["current"] for x in response.data["facets"]["objects"]]
    if not facets:  # pragma: no cover
        exceptions.ErrorCodes.E_NOT_FOUND()
    try:
        facet: dict[str, Any] = one(facets)
    except ValueError as err:  # pragma: no cover
        raise ValueError("Wrong number of facets returned, expected one.") from err
    children = facet.pop("children")

    total = len(children)
    if start:  # pragma: no cover
        children = children[start:]
    if limit:  # pragma: no cover
        children = children[:limit]

    facet["data"] = {
        "total": total,
        "offset": start,
        "items": children,
    }
    facet["path"] = facet_router.url_path_for(
        "get_classes", orgid=orgid, facet=facet["user_key"]
    )
    return facet
