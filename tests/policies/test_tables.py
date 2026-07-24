# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the policy tables"""

from datetime import UTC
from datetime import datetime
from datetime import timedelta
from uuid import UUID

import pytest
from more_itertools import one
from psycopg import errors
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.exc import DataError
from sqlalchemy.exc import IntegrityError

from mora import db


@pytest.mark.integration_test
async def test_server_defaults(empty_db: db.AsyncSession) -> None:
    """A policy needs only a name; the database supplies the rest.

    Most of all `active`, which defaults to false: a policy grants nothing
    until it is switched on.
    """
    policy = db.Policy(name="Only a name")
    # The "all" kind ignores the value, so an actor may omit it
    policy.actors = [db.PolicyActor(kind=db.PolicyActorKind.all)]
    empty_db.add(policy)
    await empty_db.flush()

    assert isinstance(policy.id, UUID)
    assert policy.description == ""
    assert policy.active is False
    assert policy.created_at.tzinfo is not None
    assert datetime.now(UTC) - policy.created_at < timedelta(minutes=1)
    assert one(policy.actors).value == ""


@pytest.mark.integration_test
async def test_policy_actor_is_unique_within_a_policy(
    empty_db: db.AsyncSession,
) -> None:
    """uq_policy_actor: a (kind, value) is declared at most once per policy."""
    policy = db.Policy(name="Duplicate actor")
    policy.actors = [db.PolicyActor(kind=db.PolicyActorKind.role, value="admin")]
    empty_db.add(policy)
    await empty_db.flush()

    with pytest.raises(IntegrityError) as exc_info:
        empty_db.add(
            db.PolicyActor(
                policy_fk=policy.id,
                kind=db.PolicyActorKind.role,
                value="admin",
            )
        )
        await empty_db.flush()

    assert isinstance(exc_info.value.orig, errors.UniqueViolation)
    assert exc_info.value.orig.diag.constraint_name == "uq_policy_actor"


@pytest.mark.integration_test
async def test_policy_rule_is_unique_within_a_policy(
    empty_db: db.AsyncSession,
) -> None:
    """uq_policy_rule: a (type, field) is declared at most once per policy."""
    policy = db.Policy(name="Duplicate rule")
    policy.rules = [db.PolicyRule(type="Query", field="version")]
    empty_db.add(policy)
    await empty_db.flush()

    with pytest.raises(IntegrityError) as exc_info:
        empty_db.add(db.PolicyRule(policy_fk=policy.id, type="Query", field="version"))
        await empty_db.flush()

    assert isinstance(exc_info.value.orig, errors.UniqueViolation)
    assert exc_info.value.orig.diag.constraint_name == "uq_policy_rule"


@pytest.mark.integration_test
@pytest.mark.parametrize("value", [{"value": ""}, {}])
async def test_policy_actor_role_kind_requires_a_value(
    empty_db: db.AsyncSession, value: dict[str, str]
) -> None:
    """ck_policy_actor_value: only the "all" kind may have an empty value.

    Whether the empty value is written out or left to the server default.
    """
    policy = db.Policy(name="Nameless role")
    empty_db.add(policy)
    await empty_db.flush()

    with pytest.raises(IntegrityError) as exc_info:
        empty_db.add(
            db.PolicyActor(policy_fk=policy.id, kind=db.PolicyActorKind.role, **value)
        )
        await empty_db.flush()

    assert isinstance(exc_info.value.orig, errors.CheckViolation)
    assert exc_info.value.orig.diag.constraint_name == "ck_policy_actor_value"


@pytest.mark.integration_test
async def test_policy_actor_kind_is_a_native_enum(empty_db: db.AsyncSession) -> None:
    """kind is a policy_actor_kind enum; the database rejects other values."""
    policy = db.Policy(name="Bogus actor kind")
    empty_db.add(policy)
    await empty_db.flush()

    with pytest.raises(DataError) as exc_info:
        await empty_db.execute(
            text(
                "insert into policy_actor (kind, value, policy_fk) "
                "values ('bogus', '', :policy)"
            ),
            {"policy": policy.id},
        )

    assert isinstance(exc_info.value.orig, errors.InvalidTextRepresentation)
    assert "policy_actor_kind" in str(exc_info.value)


async def _child_counts(session: db.AsyncSession, policy_id: UUID) -> tuple[int, int]:
    """The number of actors and rules belonging to the given policy."""
    actors = await session.scalar(
        select(func.count()).where(db.PolicyActor.policy_fk == policy_id)
    )
    rules = await session.scalar(
        select(func.count()).where(db.PolicyRule.policy_fk == policy_id)
    )
    return actors, rules


@pytest.mark.integration_test
async def test_deleting_a_policy_deletes_its_actors_and_rules(
    empty_db: db.AsyncSession,
) -> None:
    """The delete-orphan cascade takes the children with the parent.

    The cascade is the ORM's, not the database's: the foreign keys carry no
    `on delete`, so deleting a policy in SQL is refused while it has children.
    """
    policy = db.Policy(name="Doomed")
    policy.actors = [db.PolicyActor(kind=db.PolicyActorKind.all)]
    policy.rules = [db.PolicyRule(type="Query", field="version")]
    empty_db.add(policy)
    await empty_db.flush()
    policy_id = policy.id

    assert await _child_counts(empty_db, policy_id) == (1, 1)

    await empty_db.delete(policy)
    await empty_db.flush()

    assert await _child_counts(empty_db, policy_id) == (0, 0)
