# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID

import pytest
from strawberry import UNSET
from strawberry.types.unset import UnsetType


@pytest.fixture
def create_title(
    title_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID],
) -> Callable[[str], UUID]:
    """Create a class in the `title` facet."""

    def inner(user_key: str) -> UUID:
        return create_class(
            {
                "facet_uuid": str(title_facet),
                "user_key": user_key,
                "name": user_key,
                "validity": {"from": "1970-01-01"},
            }
        )

    return inner


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
@pytest.mark.parametrize(
    "initial_title, update, expect_title",
    [
        (None, None, None),
        (None, UNSET, None),
        (None, "new", "new"),
        (UNSET, None, None),
        (UNSET, UNSET, None),
        (UNSET, "new", "new"),
        ("initial", None, None),
        ("initial", UNSET, "initial"),
        ("initial", "new", "new"),
    ],
)
def test_update_engagement_title(
    create_org_unit: Callable[..., UUID],
    create_person: Callable[..., UUID],
    create_manager: Callable[..., UUID],
    create_title: Callable[[str], UUID],
    ansat: UUID,
    jurist: UUID,
    primary_class: UUID,
    create_engagement: Callable[[dict[str, Any]], UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    read_engagement: Callable[[UUID], dict[str, Any]],
    initial_title: str | UnsetType | None,
    update: str | UnsetType | None,
    expect_title: str | None,
) -> None:
    """Updating the title changes the title and nothing else."""
    # Arrange
    org_unit = create_org_unit("root")
    person = create_person()
    titles = {
        "initial": create_title("Software developer"),
        "new": create_title("Software architect"),
    }

    engagement_data: dict[str, Any] = {
        "user_key": "12345",
        "org_unit": str(org_unit),
        "person": str(person),
        "engagement_type": str(ansat),
        "job_function": str(jurist),
        "primary": str(primary_class),
        "explicit_manager": str(create_manager(org_unit, person)),
        "extension_1": "foo",
        "fraction": 500,
        "validity": {"from": "2020-01-01", "to": None},
    }
    if initial_title is not UNSET:
        engagement_data["title"] = str(titles[initial_title]) if initial_title else None
    engagement_uuid = create_engagement(engagement_data)

    before = read_engagement(engagement_uuid)
    expected = {"uuid": str(titles[initial_title])} if initial_title else None
    assert before["title"] == expected

    # Act
    update_input: dict[str, Any] = {
        "uuid": str(engagement_uuid),
        "validity": {"from": "2020-01-01", "to": None},
    }
    if update is not UNSET:
        update_input["title"] = str(titles[update]) if update else None
    update_engagement(update_input)

    # Assert
    expected = {"uuid": str(titles[expect_title])} if expect_title else None
    assert read_engagement(engagement_uuid) == {**before, "title": expected}
