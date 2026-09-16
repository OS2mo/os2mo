# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Seed the built-in Owner policy."""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b5e2f81c9d30"
down_revision: str | Sequence[str] | None = "a3d1c7e05f24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# "Owner" spelled out in the last group
OWNER_UUID = "12bac000-9bac-5eed-0000-004f776e6572"

policy_selector_kind = postgresql.ENUM(
    "role",
    "all",
    name="policy_selector_kind",
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
policy_selector = sa.table(
    "policy_selector",
    sa.column("kind", policy_selector_kind),
    sa.column("value", sa.String),
    sa.column("policy_fk", sa.Uuid),
)
policy_mutator = sa.table(
    "policy_mutator",
    sa.column("name", sa.String),
    sa.column("condition", sa.String),
    sa.column("filter", sa.String),
    sa.column("policy_fk", sa.Uuid),
)

# The employee filter naming the caller: the employee holding the token's uuid
# as an external id in the authoritative IT system, if one is configured, and
# otherwise the employee of that uuid. The branches are differently-shaped
# maps, hence `dyn`, and a token carrying no uuid names nobody
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

# Every rule reads `owner`: the filter naming what the caller owns
BIND = """cel.bind(owner, {"owner": %s},
    %s
)"""


def person_uuids(item: str, *, employee: bool) -> str:
    """The person the item names, as a list, or an empty one."""
    named = f"has({item}.person) && {item}.person != null ? [{item}.person] : []"
    if employee:
        named = (
            f"has({item}.person) && {item}.person != null ? [{item}.person] : "
            f"(has({item}.employee) && {item}.employee != null ? [{item}.employee] : [])"
        )
    return f"({named})"


def names_unit(item: str) -> str:
    """Whether the item names a unit."""
    return f"has({item}.org_unit) && {item}.org_unit != null"


def names_linked(item: str, *, employee: bool) -> str:
    """Whether the item names a unit or a person."""
    return f"{names_unit(item)} || size({person_uuids(item, employee=employee)}) > 0"


def unit_spec(uuid: str) -> str:
    """The unit named, owned in itself or through an ancestor."""
    return (
        """{
        "collection": "OrganisationUnit",
        "filter": {"descendant": {"uuids": [%s]}, "owner": owner}
    }"""
        % uuid
    )


def person_spec(uuids: str) -> str:
    """The person named, owned."""
    return (
        """{
        "collection": "Employee",
        "filter": {"uuids": %s, "owner": owner}
    }"""
        % uuids
    )


def linked_spec(item: str, *, employee: bool) -> str:
    """The unit the item names, or else the person it names."""
    return "(%s\n            ? %s\n            : %s)" % (
        names_unit(item),
        unit_spec(f"{item}.org_unit"),
        person_spec(person_uuids(item, employee=employee)),
    )


def through_unit(collection: str, item: str) -> str:
    """The detail named, through the unit it links, owned through any ancestor."""
    return """{
        "collection": "%s",
        "filter": {
            "uuids": [%s.uuid],
            "org_unit": {"ancestor": {"owner": owner}}
        }
    }""" % (collection, item)


def through_person(collection: str, item: str) -> str:
    """The detail named, through the person it links, owned."""
    return """{
        "collection": "%s",
        "filter": {"uuids": [%s.uuid], "employee": {"owner": owner}}
    }""" % (collection, item)


def keeps_parent(item: str) -> str:
    """The parent the edit names, being the one the unit already has."""
    return """{
        "collection": "OrganisationUnit",
        "filter": {"uuids": [%s.parent], "child": {"uuids": [%s.uuid]}}
    }""" % (item, item)


def one(spec: str) -> str:
    """The one object a rule requires owned."""
    return f"[{spec}]"


def each(spec: str) -> str:
    """The same object required of every item of a bulk call."""
    return f"args.input.map(i, {spec})"


def each_naming(spec: str, named: str) -> str:
    """The same object required of every item naming one.

    An item naming nothing requires nothing, as in a call whose every item
    names nothing, which requires nothing and so is granted to nobody.
    """
    return f"args.input.filter(i, {named}).map(i, {spec})"


def moved(item: str, *, employee: bool) -> str:
    """Where the edit moves the detail to, if it names anywhere."""
    return "(%s ? %s : [])" % (
        names_linked(item, employee=employee),
        one(linked_spec(item, employee=employee)),
    )


def moved_unit(item: str) -> str:
    """The unit the edit moves the detail to, if it names one."""
    return "(%s ? %s : [])" % (names_unit(item), one(unit_spec(f"{item}.org_unit")))


def both(*required: str) -> str:
    """Every object of each, all of them required."""
    return " + ".join(required)


INPUT = "args.input"
# Whether the single input names what the rule reads off it
NAMES_UUID = "has(args.input.uuid) && args.input.uuid != null"
NAMES_UNIT = names_unit(INPUT)
NAMES_PARENT = "has(args.input.parent) && args.input.parent != null"
NAMES_PERSON = "size(%s) > 0" % person_uuids(INPUT, employee=False)


# What a caller must own for a mutator to be theirs, as (mutator, condition,
# filter). A mutator is named once per way of owning what it changes, and a
# mutator named nowhere here is granted to nobody: classes, facets, IT systems
# and the event objects link neither an org unit nor a person
OWNER_RULES: list[tuple[str, str, str]] = [
    # The unit or the person the address links (exactly one is set)
    ("address_create", "", one(linked_spec(INPUT, employee=True))),
    ("address_terminate", "", one(through_unit("Address", INPUT))),
    ("address_terminate", "", one(through_person("Address", INPUT))),
    (
        "address_update",
        "",
        both(one(through_unit("Address", INPUT)), moved(INPUT, employee=True)),
    ),
    (
        "address_update",
        "",
        both(one(through_person("Address", INPUT)), moved(INPUT, employee=True)),
    ),
    (
        "addresses_create",
        "",
        each_naming(linked_spec("i", employee=True), names_linked("i", employee=True)),
    ),
    # The unit or the person of the association
    ("association_create", "", one(linked_spec(INPUT, employee=True))),
    ("association_terminate", "", one(through_unit("Association", INPUT))),
    ("association_terminate", "", one(through_person("Association", INPUT))),
    (
        "association_update",
        "",
        both(one(through_unit("Association", INPUT)), moved(INPUT, employee=True)),
    ),
    (
        "association_update",
        "",
        both(one(through_person("Association", INPUT)), moved(INPUT, employee=True)),
    ),
    # The employee itself
    ("employee_create", NAMES_UUID, one(person_spec("[args.input.uuid]"))),
    ("employee_terminate", "", one(person_spec("[args.input.uuid]"))),
    ("employee_update", "", one(person_spec("[args.input.uuid]"))),
    # The unit or the person of the engagement
    ("engagement_create", "", one(linked_spec(INPUT, employee=True))),
    ("engagement_terminate", "", one(through_unit("Engagement", INPUT))),
    ("engagement_terminate", "", one(through_person("Engagement", INPUT))),
    (
        "engagement_update",
        "",
        both(one(through_unit("Engagement", INPUT)), moved(INPUT, employee=True)),
    ),
    (
        "engagement_update",
        "",
        both(one(through_person("Engagement", INPUT)), moved(INPUT, employee=True)),
    ),
    (
        "engagements_create",
        "",
        each_naming(linked_spec("i", employee=True), names_linked("i", employee=True)),
    ),
    (
        "engagements_update",
        "",
        both(
            each(through_unit("Engagement", "i")),
            each_naming(
                linked_spec("i", employee=True), names_linked("i", employee=True)
            ),
        ),
    ),
    (
        "engagements_update",
        "",
        both(
            each(through_person("Engagement", "i")),
            each_naming(
                linked_spec("i", employee=True), names_linked("i", employee=True)
            ),
        ),
    ),
    # The unit of the IT-association, whose update cannot name a person
    ("itassociation_create", "", one(linked_spec(INPUT, employee=False))),
    ("itassociation_terminate", "", one(through_unit("Association", INPUT))),
    ("itassociation_terminate", "", one(through_person("Association", INPUT))),
    (
        "itassociation_update",
        "",
        both(one(through_unit("Association", INPUT)), moved_unit(INPUT)),
    ),
    (
        "itassociation_update",
        "",
        both(one(through_person("Association", INPUT)), moved_unit(INPUT)),
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    ("ituser_create", "", one(linked_spec(INPUT, employee=False))),
    ("ituser_terminate", "", one(through_unit("ITUser", INPUT))),
    ("ituser_terminate", "", one(through_person("ITUser", INPUT))),
    (
        "ituser_update",
        "",
        both(one(through_unit("ITUser", INPUT)), moved(INPUT, employee=False)),
    ),
    (
        "ituser_update",
        "",
        both(one(through_person("ITUser", INPUT)), moved(INPUT, employee=False)),
    ),
    (
        "itusers_create",
        "",
        each_naming(
            linked_spec("i", employee=False), names_linked("i", employee=False)
        ),
    ),
    # The annotated unit. A KLE links no person, so owning its unit is the
    # only way to own it
    ("kle_create", NAMES_UNIT, one(unit_spec("args.input.org_unit"))),
    ("kle_terminate", "", one(through_unit("KLE", INPUT))),
    ("kle_update", "", both(one(through_unit("KLE", INPUT)), moved_unit(INPUT))),
    # The person on leave
    (
        "leave_create",
        NAMES_PERSON,
        one(person_spec(person_uuids(INPUT, employee=False))),
    ),
    ("leave_terminate", "", one(through_unit("Leave", INPUT))),
    ("leave_terminate", "", one(through_person("Leave", INPUT))),
    (
        "leave_update",
        "",
        both(
            one(through_unit("Leave", INPUT)),
            "(%s ? %s : [])"
            % (NAMES_PERSON, one(person_spec(person_uuids(INPUT, employee=False)))),
        ),
    ),
    (
        "leave_update",
        "",
        both(
            one(through_person("Leave", INPUT)),
            "(%s ? %s : [])"
            % (NAMES_PERSON, one(person_spec(person_uuids(INPUT, employee=False)))),
        ),
    ),
    # The unit or the person of the manager
    ("manager_create", "", one(linked_spec(INPUT, employee=False))),
    ("manager_terminate", "", one(through_unit("Manager", INPUT))),
    ("manager_terminate", "", one(through_person("Manager", INPUT))),
    (
        "manager_update",
        "",
        both(one(through_unit("Manager", INPUT)), moved(INPUT, employee=False)),
    ),
    (
        "manager_update",
        "",
        both(one(through_person("Manager", INPUT)), moved(INPUT, employee=False)),
    ),
    (
        "managers_create",
        "",
        each_naming(
            linked_spec("i", employee=False), names_linked("i", employee=False)
        ),
    ),
    # The parent, or the unit itself and its new parent if it is being moved
    ("org_unit_create", NAMES_PARENT, one(unit_spec("args.input.parent"))),
    ("org_unit_terminate", "", one(unit_spec("args.input.uuid"))),
    # An edit naming no parent does not move the unit
    (
        "org_unit_update",
        f"!({NAMES_PARENT})",
        one(unit_spec("args.input.uuid")),
    ),
    # An edit naming the parent the unit already has does not move it either
    (
        "org_unit_update",
        NAMES_PARENT,
        both(one(unit_spec("args.input.uuid")), one(keeps_parent(INPUT))),
    ),
    # A move requires the unit it is moved under owned as well
    (
        "org_unit_update",
        NAMES_PARENT,
        both(one(unit_spec("args.input.uuid")), one(unit_spec("args.input.parent"))),
    ),
    # The unit or the person owned (exactly one is set)
    ("owner_create", "", one(linked_spec(INPUT, employee=False))),
    ("owner_terminate", "", one(through_unit("Owner", INPUT))),
    ("owner_terminate", "", one(through_person("Owner", INPUT))),
    (
        "owner_update",
        "",
        both(one(through_unit("Owner", INPUT)), moved(INPUT, employee=False)),
    ),
    (
        "owner_update",
        "",
        both(one(through_person("Owner", INPUT)), moved(INPUT, employee=False)),
    ),
    # Related units have a single `origin` field and a list of `destination`s.
    # Originally we required ownership of both the origin and destinations, but
    # that's not compatible with the old service-api owner calculation
    (
        "related_units_update",
        "has(args.input.origin) && args.input.origin != null",
        one(unit_spec("args.input.origin")),
    ),
    # The unit of the role-binding, if one is named. A role-binding links no
    # person either
    ("rolebinding_create", NAMES_UNIT, one(unit_spec("args.input.org_unit"))),
    ("rolebinding_terminate", "", one(through_unit("RoleBinding", INPUT))),
    (
        "rolebinding_update",
        "",
        both(one(through_unit("RoleBinding", INPUT)), moved_unit(INPUT)),
    ),
    (
        "rolebindings_create",
        "",
        each_naming(unit_spec("i.org_unit"), names_unit("i")),
    ),
]


def upgrade() -> None:
    op.execute(
        policy.insert().values(
            id=OWNER_UUID,
            name="Owner",
            description="Changes the objects the caller owns.",
            active=True,
        )
    )
    op.execute(
        policy_selector.insert().values(
            kind="role", value="owner", policy_fk=OWNER_UUID
        )
    )
    op.bulk_insert(
        policy_mutator,
        [
            {
                "name": name,
                "condition": condition,
                "filter": BIND % (ACTOR, required),
                "policy_fk": OWNER_UUID,
            }
            for name, condition, required in OWNER_RULES
        ],
    )


def downgrade() -> None:
    op.execute(policy_mutator.delete().where(policy_mutator.c.policy_fk == OWNER_UUID))
    op.execute(
        policy_selector.delete().where(policy_selector.c.policy_fk == OWNER_UUID)
    )
    op.execute(policy.delete().where(policy.c.id == OWNER_UUID))
