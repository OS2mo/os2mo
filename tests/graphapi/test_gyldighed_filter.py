# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Callable
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from ..conftest import GraphAPIPost


def _engagements_for_org_unit(graphapi_post: GraphAPIPost, unit: UUID) -> set[UUID]:
    response = graphapi_post(
        """
        query Engagements($filter: EngagementFilter!) {
            engagements(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        variables={
            "filter": {
                "org_unit": {"uuids": [str(unit)]},
                "from_date": None,
                "to_date": None,
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
    person = create_person()
    unit_a = create_org_unit("unit-a")
    unit_b = create_org_unit("unit-b")

    engagement = create_engagement(
        {
            "person": str(person),
            "org_unit": str(unit_a),
            "engagement_type": str(uuid4()),
            "job_function": str(uuid4()),
            "validity": {"from": "2000-01-01T00:00:00+01:00", "to": None},
        }
    )
    # Move to unit_b from 2020. Terminating afterwards would re-activate the
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
                "validity": {"from": "2020-01-01T00:00:00+01:00"},
            }
        },
    )
    assert move.errors is None
    # Terminate in 2010, well before the move, leaving the unit_b relation
    # entirely within the Inaktiv period:
    #     gyldighed:  Aktiv [2000, 2010)   Inaktiv [2010, ...)
    #     org_unit:   unit_a [2000, 2020)  unit_b  [2020, ...)
    terminate = graphapi_post(
        """
        mutation TerminateEngagement($input: EngagementTerminateInput!) {
            engagement_terminate(input: $input) { uuid }
        }
        """,
        variables={
            "input": {"uuid": str(engagement), "to": "2010-01-01T00:00:00+01:00"}
        },
    )
    assert terminate.errors is None

    # Aktiv while attached to unit_a -> found.
    assert _engagements_for_org_unit(graphapi_post, unit_a) == {engagement}
    # Only attached to unit_b while Inaktiv -> not found, even though the
    # engagement is Aktiv elsewhere in the window.
    assert _engagements_for_org_unit(graphapi_post, unit_b) == set()


@pytest.mark.integration_test
async def test_employee_owner_filter_respects_gyldighed(
    empty_db: AsyncSession,
    create_person: Callable[..., UUID],
    create_owner: Callable[[dict[str, Any]], UUID],
    graphapi_post: GraphAPIPost,
) -> None:
    person_owner = create_person()
    person_a = create_person()
    person_b = create_person()

    owner = create_owner(
        {
            "person": str(person_a),
            "owner": str(person_owner),
            "validity": {"from": "2000-01-01T00:00:00+01:00", "to": None},
        }
    )
    move = graphapi_post(
        """
        mutation MoveOwner($input: OwnerUpdateInput!) {
            owner_update(input: $input) { uuid }
        }
        """,
        variables={
            "input": {
                "uuid": str(owner),
                "person": str(person_b),
                "owner": str(person_owner),
                "validity": {"from": "2020-01-01T00:00:00+01:00"},
            }
        },
    )
    assert move.errors is None
    # Same misaligned shape as the engagement test, but through the *reverse*
    # owner lookup in the employee predicate: the ownership is moved from
    # person_a to person_b, and then terminated *before* the move, leaving the
    # person_b relation entirely within the Inaktiv period:
    #     gyldighed:  Aktiv [2000, 2010)    Inaktiv [2010, ...)
    #     person:     person_a [2000, 2020) person_b [2020, ...)
    terminate = graphapi_post(
        """
        mutation TerminateOwner($input: OwnerTerminateInput!) {
            owner_terminate(input: $input) { uuid }
        }
        """,
        variables={"input": {"uuid": str(owner), "to": "2010-01-01T00:00:00+01:00"}},
    )
    assert terminate.errors is None

    response = graphapi_post(
        """
        query Employees($filter: EmployeeFilter!) {
            employees(filter: $filter) {
                objects { uuid }
            }
        }
        """,
        variables={
            "filter": {
                "owner": {
                    "uuids": [str(owner)],
                    "from_date": "2000-01-01T00:00:00+01:00",
                    "to_date": None,
                },
                "from_date": "2000-01-01T00:00:00+01:00",
                "to_date": None,
            }
        },
    )
    assert response.errors is None
    assert response.data is not None
    employees = {UUID(o["uuid"]) for o in response.data["employees"]["objects"]}
    # person_a was owned while the role was Aktiv, so it is found. person_b was
    # only owned once the role had gone Inaktiv, so it must be absent.
    assert employees == {person_a}
