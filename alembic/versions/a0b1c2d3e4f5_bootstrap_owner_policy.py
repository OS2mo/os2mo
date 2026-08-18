# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Bootstrap the built-in "Owner" policy"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a0b1c2d3e4f5"
down_revision: str | Sequence[str] | None = "f9a0b1c2d3e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


OWNER_UUID = "b0550000-9bac-5eed-0000-006f776e6572"

policy_actor_kind = postgresql.ENUM(
    "role",
    "all",
    name="policy_actor_kind",
    # Avoid implicit creation
    create_type=False,
)
policy = sa.table(
    "policy",
    sa.column("id", sa.Uuid),
    sa.column("name", sa.String),
    sa.column("description", sa.String),
    sa.column("active", sa.Boolean),
)
policy_actor = sa.table(
    "policy_actor",
    sa.column("kind", policy_actor_kind),
    sa.column("value", sa.String),
    sa.column("policy_fk", sa.Uuid),
)
policy_rule = sa.table(
    "policy_rule",
    sa.column("type", sa.String),
    sa.column("field", sa.String),
    sa.column("condition", sa.String),
    sa.column("filter", sa.String),
    sa.column("policy_fk", sa.Uuid),
)


# The employee filter naming the caller. The branches are differently-shaped
# maps, hence `dyn`, and a token carrying no uuid matches nothing
ACTOR = """settings.keycloak_rbac_authoritative_it_system_for_owners != null
        ? dyn({
            "ituser": {
                "itsystem": {
                    "uuids": [settings.keycloak_rbac_authoritative_it_system_for_owners]
                },
                "external_ids": token.uuid != null ? [token.uuid] : []
            }
        })
        : dyn({"uuids": token.uuid != null ? [token.uuid] : []})"""


# AND: a rule grants only if every clause finds what it names
def and_(*clauses: str) -> str:
    return " + ".join(clauses)


# The unit an edit moves a detail to, owned as well
MOVED_TO_UNIT = """
            cel.bind(destination, has(args.input.org_unit) ? args.input.org_unit : null,
                destination != null
                    ? [{
                        "collection": "org_unit",
                        "filter": {"uuids": [destination], "ancestor": {"owner": owner}}
                    }]
                    : [])
"""

# The same, for the bulk mutators
MOVED_TO_UNIT_BULK = """
            args.input.filter(i, has(i.org_unit) && i.org_unit != null).map(i, {
                "collection": "org_unit",
                "filter": {"uuids": [i.org_unit], "ancestor": {"owner": owner}}
            })
"""


