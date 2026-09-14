# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from more_itertools import one

from ..conftest import GraphAPIPost


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    ("filter", "expected"),
    [
        # No filter: all three returned.
        ({}, {"eng_primary", "eng_non_primary", "eng_unset"}),
        # `primary: null` selects engagements without a primary class set.
        ({"primary": None}, {"eng_unset"}),
        # `primary: {}` selects engagements with any primary class set.
        ({"primary": {}}, {"eng_primary", "eng_non_primary"}),
        # Filter by primary class user_key.
        ({"primary": {"user_keys": ["primary"]}}, {"eng_primary"}),
        # Filter by non-primary class user_key.
        ({"primary": {"user_keys": ["non-primary"]}}, {"eng_non_primary"}),
        # Filter by both class user_keys.
        (
            {"primary": {"user_keys": ["primary", "non-primary"]}},
            {"eng_primary", "eng_non_primary"},
        ),
        # Filter by a non-existent class yields nothing.
        ({"primary": {"user_keys": ["nonexistent"]}}, set()),
    ],
)
def test_engagement_primary_filter(
    graphapi_post: GraphAPIPost,
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    person: UUID,
    primary_class: UUID,
    non_primary_class: UUID,
    filter: dict[str, Any],
    expected: set[str],
) -> None:
    """Test that engagements can be filtered by primary class."""
    org_unit = create_org_unit("ou")

    for user_key, primary in [
        ("eng_primary", primary_class),
        ("eng_non_primary", non_primary_class),
        ("eng_unset", None),
    ]:
        create_engagement(
            {
                "user_key": user_key,
                "engagement_type": str(uuid4()),
                "job_function": str(uuid4()),
                "org_unit": str(org_unit),
                "person": str(person),
                "primary": str(primary) if primary is not None else None,
                "validity": {"from": "2024-01-01"},
            }
        )

    response = graphapi_post(
        """
        query ReadEngagements($filter: EngagementFilter) {
            engagements(filter: $filter) {
                objects {
                    current {
                        user_key
                    }
                }
            }
        }
        """,
        {"filter": filter},
    )
    assert response.errors is None
    assert response.data
    assert {
        obj["current"]["user_key"]
        for obj in response.data["engagements"]["objects"]
        if obj["current"] is not None
    } == expected


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_engagement_primary_survives_validity_extension(
    graphapi_post: GraphAPIPost,
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_org_unit: Callable[..., UUID],
    person: UUID,
    primary_class: UUID,
) -> None:
    """An edit that only touches validity must not drop the primary relation."""
    org_unit = create_org_unit("ou")
    engagement_uuid = create_engagement(
        {
            "user_key": "eng_primary",
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "org_unit": str(org_unit),
            "person": str(person),
            "primary": str(primary_class),
            "validity": {"from": "2024-01-01", "to": "2024-12-31"},
        }
    )

    # Extend validity without touching primary.
    update_response = graphapi_post(
        """
        mutation UpdateEngagement($input: EngagementUpdateInput!) {
            engagement_update(input: $input) {
                uuid
            }
        }
        """,
        {
            "input": {
                "uuid": str(engagement_uuid),
                "validity": {"from": "2024-01-01", "to": "2025-12-31"},
            }
        },
    )
    assert update_response.errors is None

    read_response = graphapi_post(
        """
        query Read($uuid: UUID!) {
            engagements(filter: {uuids: [$uuid], from_date: null, to_date: null}) {
                objects {
                    validities {
                        primary_uuid
                        validity {from to}
                    }
                }
            }
        }
        """,
        {"uuid": str(engagement_uuid)},
    )
    assert read_response.errors is None
    assert read_response.data
    validities = one(read_response.data["engagements"]["objects"])["validities"]
    validity = one(validities)
    assert validity == {
        "primary_uuid": str(primary_class),
        "validity": {
            "from": "2024-01-01T00:00:00+01:00",
            "to": "2025-12-31T00:00:00+01:00",
        },
    }
