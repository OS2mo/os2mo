# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from functools import partial

from mora.auth.keycloak.uuid_extractor import OwnerRule
from mora.auth.keycloak.uuid_extractor import get_entities_graphql
from mora.graphapi.permissions import CollectionPermissionType
from mora.graphapi.permissions import Collections

# The collection and operation each mutator touches
_TOUCHES: dict[str, tuple[Collections, CollectionPermissionType]] = {
    "address_create": ("address", "create"),
    "address_terminate": ("address", "terminate"),
    "address_update": ("address", "update"),
    "addresses_create": ("address", "create"),
    "association_create": ("association", "create"),
    "association_terminate": ("association", "terminate"),
    "association_update": ("association", "update"),
    "employee_create": ("employee", "create"),
    "employee_terminate": ("employee", "terminate"),
    "employee_update": ("employee", "update"),
    "engagement_create": ("engagement", "create"),
    "engagement_terminate": ("engagement", "terminate"),
    "engagement_update": ("engagement", "update"),
    "engagements_create": ("engagement", "create"),
    "engagements_update": ("engagement", "update"),
    "itassociation_create": ("association", "create"),
    "itassociation_terminate": ("association", "terminate"),
    "itassociation_update": ("association", "update"),
    "ituser_create": ("ituser", "create"),
    "ituser_terminate": ("ituser", "terminate"),
    "ituser_update": ("ituser", "update"),
    "itusers_create": ("ituser", "create"),
    "kle_create": ("kle", "create"),
    "kle_terminate": ("kle", "terminate"),
    "kle_update": ("kle", "update"),
    "leave_create": ("leave", "create"),
    "leave_terminate": ("leave", "terminate"),
    "leave_update": ("leave", "update"),
    "manager_create": ("manager", "create"),
    "manager_terminate": ("manager", "terminate"),
    "manager_update": ("manager", "update"),
    "managers_create": ("manager", "create"),
    "org_unit_create": ("org_unit", "create"),
    "org_unit_terminate": ("org_unit", "terminate"),
    "org_unit_update": ("org_unit", "update"),
    "owner_create": ("owner", "create"),
    "owner_terminate": ("owner", "terminate"),
    "owner_update": ("owner", "update"),
    "related_units_update": ("related_unit", "update"),
    "rolebinding_create": ("rolebinding", "create"),
    "rolebinding_terminate": ("rolebinding", "terminate"),
    "rolebinding_update": ("rolebinding", "update"),
    "rolebindings_create": ("rolebinding", "create"),
}

# What a mutator requires owned: the rule for its collection and operation.
# A mutator not listed here is never granted by ownership
OWNER_ENTITIES: dict[str, OwnerRule] = {
    mutator: partial(
        get_entities_graphql, collection=collection, permission_type=permission_type
    )
    for mutator, (collection, permission_type) in _TOUCHES.items()
}
