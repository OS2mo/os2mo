# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Helpers shared by the policy tests."""

from uuid import UUID

from more_itertools import one
from sqlalchemy import select

from mora import db
from tests.conftest import GQLResponse

# The one error a denial produces. Anything else is a genuine failure, not a
# permission decision, so the assertions below keep the two apart
DENIED = "No policy approved the access"


def assert_granted(response: GQLResponse) -> None:
    """Assert a policy approved the access."""
    assert response.errors is None


def assert_denied(response: GQLResponse) -> None:
    """Assert no policy approved the access, and nothing else went wrong."""
    assert response.errors is not None
    assert one(response.errors)["message"] == DENIED


def assert_access(response: GQLResponse, granted: bool) -> None:
    """Assert the access was granted or denied, as `granted` says."""
    if granted:
        assert_granted(response)
    else:
        assert_denied(response)


async def assert_bootstrapped(
    session: db.AsyncSession, name: str, actor: tuple[str, str]
) -> UUID:
    """Assert the named built-in policy is seeded active, bound to one actor.

    Returns its id, for the caller to check its rules against the source the
    migration seeded them from.
    """
    policy = (
        await session.scalars(select(db.Policy).where(db.Policy.name == name))
    ).one()
    assert policy.active is True
    seeded = (
        await session.scalars(
            select(db.PolicyActor).where(db.PolicyActor.policy_fk == policy.id)
        )
    ).one()
    assert (seeded.kind.value, seeded.value) == actor
    return policy.id
