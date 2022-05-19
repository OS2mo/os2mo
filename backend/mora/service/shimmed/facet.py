#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Any
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
    except ValueError:
        raise ValueError("Wrong number of classes returned, expected one.")
    return clazz
