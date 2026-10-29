# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "initial_fraction, update, expected_fraction",
    [
        # Set on an engagement without a fraction
        (None, {"fraction": 500}, 500),
        # Overwrite an existing fraction
        (500, {"fraction": 1000}, 1000),
        # Omitting the field leaves the existing value untouched (PATCH)
        (500, {}, 500),
        # Explicit null clears the fraction
        (500, {"fraction": None}, None),
        (None, {"fraction": None}, None),
    ],
)
def test_engagement_fraction(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    read_engagement: Callable[[UUID], dict[str, Any]],
    initial_fraction: int | None,
    update: dict[str, Any],
    expected_fraction: int | None,
) -> None:
    """Updating the fraction changes the fraction and nothing else."""
    # Arrange
    org_unit = create_org_unit("root")
    person = create_person()
    engagement_data: dict[str, Any] = {
        "user_key": "12345",
        "org_unit": str(org_unit),
        "person": str(person),
        "engagement_type": str(uuid4()),
        "job_function": str(uuid4()),
        "primary": str(uuid4()),
        "explicit_manager": str(create_manager(org_unit, person)),
        "extension_1": "foo",
        "extension_2": "bar",
        "fraction": initial_fraction,
        "validity": {"from": "2020-01-01", "to": None},
    }
    engagement_uuid = create_engagement(engagement_data)
    before = read_engagement(engagement_uuid)
    assert before["fraction"] == initial_fraction

    # Act
    update_engagement(
        {
            "uuid": str(engagement_uuid),
            "validity": {"from": "2020-01-01", "to": None},
            **update,
        }
    )

    # Assert
    assert read_engagement(engagement_uuid) == {
        **before,
        "fraction": expected_fraction,
    }
