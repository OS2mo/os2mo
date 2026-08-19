# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Helpers shared by the policy tests."""

from contextlib import suppress
from unittest import TestCase
from uuid import UUID

from sqlalchemy import select

from mora import db
from tests.conftest import GQLResponse
from tests.conftest import assert_denied
from tests.conftest import assert_granted


class UnorderedList(list):
    def __eq__(self, other: object) -> bool:
        with suppress(AssertionError, TypeError):
            TestCase().assertCountEqual(self, other)
            return True
        return False


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
