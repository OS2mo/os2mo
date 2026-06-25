# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ..conftest import GraphAPIPost


def _engagements_for_org_unit(
    graphapi_post: GraphAPIPost, unit: UUID, window: tuple[str, str]
) -> set[UUID]:
    query = """
        query Engagements($filter: EngagementFilter!) {
            engagements(filter: $filter) {
                objects { uuid }
            }
        }
    """
    response = graphapi_post(
        query,
        variables={
            "filter": {
                "org_unit": {"uuids": [str(unit)]},
                "from_date": window[0],
                "to_date": window[1],
            }
        },
    )
    assert response.errors is None
    assert response.data is not None
    return {UUID(o["uuid"]) for o in response.data["engagements"]["objects"]}


@pytest.mark.integration_test
async def test_engagement_org_unit_filter_respects_gyldighed(
    empty_db: AsyncSession,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    """Filtering engagements by org_unit must not match a unit the engagement
    is only attached to while Inaktiv.

    Regression test for #70660: the gyldighed=Aktiv check and the org-unit
    relation check were previously evaluated independently against the filter
    window, so an engagement could match a unit it was only attached to while
    Inaktiv, as long as it was Aktiv at some other point in the window.

    We reproduce the misaligned shape through the GraphQL API: an engagement is
    created in unit_a, moved to unit_b, and then terminated *before* the move,
    leaving the unit_b relation entirely within the Inaktiv period::

        gyldighed:  Aktiv [2020, 2021)   Inaktiv [2021, ...)
        org_unit:   unit_a [2020, 2023)  unit_b  [2023, ...)
    """
    person = create_person()
    unit_a = create_org_unit("unit-a")
    unit_b = create_org_unit("unit-b")

    engagement = create_engagement(
        {
            "person": str(person),
            "org_unit": str(unit_a),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2020-01-01T00:00:00+01:00", "to": None},
        }
    )
    # Move to unit_b from 2023. Terminating afterwards would re-activate the
    # engagement from the move date, so the move must happen first.
    move = graphapi_post(
        """
        mutation MoveEngagement($input: EngagementUpdateInput!) {
            engagement_update(input: $input) { uuid }
        }
        """,
        variables={
            "input": {
                "uuid": str(engagement),
                "org_unit": str(unit_b),
                "validity": {"from": "2023-01-01T00:00:00+01:00"},
            }
        },
    )
    assert move.errors is None
    # Terminate in 2021, well before the move: unit_b is now only ever attached
    # while the engagement is Inaktiv.
    terminate = graphapi_post(
        """
        mutation TerminateEngagement($input: EngagementTerminateInput!) {
            engagement_terminate(input: $input) { uuid }
        }
        """,
        variables={
            "input": {"uuid": str(engagement), "to": "2021-01-01T00:00:00+01:00"}
        },
    )
    assert terminate.errors is None

    window = ("2020-01-01T00:00:00+01:00", "2025-01-01T00:00:00+01:00")
    # Aktiv while attached to unit_a -> found.
    assert _engagements_for_org_unit(graphapi_post, unit_a, window) == {engagement}
    # Only attached to unit_b while Inaktiv -> not found.
    assert _engagements_for_org_unit(graphapi_post, unit_b, window) == set()


@pytest.mark.integration_test
async def test_engagement_org_unit_filter_disjoint_active_periods(
    empty_db: AsyncSession,
    create_org_unit: Callable[[str, UUID | None], UUID],
    create_person: Callable[[dict[str, Any] | None], UUID],
    create_engagement: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    """An org_unit attached only during the inactive *gap* between two active
    periods must not match, even though the gap is inside the filter window.

    Guards the multirange semantics of the active-period set: it is stored as a
    true ``tstzmultirange`` (a disjoint union), not a single merged ``[min,
    max)`` range. A merged range would wrongly swallow the inactive gap and
    match ``unit_gap``::

        gyldighed:  Aktiv [2020, 2021)   Inaktiv [2021, 2023)   Aktiv [2023, ...)
        org_unit:   unit_a [2020, 2021)  unit_gap [2021, 2023)  unit_c [2023, ...)
    """

    def move(unit: UUID, frm: str) -> None:
        response = graphapi_post(
            """
            mutation MoveEngagement($input: EngagementUpdateInput!) {
                engagement_update(input: $input) { uuid }
            }
            """,
            variables={
                "input": {
                    "uuid": str(engagement),
                    "org_unit": str(unit),
                    "validity": {"from": frm},
                }
            },
        )
        assert response.errors is None

    person = create_person()
    unit_a = create_org_unit("unit-a")
    unit_gap = create_org_unit("unit-gap")
    unit_c = create_org_unit("unit-c")

    engagement = create_engagement(
        {
            "person": str(person),
            "org_unit": str(unit_a),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2020-01-01T00:00:00+01:00", "to": None},
        }
    )
    # Build the org_unit timeline first (while still Aktiv everywhere):
    # unit_a [2020, 2021), unit_gap [2021, 2023), unit_c [2023, ...).
    move(unit_gap, "2021-01-01T00:00:00+01:00")
    move(unit_c, "2023-01-01T00:00:00+01:00")
    # Carve the gyldighed into two disjoint active periods: terminate at 2021,
    # then re-activate from 2023 by editing that period.
    terminate = graphapi_post(
        """
        mutation TerminateEngagement($input: EngagementTerminateInput!) {
            engagement_terminate(input: $input) { uuid }
        }
        """,
        variables={
            "input": {"uuid": str(engagement), "to": "2021-01-01T00:00:00+01:00"}
        },
    )
    assert terminate.errors is None
    move(unit_c, "2023-01-01T00:00:00+01:00")

    window = ("2019-01-01T00:00:00+01:00", "2025-01-01T00:00:00+01:00")
    # Attached to unit_a / unit_c while Aktiv -> found.
    assert _engagements_for_org_unit(graphapi_post, unit_a, window) == {engagement}
    assert _engagements_for_org_unit(graphapi_post, unit_c, window) == {engagement}
    # Attached to unit_gap only during the inactive gap -> not found.
    assert _engagements_for_org_unit(graphapi_post, unit_gap, window) == set()
