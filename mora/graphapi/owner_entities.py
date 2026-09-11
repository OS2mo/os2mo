# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from functools import partial

from mora.auth.keycloak.uuid_extractor import OwnerRule
from mora.auth.keycloak.uuid_extractor import and_or_none
from mora.auth.keycloak.uuid_extractor import check_parent
from mora.auth.keycloak.uuid_extractor import detail
from mora.auth.keycloak.uuid_extractor import get_entities_graphql
from mora.auth.keycloak.uuid_extractor import org_unit
from mora.auth.keycloak.uuid_extractor import org_unit_or_person
from mora.auth.keycloak.uuid_extractor import person
from mora.graphapi.permissions import CollectionPermissionType
from mora.graphapi.permissions import Collections

# The collection and operation each mutator touches
_TOUCHES: dict[str, tuple[Collections, CollectionPermissionType]] = {
    "address_update": ("address", "update"),
    "association_update": ("association", "update"),
    "engagement_update": ("engagement", "update"),
    "engagements_update": ("engagement", "update"),
    "itassociation_update": ("association", "update"),
    "ituser_update": ("ituser", "update"),
    "kle_update": ("kle", "update"),
    "leave_update": ("leave", "update"),
    "manager_update": ("manager", "update"),
    "owner_update": ("owner", "update"),
    "rolebinding_update": ("rolebinding", "update"),
}

# The rule for each collection's detail
address = partial(detail, collection="address")
association = partial(detail, collection="association")
engagement = partial(detail, collection="engagement")
ituser = partial(detail, collection="ituser")
kle = partial(detail, collection="kle")
leave = partial(detail, collection="leave")
manager = partial(detail, collection="manager")
owner = partial(detail, collection="owner")
rolebinding = partial(detail, collection="rolebinding")


# What a mutator requires owned, read off its arguments.
# A mutator not listed here is never granted by ownership
OWNER_ENTITIES: dict[str, OwnerRule] = {
    # The unit or the person the address links to (exactly one is set)
    "address_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings,
        version,
        token,
        arguments["input"].org_unit,
        arguments["input"].person or arguments["input"].employee,
    ),
    "address_terminate": lambda settings, version, token, arguments: address(
        settings, version, token, arguments["input"].uuid
    ),
    "addresses_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(
                settings, version, token, input.org_unit, input.person or input.employee
            )
            for input in arguments["input"]
        )
    ),
    # The unit of the association
    "association_create": lambda settings,
    version,
    token,
    arguments: org_unit_or_person(
        settings,
        version,
        token,
        arguments["input"].org_unit,
        arguments["input"].person or arguments["input"].employee,
    ),
    "association_terminate": lambda settings, version, token, arguments: association(
        settings, version, token, arguments["input"].uuid
    ),
    # The employee itself
    "employee_create": lambda settings, version, token, arguments: person(
        settings, version, token, arguments["input"].uuid
    ),
    "employee_terminate": lambda settings, version, token, arguments: person(
        settings, version, token, arguments["input"].uuid
    ),
    "employee_update": lambda settings, version, token, arguments: person(
        settings, version, token, arguments["input"].uuid
    ),
    # The unit of the engagement
    "engagement_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings,
        version,
        token,
        arguments["input"].org_unit,
        arguments["input"].person or arguments["input"].employee,
    ),
    "engagement_terminate": lambda settings, version, token, arguments: engagement(
        settings, version, token, arguments["input"].uuid
    ),
    "engagements_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(
                settings, version, token, input.org_unit, input.person or input.employee
            )
            for input in arguments["input"]
        )
    ),
    # The unit of the IT-association, whose update cannot name a person
    "itassociation_create": lambda settings,
    version,
    token,
    arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "itassociation_terminate": lambda settings, version, token, arguments: association(
        settings, version, token, arguments["input"].uuid
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    "ituser_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "ituser_terminate": lambda settings, version, token, arguments: ituser(
        settings, version, token, arguments["input"].uuid
    ),
    "itusers_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(settings, version, token, input.org_unit, input.person)
            for input in arguments["input"]
        )
    ),
    # The annotated unit
    "kle_create": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].org_unit
    ),
    "kle_terminate": lambda settings, version, token, arguments: kle(
        settings, version, token, arguments["input"].uuid
    ),
    # The person on leave
    "leave_create": lambda settings, version, token, arguments: person(
        settings, version, token, arguments["input"].person
    ),
    "leave_terminate": lambda settings, version, token, arguments: leave(
        settings, version, token, arguments["input"].uuid
    ),
    # The unit of the manager
    "manager_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "manager_terminate": lambda settings, version, token, arguments: manager(
        settings, version, token, arguments["input"].uuid
    ),
    "managers_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit_or_person(settings, version, token, input.org_unit, input.person)
            for input in arguments["input"]
        )
    ),
    # The parent, or the unit itself and its new parent if it is being moved
    "org_unit_create": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].parent
    ),
    "org_unit_terminate": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].uuid
    ),
    "org_unit_update": lambda settings, version, token, arguments: and_or_none(
        org_unit(settings, version, token, arguments["input"].uuid),
        check_parent(
            settings, version, token, arguments["input"].uuid, arguments["input"].parent
        ),
    ),
    # The unit or the person owned (exactly one is set)
    "owner_create": lambda settings, version, token, arguments: org_unit_or_person(
        settings, version, token, arguments["input"].org_unit, arguments["input"].person
    ),
    "owner_terminate": lambda settings, version, token, arguments: owner(
        settings, version, token, arguments["input"].uuid
    ),
    # Related units have a single `origin` field and a list of
    # `destination`s. Originally we required ownership of both the
    # origin and destinations, but that's not compatible with the old
    # service-api owner calculation
    "related_units_update": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].origin
    ),
    # The unit of the role-binding, if one is named
    "rolebinding_create": lambda settings, version, token, arguments: org_unit(
        settings, version, token, arguments["input"].org_unit
    ),
    "rolebinding_terminate": lambda settings, version, token, arguments: rolebinding(
        settings, version, token, arguments["input"].uuid
    ),
    "rolebindings_create": lambda settings, version, token, arguments: and_or_none(
        *(
            org_unit(settings, version, token, input.org_unit)
            for input in arguments["input"]
        )
    ),
    # The mutators whose rule is still branched on collection and operation
    **{
        mutator: partial(
            get_entities_graphql, collection=collection, permission_type=permission_type
        )
        for mutator, (collection, permission_type) in _TOUCHES.items()
    },
}
