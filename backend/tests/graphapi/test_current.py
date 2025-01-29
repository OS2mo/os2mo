# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

import freezegun
import pytest

uuid = "2874e1dc-85e6-4269-823a-e1125484dfd3"


def setup_data(graphapi_post: Any) -> None:
    mutation = """
        mutation UpdateOrgUnit($input: OrganisationUnitUpdateInput!) {
            org_unit_update(input: $input) {
                uuid
            }
        }
    """
    changes = [
        ("1970-01-01", "Unix"),
        ("2000-01-01", "Millennium"),
        ("2020-01-01", "MMXX"),
    ]
    for from_date, name in changes:
        response = graphapi_post(
            mutation,
            {"input": {"uuid": uuid, "validity": {"from": from_date}, "name": name}},
        )
        assert response.errors is None
        assert response.data == {"org_unit_update": {"uuid": uuid}}

    response = graphapi_post(
        """
            query ReadHistory($uuid: UUID!) {
              org_units(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                  objects {
                    name
                    validity {
                      from
                      to
                    }
                  }
                }
              }
            }
        """,
        {"uuid": uuid},
    )
    assert response.errors is None
    assert response.data == {
        "org_units": {
            "objects": [
                {
                    "objects": [
                        {
                            "name": "Unix",
                            "validity": {
                                "from": "1970-01-01T00:00:00+01:00",
                                "to": "1999-12-31T00:00:00+01:00",
                            },
                        },
                        {
                            "name": "Millennium",
                            "validity": {
                                "from": "2000-01-01T00:00:00+01:00",
                                "to": "2019-12-31T00:00:00+01:00",
                            },
                        },
                        {
                            "name": "MMXX",
                            "validity": {
                                "from": "2020-01-01T00:00:00+01:00",
                                "to": None,
                            },
                        },
                    ]
                }
            ]
        }
    }


def current_response(expected):
    return [
        {
            "uuid": uuid,
            "current": {
                "name": expected,
            }
            if expected
            else None,
        }
    ]


@pytest.mark.integration_test
@pytest.mark.usefixtures("fixture_db")
@pytest.mark.parametrize(
    "query_time,from_date,to_date,expected",
    [
        # Full history in objects
        # current is set as expected
        ("1930-01-01", None, None, current_response(None)),
        ("1972-01-01", None, None, current_response("Unix")),
        ("1998-01-01", None, None, current_response("Unix")),
        ("2002-01-01", None, None, current_response("Millennium")),
        ("2011-01-01", None, None, current_response("Millennium")),
        ("2023-01-01", None, None, current_response("MMXX")),
        ("3000-01-01", None, None, current_response("MMXX")),
        # Relevant history in objects
        # current is set as expected
        ("1930-01-01", "1929-01-01", "1931-01-01", []),
        ("1972-01-01", "1971-01-01", "1973-01-01", current_response("Unix")),
        ("1998-01-01", "1997-01-01", "1999-01-01", current_response("Unix")),
        ("2002-01-01", "2001-01-01", "2003-01-01", current_response("Millennium")),
        ("2011-01-01", "2010-01-01", "2012-01-01", current_response("Millennium")),
        ("2023-01-01", "2022-01-01", "2024-01-01", current_response("MMXX")),
        ("3000-01-01", "2999-01-01", "3001-01-01", current_response("MMXX")),
        # Limited history just after y2k in objects
        # current only available within the history (for now)
        ("1930-01-01", "2001-01-01", "2003-01-01", current_response(None)),
        ("1972-01-01", "2001-01-01", "2003-01-01", current_response(None)),
        ("1998-01-01", "2001-01-01", "2003-01-01", current_response(None)),
        ("2002-01-01", "2001-01-01", "2003-01-01", current_response("Millennium")),
        ("2011-01-01", "2001-01-01", "2003-01-01", current_response("Millennium")),
        ("2023-01-01", "2001-01-01", "2003-01-01", current_response(None)),
        ("3000-01-01", "2001-01-01", "2003-01-01", current_response(None)),
        # No history in objects
        # current not available as objects aren't available at all
        ("1930-01-01", "1930-01-01", "1931-01-01", []),
        ("1972-01-01", "1930-01-01", "1931-01-01", []),
        ("1998-01-01", "1930-01-01", "1931-01-01", []),
        ("2002-01-01", "1930-01-01", "1931-01-01", []),
        ("2011-01-01", "1930-01-01", "1931-01-01", []),
        ("2023-01-01", "1930-01-01", "1931-01-01", []),
        ("3000-01-01", "1930-01-01", "1931-01-01", []),
    ],
)
def test_read_current(
    graphapi_post: Any,
    from_date: str,
    to_date: str,
    query_time: str,
    expected: str | None,
) -> None:
    """Integrationtest for reading current."""
    setup_data(graphapi_post)

    with freezegun.freeze_time(query_time):
        response = graphapi_post(
            """
                query ReadCurrent(
                    $uuid: UUID!, $from_date: DateTime, $to_date: DateTime
                ) {
                  org_units(filter: {uuids: [$uuid], from_date: $from_date, to_date: $to_date}) {
                    objects {
                      uuid
                      current {
                          name
                      }
                    }
                  }
                }
            """,
            {"uuid": uuid, "from_date": from_date, "to_date": to_date},
        )
        assert response.errors is None
        assert response.data == {"org_units": {"objects": expected}}
