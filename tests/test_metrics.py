# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy import text

from tests.conftest import AnotherTransaction

# Prometheus counters are exposed with a `_total` suffix.
METRIC_NAME = "os2mo_registration_count_total"


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_registrations_org_func_no_registrations(
    fetch_metrics: Callable[[], str],
) -> None:
    """No organisation functions means no registrations to report."""
    metrics = fetch_metrics()
    assert f"{METRIC_NAME}{{" not in metrics


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
def test_registrations_org_func(
    fetch_metrics: Callable[[], str],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    create_itsystem: Callable[[dict[str, Any]], UUID],
    create_ituser: Callable[[dict[str, Any]], UUID],
) -> None:
    """Registrations are counted per org func type, under their english name.

    The count is recomputed on every scrape rather than accumulated, so
    scraping repeatedly does not inflate it.
    """
    person = create_person()
    org_unit = create_org_unit("unit")

    create_engagement(
        {
            "user_key": "engagement",
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2024-01-01", "to": None},
        }
    )
    itsystem = create_itsystem(
        {
            "user_key": "suila",
            "name": "Suila-tapit",
            "validity": {"from": "2024-01-01"},
        }
    )
    create_ituser(
        {
            "user_key": "ituser",
            "itsystem": str(itsystem),
            "person": str(person),
            "validity": {"from": "2024-01-01"},
        }
    )

    metrics = fetch_metrics()
    assert f'{METRIC_NAME}{{type="engagement"}} 1.0' in metrics
    assert f'{METRIC_NAME}{{type="ituser"}} 1.0' in metrics

    # A second engagement, leaving the ituser count untouched.
    create_engagement(
        {
            "user_key": "engagement2",
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2024-01-01", "to": None},
        }
    )

    metrics = fetch_metrics()
    assert f'{METRIC_NAME}{{type="engagement"}} 2.0' in metrics
    assert f'{METRIC_NAME}{{type="ituser"}} 1.0' in metrics


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_registrations_org_func_unknown_funktionsnavn(
    fetch_metrics: Callable[[], str],
    create_org_unit: Callable[..., UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    another_transaction: AnotherTransaction,
) -> None:
    """A funktionsnavn outside the enum is reported rather than breaking /metrics.

    Older databases hold funktionsnavne that are no longer part of
    `mora.db.FunktionsNavn`, e.g. "Rolle". Reading one must neither fail the
    scrape nor drop the registration.
    """
    person = create_person()
    org_unit = create_org_unit("unit")
    create_engagement(
        {
            "user_key": "engagement",
            "person": str(person),
            "org_unit": str(org_unit),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2024-01-01", "to": None},
        }
    )

    async with another_transaction() as (_, session):
        await session.execute(
            text(
                "update organisationfunktion_attr_egenskaber "
                "set funktionsnavn = 'Rolle'"
            )
        )

    metrics = fetch_metrics()
    assert f'{METRIC_NAME}{{type="Rolle"}} 1.0' in metrics
