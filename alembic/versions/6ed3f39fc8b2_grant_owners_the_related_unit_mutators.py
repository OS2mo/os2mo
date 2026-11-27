# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Grant owners the related unit mutators"""

from collections.abc import Sequence
from string import Template

import sqlalchemy as sa

from alembic import op

revision: str = "6ed3f39fc8b2"
down_revision: str | Sequence[str] | None = "6eaa002d8321"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OWNER_UUID = "de1e6a7e-9bac-5eed-0000-006f776e6572"

policy_write_rule = sa.table(
    "policy_write_rule",
    sa.column("mutator", sa.Text),
    sa.column("condition", sa.Text),
    sa.column("graphql_version", sa.Integer),
    sa.column("policy_fk", sa.Uuid),
)


# The helpers below are copied from 4b2d9e7a1c36, as migrations must not change
# when the helpers of other migrations do


def _owner_filter(requirements: str) -> str:
    """Bind the owner filter matching the calling actor, by the token's uuid."""
    return Template(
        'cel.bind(owner_filter, {"owner": {"uuids": [token.uuid]}}, $requirements)'
    ).substitute(requirements=requirements)


def deny_tokens_without_uuid(rule: str) -> str:
    """Deny tokens carrying no uuid, before `rule` is evaluated."""
    return Template("token.uuid == null ? false : $rule").substitute(rule=rule)


def deny_requiring_nothing(rule: str) -> str:
    """Deny where `rule` requires nothing."""
    return Template(
        "cel.bind(required, dyn($rule), required == null ? false : required)"
    ).substitute(rule=rule)


def owner_rule(requirements: str) -> str:
    """The owner rule requiring what `requirements` names owned."""
    return deny_tokens_without_uuid(deny_requiring_nothing(_owner_filter(requirements)))


def org_unit(uuid_expr: str) -> str:
    """Require ownership of the unit named, if one is named.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors.
    """
    return Template("""(!has($uuid_expr) ? null : $uuid_expr == null ? null : dyn({
        "collection": "OrganisationUnit",
        "filter": {"descendant": {"uuids": [$uuid_expr]}, "owner": owner_filter}
    }))""").substitute(uuid_expr=uuid_expr)


def related_unit(uuid_expr: str) -> str:
    """Require ownership of either unit of the related unit, through any ancestor.

    The `org_unit` filter of a related unit matches either of its units.
    """
    return Template("""dyn({
        "collection": "RelatedUnit",
        "filter": {"uuids": [$uuid_expr], "org_unit": {
            "ancestor": {"owner": owner_filter}
        }}
    })""").substitute(uuid_expr=uuid_expr)


def either_unit(org_unit_expr: str, related_org_unit_expr: str) -> str:
    """Require ownership of either of the units."""
    return Template('dyn({"or": [$org_unit, $related_org_unit]})').substitute(
        org_unit=org_unit(org_unit_expr),
        related_org_unit=org_unit(related_org_unit_expr),
    )


# Owning either unit of a relation grants it, as `related_units_update` does
# for whichever unit is its `origin`. An update cannot change the units.
OWNER_RULES = [
    (
        "related_unit_create",
        owner_rule(either_unit("args.input.org_unit", "args.input.related_org_unit")),
    ),
    ("related_unit_terminate", owner_rule(related_unit("args.input.uuid"))),
    ("related_unit_update", owner_rule(related_unit("args.input.uuid"))),
]


def upgrade() -> None:
    op.bulk_insert(
        policy_write_rule,
        [
            {
                "mutator": mutator,
                "condition": condition,
                "graphql_version": 31,
                "policy_fk": OWNER_UUID,
            }
            for mutator, condition in OWNER_RULES
        ],
    )


def downgrade() -> None:
    op.execute(
        policy_write_rule.delete().where(
            policy_write_rule.c.policy_fk == OWNER_UUID,
            policy_write_rule.c.mutator.in_([mutator for mutator, _ in OWNER_RULES]),
        )
    )
