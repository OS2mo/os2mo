# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from mora.mapping import ADMIN
from tests.conftest import BRUCE_UUID
from tests.conftest import SetAuth

METRIC_NAME = "os2mo_max_daily_registrations_single_org_func"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_max_daily_registrations_no_registrations(
    fetch_metrics: Callable[[], str],
) -> None:
    """The metric reports zero when nothing was registered within the last day.

    There is no actor to attribute the zero to, so the label is empty. The
    dataseries goes to zero rather than disappearing.
    """
    metrics = fetch_metrics()
    assert f'{METRIC_NAME}{{actor=""}} 0.0' in metrics


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_max_daily_registrations(
    fetch_metrics: Callable[[], str],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
) -> None:
    """The metric reports the org func with the most registrations the last day.

    Every write creates a new registration, so updating an engagement twice
    leaves it with three registrations in total: one from the create and one
    per update.
    """
    person = create_person()
    org_unit = create_org_unit("unit")

    busy = create_engagement(
        {
            "user_key": "busy",
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2024-01-01", "to": None},
        }
    )
    for to_date in ("2024-06-30", "2024-12-31"):
        update_engagement(
            {
                "uuid": str(busy),
                "validity": {"from": "2024-01-01", "to": to_date},
            }
        )

    # A less frequently edited engagement, which must not win over `busy`.
    quiet = create_engagement(
        {
            "user_key": "quiet",
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2024-01-01", "to": None},
        }
    )
    update_engagement(
        {
            "uuid": str(quiet),
            "validity": {"from": "2024-01-01", "to": "2024-06-30"},
        }
    )

    metrics = fetch_metrics()

    # Three registrations on `busy`, not the two on `quiet` and not the five
    # made in total.
    assert f'{METRIC_NAME}{{actor="{BRUCE_UUID}"}} 3.0' in metrics
    assert f'{METRIC_NAME}{{actor=""}}' not in metrics


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_max_daily_registrations_switches_actor(
    fetch_metrics: Callable[[], str],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    update_engagement: Callable[[dict[str, Any]], UUID],
    set_auth: SetAuth,
) -> None:
    """The previous actor is dropped once another actor overtakes them.

    The gauge is cleared on every scrape, so it never keeps a label for an
    actor who no longer holds the maximum.
    """
    person = create_person()
    org_unit = create_org_unit("unit")

    alice = uuid4()
    bob = uuid4()

    set_auth(ADMIN, alice)
    alice_engagement = create_engagement(
        {
            "user_key": "alice",
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2024-01-01", "to": None},
        }
    )
    update_engagement(
        {
            "uuid": str(alice_engagement),
            "validity": {"from": "2024-01-01", "to": "2024-06-30"},
        }
    )

    metrics = fetch_metrics()
    assert f'{METRIC_NAME}{{actor="{alice}"}} 2.0' in metrics

    set_auth(ADMIN, bob)
    bob_engagement = create_engagement(
        {
            "user_key": "bob",
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2024-01-01", "to": None},
        }
    )
    for to_date in ("2024-06-30", "2024-09-30", "2024-12-31"):
        update_engagement(
            {
                "uuid": str(bob_engagement),
                "validity": {"from": "2024-01-01", "to": to_date},
            }
        )

    metrics = fetch_metrics()
    assert f'{METRIC_NAME}{{actor="{bob}"}} 4.0' in metrics
    assert f'actor="{alice}"' not in metrics
