# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Tests of the built-in Public policy."""

import pytest
from sqlalchemy import select
from sqlalchemy import update

from alembic_helpers.public_fields import PUBLIC_FIELDS
from mora import db
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import assert_denied
from tests.conftest import assert_granted
from tests.policies.helpers import assert_bootstrapped

VERSION_QUERY = "query { version { mo_version } }"


@pytest.mark.integration_test
async def test_public_policy_bootstrapped(empty_db: db.AsyncSession) -> None:
    """The Public policy is seeded active, bound to every actor."""
    policy_id = await assert_bootstrapped(empty_db, "Public", ("all", ""))
    rules = (
        await empty_db.execute(
            select(db.PolicyRule.type, db.PolicyRule.field).where(
                db.PolicyRule.policy_fk == policy_id
            )
        )
    ).all()
    assert set(rules) == PUBLIC_FIELDS


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_public_field_readable_without_roles(
    graphapi_post: GraphAPIPost, set_auth: SetAuth
) -> None:
    """The all-actor Public policy grants public fields to a roleless token."""
    set_auth(role="nobody")
    assert_granted(graphapi_post(VERSION_QUERY))


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_public_policy_deactivation_denies(
    graphapi_post: GraphAPIPost,
    set_auth: SetAuth,
    raw_session: db.AsyncSession,
) -> None:
    """A deactivated policy does not grant access."""
    await raw_session.execute(
        update(db.Policy).where(db.Policy.name == "Public").values(active=False)
    )
    await raw_session.commit()
    set_auth(role="nobody")
    assert_denied(graphapi_post(VERSION_QUERY))