# One rule per way of owning what a mutator touches, OR-ed, each gated on the
# input naming what it checks. A mutator missing here is granted nothing: classes,
# facets, IT systems and the event objects link neither an org unit nor a person
OWNER_RULES: list[tuple[str, str, str]] = [
    (
        "address_create",
        "has(args.input.org_unit) && args.input.org_unit != null",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "address_create",
        """
        (!has(args.input.org_unit) || args.input.org_unit == null)
        && has(args.input.employee) && args.input.employee != null
        """,
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.employee], "owner": owner}
        }]
        """,
    ),
    (
        "address_create",
        """
        (!has(args.input.org_unit) || args.input.org_unit == null)
        && (!has(args.input.employee) || args.input.employee == null)
        && has(args.input.person) && args.input.person != null
        """,
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.person], "owner": owner}
        }]
        """,
    ),
    (
        "address_terminate",
        "",
        """
        [{
            "collection": "address",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "address_terminate",
        "",
        """
        [{
            "collection": "address",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "address_update",
        "",
        and_(
            """
            [{
                "collection": "address",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "address_update",
        "",
        and_(
            """
            [{
                "collection": "address",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "addresses_create",
        "",
        """
        args.input.map(i,
            has(i.org_unit) && i.org_unit != null
                ? {
                    "collection": "org_unit",
                    "filter": {"uuids": [i.org_unit], "ancestor": {"owner": owner}}
                }
                : {
                    "collection": "employee",
                    "filter": {
                        "uuids": has(i.employee) && i.employee != null
                            ? [i.employee]
                            : (has(i.person) && i.person != null ? [i.person] : []),
                        "owner": owner
                    }
                }
        )
        """,
    ),
    (
        "association_create",
        "",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "association_terminate",
        "",
        """
        [{
            "collection": "association",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "association_terminate",
        "",
        """
        [{
            "collection": "association",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "association_update",
        "",
        and_(
            """
            [{
                "collection": "association",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "association_update",
        "",
        and_(
            """
            [{
                "collection": "association",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "employee_create",
        "has(args.input.uuid) && args.input.uuid != null",
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.uuid], "owner": owner}
        }]
        """,
    ),
    (
        "employee_terminate",
        "",
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.uuid], "owner": owner}
        }]
        """,
    ),
    (
        "employee_update",
        "",
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.uuid], "owner": owner}
        }]
        """,
    ),
    (
        "engagement_create",
        "",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "engagement_terminate",
        "",
        """
        [{
            "collection": "engagement",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "engagement_terminate",
        "",
        """
        [{
            "collection": "engagement",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "engagement_update",
        "",
        and_(
            """
            [{
                "collection": "engagement",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "engagement_update",
        "",
        and_(
            """
            [{
                "collection": "engagement",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "engagements_create",
        "",
        """
        args.input.map(i, {
            "collection": "org_unit",
            "filter": {"uuids": [i.org_unit], "ancestor": {"owner": owner}}
        })
        """,
    ),
    (
        "engagements_update",
        "",
        and_(
            """
            args.input.map(i, {
                "collection": "engagement",
                "filter": {
                    "uuids": [i.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            })
            """,
            MOVED_TO_UNIT_BULK,
        ),
    ),
    (
        "engagements_update",
        "",
        and_(
            """
            args.input.map(i, {
                "collection": "engagement",
                "filter": {"uuids": [i.uuid], "employee": {"owner": owner}}
            })
            """,
            MOVED_TO_UNIT_BULK,
        ),
    ),
    (
        "itassociation_create",
        "",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "itassociation_terminate",
        "",
        """
        [{
            "collection": "association",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "itassociation_terminate",
        "",
        """
        [{
            "collection": "association",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "itassociation_update",
        "",
        and_(
            """
            [{
                "collection": "association",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "itassociation_update",
        "",
        and_(
            """
            [{
                "collection": "association",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "ituser_create",
        "has(args.input.org_unit) && args.input.org_unit != null",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "ituser_create",
        """
        (!has(args.input.org_unit) || args.input.org_unit == null)
        && has(args.input.person) && args.input.person != null
        """,
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.person], "owner": owner}
        }]
        """,
    ),
    (
        "ituser_terminate",
        "",
        """
        [{
            "collection": "ituser",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "ituser_terminate",
        "",
        """
        [{
            "collection": "ituser",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "ituser_update",
        "",
        and_(
            """
            [{
                "collection": "ituser",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "ituser_update",
        "",
        and_(
            """
            [{
                "collection": "ituser",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "itusers_create",
        "",
        """
        args.input.map(i,
            has(i.org_unit) && i.org_unit != null
                ? {
                    "collection": "org_unit",
                    "filter": {"uuids": [i.org_unit], "ancestor": {"owner": owner}}
                }
                : {
                    "collection": "employee",
                    "filter": {
                        "uuids": has(i.person) && i.person != null ? [i.person] : [],
                        "owner": owner
                    }
                }
        )
        """,
    ),
    (
        "kle_create",
        "",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "kle_terminate",
        "",
        """
        [{
            "collection": "kle",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "kle_terminate",
        "",
        """
        [{
            "collection": "kle",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "kle_update",
        "",
        and_(
            """
            [{
                "collection": "kle",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "kle_update",
        "",
        and_(
            """
            [{
                "collection": "kle",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "leave_create",
        "",
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.person], "owner": owner}
        }]
        """,
    ),
    (
        "leave_terminate",
        "",
        """
        [{
            "collection": "leave",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "leave_terminate",
        "",
        """
        [{
            "collection": "leave",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "leave_update",
        "",
        """
        [{
            "collection": "leave",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "leave_update",
        "",
        """
        [{
            "collection": "leave",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "manager_create",
        "",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "manager_terminate",
        "",
        """
        [{
            "collection": "manager",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "manager_terminate",
        "",
        """
        [{
            "collection": "manager",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "manager_update",
        "",
        and_(
            """
            [{
                "collection": "manager",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "manager_update",
        "",
        and_(
            """
            [{
                "collection": "manager",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "managers_create",
        "",
        """
        args.input.map(i, {
            "collection": "org_unit",
            "filter": {"uuids": [i.org_unit], "ancestor": {"owner": owner}}
        })
        """,
    ),
    (
        "org_unit_create",
        "has(args.input.parent) && args.input.parent != null",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.parent], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "org_unit_terminate",
        "",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.uuid], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    # An edit naming no parent, or naming root, only needs the unit itself owned
    (
        "org_unit_update",
        "!has(args.input.parent) || args.input.parent == null",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.uuid], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    # An edit naming the unit's current parent does not move it
    (
        "org_unit_update",
        "has(args.input.parent) && args.input.parent != null",
        and_(
            """
            [{
                "collection": "org_unit",
                "filter": {"uuids": [args.input.uuid], "ancestor": {"owner": owner}}
            }]
            """,
            """
            [{
                "collection": "org_unit",
                "filter": {
                    "uuids": [args.input.parent],
                    "child": {"uuids": [args.input.uuid]}
                }
            }]
            """,
        ),
    ),
    # A move requires the destination owned as well
    (
        "org_unit_update",
        "has(args.input.parent) && args.input.parent != null",
        and_(
            """
            [{
                "collection": "org_unit",
                "filter": {"uuids": [args.input.uuid], "ancestor": {"owner": owner}}
            }]
            """,
            """
            [{
                "collection": "org_unit",
                "filter": {"uuids": [args.input.parent], "ancestor": {"owner": owner}}
            }]
            """,
        ),
    ),
    (
        "owner_create",
        "has(args.input.org_unit) && args.input.org_unit != null",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "owner_create",
        """
        (!has(args.input.org_unit) || args.input.org_unit == null)
        && has(args.input.person) && args.input.person != null
        """,
        """
        [{
            "collection": "employee",
            "filter": {"uuids": [args.input.person], "owner": owner}
        }]
        """,
    ),
    (
        "owner_terminate",
        "",
        """
        [{
            "collection": "owner",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "owner_terminate",
        "",
        """
        [{
            "collection": "owner",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "owner_update",
        "",
        and_(
            """
            [{
                "collection": "owner",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "owner_update",
        "",
        and_(
            """
            [{
                "collection": "owner",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "related_units_update",
        "",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.origin], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "rolebinding_create",
        "has(args.input.org_unit) && args.input.org_unit != null",
        """
        [{
            "collection": "org_unit",
            "filter": {"uuids": [args.input.org_unit], "ancestor": {"owner": owner}}
        }]
        """,
    ),
    (
        "rolebinding_terminate",
        "",
        """
        [{
            "collection": "rolebinding",
            "filter": {
                "uuids": [args.input.uuid],
                "org_unit": {"ancestor": {"owner": owner}}
            }
        }]
        """,
    ),
    (
        "rolebinding_terminate",
        "",
        """
        [{
            "collection": "rolebinding",
            "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
        }]
        """,
    ),
    (
        "rolebinding_update",
        "",
        and_(
            """
            [{
                "collection": "rolebinding",
                "filter": {
                    "uuids": [args.input.uuid],
                    "org_unit": {"ancestor": {"owner": owner}}
                }
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "rolebinding_update",
        "",
        and_(
            """
            [{
                "collection": "rolebinding",
                "filter": {"uuids": [args.input.uuid], "employee": {"owner": owner}}
            }]
            """,
            MOVED_TO_UNIT,
        ),
    ),
    (
        "rolebindings_create",
        "",
        """
        args.input.map(i, {
            "collection": "org_unit",
            "filter": {
                "uuids": has(i.org_unit) && i.org_unit != null ? [i.org_unit] : [],
                "ancestor": {"owner": owner}
            }
        })
        """,
    ),
]


# Every rule reads `owner`: the filter naming what the caller owns
BIND = """cel.bind(owner, {"owner": %s},
    %s
)"""


def upgrade() -> None:
    op.execute(
        policy.insert().values(
            id=OWNER_UUID,
            name="Owner",
            description="Grants owners access to the entities they own. A default starter policy; deactivate it if unwanted.",
            active=True,
        )
    )
    op.execute(
        policy_actor.insert().values(kind="role", value="owner", policy_fk=OWNER_UUID)
    )
    op.bulk_insert(
        policy_rule,
        [
            {
                "type": "Mutation",
                "field": field,
                "condition": condition,
                "filter": BIND % (ACTOR, selection),
                "policy_fk": OWNER_UUID,
            }
            for field, condition, selection in OWNER_RULES
        ],
    )


def downgrade() -> None:
    op.execute(policy_rule.delete().where(policy_rule.c.policy_fk == OWNER_UUID))
    op.execute(policy_actor.delete().where(policy_actor.c.policy_fk == OWNER_UUID))
    op.execute(policy.delete().where(policy.c.id == OWNER_UUID))
