# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pytest helper functions for GraphAPI tests."""

from datetime import datetime
from functools import partial
from operator import itemgetter
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from more_itertools import one
from strawberry import UNSET
from strawberry.types.unset import UnsetType

from tests.conftest import GraphAPIPost

# jsonable encoder that coerces UNSET to None.
# Useful in the transition period while introducing PATCH writes to GraphQL
sjsonable_encoder = partial(
    jsonable_encoder, custom_encoder={UnsetType: lambda _: None}
)


def fetch_org_unit_validity(
    graphapi_post: GraphAPIPost, org_uuid: UUID
) -> tuple[datetime, datetime | None]:
    validity_query = """
        query FetchValidity($uuid: UUID!) {
            org_units(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(validity_query, {"uuid": str(org_uuid)})
    assert response.errors is None
    validity = one(one(response.data["org_units"]["objects"])["objects"])["validity"]
    from_time = datetime.fromisoformat(validity["from"]).replace(tzinfo=None)
    to_time = (
        datetime.fromisoformat(validity["to"]).replace(tzinfo=None)
        if validity["to"]
        else None
    )
    return from_time, to_time


def fetch_employee_validity(
    graphapi_post: GraphAPIPost, employee_uuid: UUID
) -> tuple[datetime, datetime | None]:
    validity_query = """
        query FetchValidity($uuid: UUID!) {
            employees(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(validity_query, {"uuid": str(employee_uuid)})
    assert response.errors is None
    validity = one(one(response.data["employees"]["objects"])["objects"])["validity"]
    from_time = datetime.fromisoformat(validity["from"]).replace(tzinfo=None)
    to_time = (
        datetime.fromisoformat(validity["to"]).replace(tzinfo=None)
        if validity["to"]
        else None
    )
    return from_time, to_time


def fetch_engagement_validity(
    graphapi_post: GraphAPIPost, engagement_uuid: UUID
) -> tuple[datetime, datetime | None]:
    validity_query = """
        query FetchValidity($uuid: UUID!) {
            engagements(filter: {uuids: [$uuid]}) {
                objects {
                    objects {
                        uuid
                        validity {
                            from
                            to
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(validity_query, {"uuid": str(engagement_uuid)})
    assert response.errors is None
    validity = one(one(response.data["engagements"]["objects"])["objects"])["validity"]
    from_time = datetime.fromisoformat(validity["from"]).replace(tzinfo=None)
    to_time = (
        datetime.fromisoformat(validity["to"]).replace(tzinfo=None)
        if validity["to"]
        else None
    )
    return from_time, to_time


def fetch_class_uuids(graphapi_post: GraphAPIPost, facet_name: str) -> list[UUID]:
    class_query = """
        query FetchClassUUIDs($user_key: String!) {
            facets(filter: {user_keys: [$user_key]}) {
                objects {
                    current {
                        classes {
                            uuid
                        }
                    }
                }
            }
        }
    """
    response = graphapi_post(class_query, {"user_key": facet_name})
    assert response.errors is None
    facet = one(response.data["facets"]["objects"])["current"]
    class_uuids = list(map(UUID, map(itemgetter("uuid"), facet["classes"])))
    return class_uuids


def gen_read_parent(graphapi_post: GraphAPIPost, url: str, uuid: UUID) -> UUID | None:
    read_query = """
    query ReadOrgUnitParent($uuid: UUID!) {
      org_units(filter: {uuids: [$uuid]}) {
        objects {
          current {
            parent {
                uuid
            }
          }
        }
      }
    }
    """
    response = graphapi_post(query=read_query, variables={"uuid": str(uuid)}, url=url)
    assert response.errors is None
    assert response.data is not None
    parent = one(response.data["org_units"]["objects"])["current"]["parent"]
    if parent is None:
        # NOTE: parent_uuid will be set to the root org when this happens
        return None
    return UUID(parent["uuid"])


def gen_set_parent(
    graphapi_post: GraphAPIPost,
    url: str,
    uuid: UUID,
    parent_uuid: UUID | UnsetType | None,
) -> None:
    write_query = """
    mutation MyMutation($input: OrganisationUnitUpdateInput!) {
      org_unit_update(input: $input) {
        uuid
      }
    }
    """
    payload = {"uuid": str(uuid), "validity": {"from": "2020-01-01"}}
    if parent_uuid is not UNSET:
        payload["parent"] = str(parent_uuid) if parent_uuid else None
    response = graphapi_post(query=write_query, variables={"input": payload}, url=url)
    assert response.errors is None
    assert response.data is not None
    assert UUID(response.data["org_unit_update"]["uuid"]) == uuid
