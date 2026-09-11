# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from functools import partial

from mora.auth.keycloak.uuid_extractor import OwnerRule
from mora.auth.keycloak.uuid_extractor import all_of
from mora.auth.keycloak.uuid_extractor import check_parent
from mora.auth.keycloak.uuid_extractor import each
from mora.auth.keycloak.uuid_extractor import get_entities_graphql
from mora.auth.keycloak.uuid_extractor import org_unit
from mora.auth.keycloak.uuid_extractor import org_unit_or_person
from mora.auth.keycloak.uuid_extractor import person
from mora.graphapi.permissions import CollectionPermissionType
from mora.graphapi.permissions import Collections

# The collection and operation each mutator touches
_TOUCHES: dict[str, tuple[Collections, CollectionPermissionType]] = {
    "address_terminate": ("address", "terminate"),
    "address_update": ("address", "update"),
    "association_terminate": ("association", "terminate"),
    "association_update": ("association", "update"),
    "engagement_terminate": ("engagement", "terminate"),
    "engagement_update": ("engagement", "update"),
    "engagements_update": ("engagement", "update"),
    "itassociation_terminate": ("association", "terminate"),
    "itassociation_update": ("association", "update"),
    "ituser_terminate": ("ituser", "terminate"),
    "ituser_update": ("ituser", "update"),
    "kle_terminate": ("kle", "terminate"),
    "kle_update": ("kle", "update"),
    "leave_terminate": ("leave", "terminate"),
    "leave_update": ("leave", "update"),
    "manager_terminate": ("manager", "terminate"),
    "manager_update": ("manager", "update"),
    "owner_terminate": ("owner", "terminate"),
    "owner_update": ("owner", "update"),
    "rolebinding_terminate": ("rolebinding", "terminate"),
    "rolebinding_update": ("rolebinding", "update"),
}

# What a mutator requires owned, read off its `input`.
# A mutator not listed here is never granted by ownership
OWNER_ENTITIES: dict[str, OwnerRule] = {
    # The unit or the person the address links to (exactly one is set)
    "address_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "addresses_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person or input.employee)
    ),
    # The unit of the association
    "association_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    # The employee itself
    "employee_create": lambda input: person(input.uuid),
    "employee_terminate": lambda input: person(input.uuid),
    "employee_update": lambda input: person(input.uuid),
    # The unit of the engagement
    "engagement_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "engagements_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person or input.employee)
    ),
    # The unit of the IT-association, whose update cannot name a person
    "itassociation_create": lambda input: org_unit_or_person(
        input.org_unit, input.person
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    "ituser_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    "itusers_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person)
    ),
    # The annotated unit
    "kle_create": lambda input: org_unit(input.org_unit),
    # The person on leave
    "leave_create": lambda input: person(input.person),
    # The unit of the manager
    "manager_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    "managers_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person)
    ),
    # The parent, or the unit itself and its new parent if it is being moved
    "org_unit_create": lambda input: org_unit(input.parent),
    "org_unit_terminate": lambda input: org_unit(input.uuid),
    "org_unit_update": lambda input: all_of(
        org_unit(input.uuid), check_parent(input.uuid, input.parent)
    ),
    # The unit or the person owned (exactly one is set)
    "owner_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    # The origin of the relation
    "related_units_update": lambda input: org_unit(input.origin),
    # The unit of the role-binding, if one is named
    "rolebinding_create": lambda input: org_unit(input.org_unit),
    "rolebindings_create": each(lambda input: org_unit(input.org_unit)),
    # The mutators whose rule is still branched on collection and operation
    **{
        mutator: partial(
            get_entities_graphql, collection=collection, permission_type=permission_type
        )
        for mutator, (collection, permission_type) in _TOUCHES.items()
    },
}
