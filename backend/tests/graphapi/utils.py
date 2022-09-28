# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Pytest helper functions for GraphAPI tests."""
from collections.abc import Callable
from datetime import datetime
from operator import itemgetter
from uuid import UUID

from more_itertools import one

from tests.conftest import GQLResponse


def fetch_org_unit_validity(
    graphapi_post: Callable, org_uuid: UUID
) -> tuple[datetime, datetime | None]:
    validity_query = """
        query FetchValidity($uuid: UUID!) {
            org_units(uuids: [$uuid]) {
                objects {
                    uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(validity_query, {"uuid": str(org_uuid)})
    assert response.errors is None
    validity = one(one(response.data["org_units"])["objects"])["validity"]
    from_time = datetime.fromisoformat(validity["from"]).replace(tzinfo=None)
    to_time = (
        datetime.fromisoformat(validity["to"]).replace(tzinfo=None)
        if validity["to"]
        else None
    )
    return from_time, to_time


def fetch_employee_validity(
    graphapi_post: Callable, employee_uuid: UUID
) -> tuple[datetime, datetime | None]:
    validity_query = """
        query FetchValidity($uuid: UUID!) {
            employees(uuids: [$uuid]) {
                objects {
                    uuid
                    validity {
                        from
                        to
                    }
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(validity_query, {"uuid": str(employee_uuid)})
    assert response.errors is None
    validity = one(one(response.data["employees"])["objects"])["validity"]
    from_time = datetime.fromisoformat(validity["from"]).replace(tzinfo=None)
    to_time = (
        datetime.fromisoformat(validity["to"]).replace(tzinfo=None)
        if validity["to"]
        else None
    )
    return from_time, to_time


def fetch_class_uuids(graphapi_post: Callable, facet_name: str) -> list[UUID]:
    class_query = """
        query FetchClassUUIDs($user_key: String!) {
            facets(user_keys: [$user_key]) {
                classes {
                    uuid
                }
            }
        }
    """
    response: GQLResponse = graphapi_post(class_query, {"user_key": facet_name})
    assert response.errors is None
    facet = one(response.data["facets"])
    class_uuids = list(map(UUID, map(itemgetter("uuid"), facet["classes"])))
    return class_uuids
