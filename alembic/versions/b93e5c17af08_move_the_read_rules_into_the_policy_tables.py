# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Move the read rules into the policy tables"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b93e5c17af08"
down_revision: str | Sequence[str] | None = "c4d81f0a7b32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

READER_UUID = "12bac000-9bac-5eed-0000-726561646572"

policy = sa.table(
    "policy",
    sa.column("pk", sa.Uuid),
    sa.column("name", sa.Text),
    sa.column("description", sa.Text),
    sa.column("role", sa.Text),
)
policy_read_rule = sa.table(
    "policy_read_rule",
    sa.column("pk", sa.Uuid),
    sa.column(
        "collection", postgresql.ENUM(name="policycollection", create_type=False)
    ),
    sa.column("policy_fk", sa.Uuid),
)
policy_read_rule_field = sa.table(
    "policy_read_rule_field",
    sa.column("field", sa.Text),
    sa.column("rule_fk", sa.Uuid),
)

# The fields a reader could read before the rules moved into the policy tables
READ_RULES: dict[str, frozenset[str]] = {
    "Address": frozenset(
        {
            "address_type",
            "address_type_response",
            "address_type_uuid",
            "employee",
            "employee_uuid",
            "engagement",
            "engagement_response",
            "engagement_uuid",
            "href",
            "ituser",
            "ituser_response",
            "ituser_uuid",
            "name",
            "org_unit",
            "org_unit_response",
            "org_unit_uuid",
            "person",
            "person_response",
            "resolve",
            "type",
            "user_key",
            "uuid",
            "validity",
            "value",
            "value2",
            "visibility",
            "visibility_response",
            "visibility_uuid",
        }
    ),
    "Association": frozenset(
        {
            "association_type",
            "association_type_response",
            "association_type_uuid",
            "dynamic_class",
            "dynamic_class_response",
            "dynamic_class_uuid",
            "employee",
            "employee_uuid",
            "it_user",
            "it_user_response",
            "it_user_uuid",
            "job_function",
            "job_function_response",
            "job_function_uuid",
            "org_unit",
            "org_unit_response",
            "org_unit_uuid",
            "person",
            "person_response",
            "primary",
            "primary_response",
            "primary_uuid",
            "substitute",
            "substitute_response",
            "substitute_uuid",
            "trade_union",
            "trade_union_response",
            "trade_union_uuid",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Class": frozenset(
        {
            "children",
            "children_response",
            "description",
            "example",
            "facet",
            "facet_response",
            "facet_uuid",
            "full_name",
            "it_system",
            "it_system_response",
            "it_system_uuid",
            "name",
            "org_uuid",
            "owner",
            "owner_response",
            "parent",
            "parent_response",
            "parent_uuid",
            "published",
            "scope",
            "top_level_facet",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Employee": frozenset(
        {
            "addresses",
            "addresses_response",
            "associations",
            "associations_response",
            "cpr_no",
            "cpr_number",
            "engagements",
            "engagements_response",
            "given_name",
            "givenname",
            "itusers",
            "itusers_response",
            "leaves",
            "leaves_response",
            "manager_roles",
            "manager_roles_response",
            "name",
            "nickname",
            "nickname_given_name",
            "nickname_givenname",
            "nickname_surname",
            "seniority",
            "surname",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Engagement": frozenset(
        {
            "addresses_response",
            "employee",
            "employee_uuid",
            "engagement_type",
            "engagement_type_response",
            "engagement_type_uuid",
            "extension_1",
            "extension_10",
            "extension_2",
            "extension_3",
            "extension_4",
            "extension_5",
            "extension_6",
            "extension_7",
            "extension_8",
            "extension_9",
            "fraction",
            "is_primary",
            "itusers",
            "itusers_response",
            "job_function",
            "job_function_response",
            "job_function_uuid",
            "leave",
            "leave_response",
            "leave_uuid",
            "managers",
            "org_unit",
            "org_unit_response",
            "org_unit_uuid",
            "person",
            "person_response",
            "primary",
            "primary_response",
            "primary_uuid",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Facet": frozenset(
        {
            "children",
            "children_response",
            "classes",
            "classes_responses",
            "description",
            "org_uuid",
            "parent",
            "parent_response",
            "parent_uuid",
            "published",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "ITSystem": frozenset(
        {
            "name",
            "roles",
            "roles_response",
            "system_type",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "ITUser": frozenset(
        {
            "addresses",
            "addresses_response",
            "binding_type",
            "employee",
            "employee_uuid",
            "engagement",
            "engagement_response",
            "engagement_uuid",
            "engagement_uuids",
            "engagements",
            "engagements_responses",
            "external_id",
            "itsystem",
            "itsystem_response",
            "itsystem_uuid",
            "org_unit",
            "org_unit_response",
            "org_unit_uuid",
            "person",
            "person_response",
            "primary",
            "primary_response",
            "primary_uuid",
            "rolebindings",
            "rolebindings_response",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "KLE": frozenset(
        {
            "kle_aspect_uuids",
            "kle_aspects",
            "kle_aspects_response",
            "kle_number",
            "kle_number_response",
            "kle_number_uuid",
            "org_unit",
            "org_unit_response",
            "org_unit_uuid",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Leave": frozenset(
        {
            "employee",
            "employee_uuid",
            "engagement",
            "engagement_response",
            "engagement_uuid",
            "leave_type",
            "leave_type_response",
            "leave_type_uuid",
            "person",
            "person_response",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Manager": frozenset(
        {
            "employee",
            "employee_uuid",
            "engagement_response",
            "manager_level",
            "manager_level_response",
            "manager_level_uuid",
            "manager_type",
            "manager_type_response",
            "manager_type_uuid",
            "org_unit",
            "org_unit_response",
            "org_unit_uuid",
            "person",
            "person_response",
            "responsibilities",
            "responsibilities_response",
            "responsibility_uuids",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Organisation": frozenset(
        {
            "municipality_code",
            "name",
            "type",
            "user_key",
            "uuid",
        }
    ),
    "OrganisationUnit": frozenset(
        {
            "addresses",
            "addresses_response",
            "ancestors",
            "associations",
            "associations_response",
            "child_count",
            "children",
            "children_response",
            "engagements",
            "engagements_response",
            "has_children",
            "itusers",
            "itusers_response",
            "kles",
            "kles_response",
            "leaves",
            "leaves_response",
            "managers",
            "managers_response",
            "name",
            "org_unit_hierarchy",
            "org_unit_hierarchy_model",
            "org_unit_level",
            "org_unit_level_uuid",
            "owners",
            "parent",
            "parent_response",
            "parent_uuid",
            "related_units",
            "related_units_response",
            "root",
            "root_response",
            "time_planning",
            "time_planning_response",
            "time_planning_uuid",
            "type",
            "unit_hierarchy_response",
            "unit_level_response",
            "unit_type",
            "unit_type_response",
            "unit_type_uuid",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "Owner": frozenset(
        {
            "employee_uuid",
            "org_unit",
            "org_unit_response",
            "org_unit_uuid",
            "owner",
            "owner_inference_priority",
            "owner_response",
            "owner_uuid",
            "person",
            "person_response",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "RelatedUnit": frozenset(
        {
            "org_unit_uuids",
            "org_units",
            "org_units_response",
            "type",
            "user_key",
            "uuid",
            "validity",
        }
    ),
    "RoleBinding": frozenset(
        {
            "ituser",
            "ituser_response",
            "org_unit",
            "org_unit_response",
            "role",
            "role_response",
            "user_key",
            "uuid",
            "validity",
        }
    ),
}


def upgrade() -> None:
    rule_pks = {collection: uuid4() for collection in READ_RULES}

    op.bulk_insert(
        policy,
        [
            {
                "pk": READER_UUID,
                "name": "Reader",
                "description": "Read access to the fields of every collection",
                "role": "reader",
            }
        ],
    )
    op.bulk_insert(
        policy_read_rule,
        [
            {
                "pk": rule_pks[collection],
                "collection": collection,
                "policy_fk": READER_UUID,
            }
            for collection in READ_RULES
        ],
    )
    op.bulk_insert(
        policy_read_rule_field,
        [
            {
                "field": field,
                "rule_fk": rule_pks[collection],
            }
            for collection, fields in READ_RULES.items()
            for field in fields
        ],
    )


def downgrade() -> None:
    op.execute(
        policy_read_rule_field.delete().where(
            policy_read_rule_field.c.rule_fk == policy_read_rule.c.pk,
            policy_read_rule.c.policy_fk == READER_UUID,
        )
    )
    op.execute(
        policy_read_rule.delete().where(policy_read_rule.c.policy_fk == READER_UUID)
    )
    op.execute(policy.delete().where(policy.c.pk == READER_UUID))
