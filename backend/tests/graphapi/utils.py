# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pytest helper functions for GraphAPI tests."""
from datetime import datetime
from operator import itemgetter
from uuid import UUID

from more_itertools import one

from tests.conftest import GraphAPIPost


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
