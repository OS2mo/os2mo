# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Any
from uuid import UUID

import pytest
from more_itertools import one
from strawberry import UNSET
from strawberry.types.unset import UnsetType

from ..conftest import GraphAPIPost


def gentime(date: str) -> str:
    return f"{date}T00:00:00+01:00"


@pytest.fixture
def validity_employee_uuid(graphapi_post: GraphAPIPost) -> UUID:
    # Setup our data
    create_mutation = """
        mutation EmployeeCreate($input: EmployeeCreateInput!) {
          employee_create(input: $input) {
            uuid
          }
        }
    """
    update_mutation = """
        mutation EmployeeUpdate($input:EmployeeUpdateInput!) {
          employee_update(input: $input) {
            uuid
          }
        }
    """
    # This will be active from -infinity to infinity
    payload = {"given_name": "Startasia", "surname": "Ravenoak"}
    response = graphapi_post(create_mutation, {"input": payload})
    assert response.errors is None
    assert response.data is not None
    uuid = response.data["employee_create"]["uuid"]

    # This will be active from -infinity to 2020-01-01
    payload = {
        "uuid": uuid,
        "validity": {"from": "2000-01-01", "to": "2020-01-01"},
        "given_name": "Middleton",
    }
    response = graphapi_post(update_mutation, {"input": payload})
    assert response.errors is None
    assert response.data is not None
    assert response.data["employee_update"]["uuid"] == uuid

    # This will be active from 2020-01-01 to infinity
    payload = {
        "uuid": uuid,
        "validity": {"from": "2020-01-01"},
        "given_name": "Lastarza",
    }
    response = graphapi_post(update_mutation, {"input": payload})
    assert response.errors is None
    assert response.data is not None
    assert response.data["employee_update"]["uuid"] == uuid

    return UUID(uuid)


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "start,end,expected",
    [
        # Combinations of UNSET and None
        (
            UNSET,
            UNSET,
            [
                {
                    "given_name": "Lastarza",
                    "validity": {"from": gentime("2020-01-01"), "to": None},
                }
            ],
        ),
        (None, UNSET, "Cannot infer UNSET to_date from interval starting at -infinity"),
        (
            UNSET,
            None,
            [
                {
                    "given_name": "Lastarza",
                    "validity": {"from": gentime("2020-01-01"), "to": None},
                },
            ],
        ),
        (
            None,
            None,
            [
                {
                    "given_name": "Startasia",
                    "validity": {"from": None, "to": gentime("2000-01-01")},
                },
                {
                    "given_name": "Middleton",
                    "validity": {
                        "from": gentime("2000-01-01"),
                        "to": gentime("2020-01-01"),
                    },
                },
                {
                    "given_name": "Lastarza",
                    "validity": {"from": gentime("2020-01-01"), "to": None},
                },
            ],
        ),
        # Combinations of UNSET and dates
        (
            UNSET,
            "2010-01-01",
            "must be less than or equal to to_date 2010-01-01 00:00:00+01:00",
        ),
        (
            None,
            "2010-01-01",
            [
                {
                    "given_name": "Startasia",
                    "validity": {"from": None, "to": gentime("2000-01-01")},
                },
                {
                    "given_name": "Middleton",
                    "validity": {
                        "from": gentime("2000-01-01"),
                        "to": gentime("2020-01-01"),
                    },
                },
            ],
        ),
        (
            "2010-01-01",
            UNSET,
            [
                {
                    "given_name": "Middleton",
                    "validity": {
                        "from": gentime("2000-01-01"),
                        "to": gentime("2020-01-01"),
                    },
                },
            ],
        ),
        (
            "2010-01-01",
            None,
            [
                {
                    "given_name": "Middleton",
                    "validity": {
                        "from": gentime("2000-01-01"),
                        "to": gentime("2020-01-01"),
                    },
                },
                {
                    "given_name": "Lastarza",
                    "validity": {
                        "from": gentime("2020-01-01"),
                        "to": None,
                    },
                },
            ],
        ),
        # Combinations of dates
        (
            "1920-01-01",
            "1921-01-01",
            [
                {
                    "given_name": "Startasia",
                    "validity": {"from": None, "to": gentime("2000-01-01")},
                }
            ],
        ),
        (
            "3920-01-01",
            "3921-01-01",
            [
                {
                    "given_name": "Lastarza",
                    "validity": {
                        "from": gentime("2020-01-01"),
                        "to": None,
                    },
                }
            ],
        ),
        (
            "2010-01-01",
            "2011-01-01",
            [
                {
                    "given_name": "Middleton",
                    "validity": {
                        "from": gentime("2000-01-01"),
                        "to": gentime("2020-01-01"),
                    },
                }
            ],
        ),
        (
            "1920-01-01",
            "3921-01-01",
            [
                {
                    "given_name": "Startasia",
                    "validity": {"from": None, "to": gentime("2000-01-01")},
                },
                {
                    "given_name": "Middleton",
                    "validity": {
                        "from": gentime("2000-01-01"),
                        "to": gentime("2020-01-01"),
                    },
                },
                {
                    "given_name": "Lastarza",
                    "validity": {"from": gentime("2020-01-01"), "to": None},
                },
            ],
        ),
    ],
)
async def test_validity_queries(
    graphapi_post: GraphAPIPost,
    validity_employee_uuid: UUID,
    start: datetime | UnsetType | None,
    end: datetime | UnsetType | None,
    expected: list[dict[str, Any]] | str,
) -> None:
    uuid = str(validity_employee_uuid)

    validities_query = """
    query ReadValidities($uuid: UUID!, $start: DateTime, $end: DateTime) {
      employees(filter: {uuids: [$uuid]}) {
        objects {
          validities(start: $start, end: $end) {
            validity {
              from
              to
            }
            given_name
          }
        }
      }
    }
    """
    payload: dict[str, Any] = {"uuid": uuid}
    if start is not UNSET:
        payload["start"] = start
    if end is not UNSET:
        payload["end"] = end

    response = graphapi_post(validities_query, payload)
    if isinstance(expected, str):
        assert response.errors is not None
        assert response.data is None
        message = one(response.errors)["message"]
        assert expected in message
    else:
        assert response.errors is None
        assert response.data is not None
        validities = one(response.data["employees"]["objects"])["validities"]
        assert validities == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "at,expected",
    [
        (
            UNSET,
            {
                "given_name": "Lastarza",
                "validity": {"from": gentime("2020-01-01"), "to": None},
            },
        ),
        (
            None,
            {
                "given_name": "Lastarza",
                "validity": {"from": gentime("2020-01-01"), "to": None},
            },
        ),
        (
            "1920-01-01",
            {
                "given_name": "Startasia",
                "validity": {"from": None, "to": gentime("2000-01-01")},
            },
        ),
        (
            "1995-01-01",
            {
                "given_name": "Startasia",
                "validity": {"from": None, "to": gentime("2000-01-01")},
            },
        ),
        (
            "2010-01-01",
            {
                "given_name": "Middleton",
                "validity": {
                    "from": gentime("2000-01-01"),
                    "to": gentime("2020-01-01"),
                },
            },
        ),
        (
            "2025-01-01",
            {
                "given_name": "Lastarza",
                "validity": {"from": gentime("2020-01-01"), "to": None},
            },
        ),
        (
            "3921-01-01",
            {
                "given_name": "Lastarza",
                "validity": {"from": gentime("2020-01-01"), "to": None},
            },
        ),
    ],
)
async def test_at_queries(
    graphapi_post: GraphAPIPost,
    validity_employee_uuid: UUID,
    at: datetime | UnsetType | None,
    expected: dict[str, Any] | str | None,
) -> None:
    uuid = str(validity_employee_uuid)

    current_query = """
    query ReadCurrent($uuid: UUID!, $at: DateTime) {
      employees(filter: {uuids: [$uuid]}) {
        objects {
          current(at: $at) {
            validity {
              from
              to
            }
            given_name
          }
        }
      }
    }
    """
    payload: dict[str, Any] = {"uuid": uuid}
    if at is not UNSET:
        payload["at"] = at

    response = graphapi_post(current_query, payload)
    if isinstance(expected, str):
        assert response.errors is not None
        assert response.data is None
        message = one(response.errors)["message"]
        assert expected in message
    else:
        assert response.errors is None
        assert response.data is not None
        current = one(response.data["employees"]["objects"])["current"]
        assert current == expected
