# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Owner resolution map."""

from functools import partial

from mora.auth.keycloak.uuid_extractor import OwnerRule
from mora.auth.keycloak.uuid_extractor import all_of
from mora.auth.keycloak.uuid_extractor import check_parent
from mora.auth.keycloak.uuid_extractor import detail
from mora.auth.keycloak.uuid_extractor import each
from mora.auth.keycloak.uuid_extractor import org_unit
from mora.auth.keycloak.uuid_extractor import org_unit_or_person
from mora.auth.keycloak.uuid_extractor import person

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


# What a mutator requires owned, read off its `input`.
# A mutator not listed here is never granted by ownership
OWNER_ENTITIES: dict[str, OwnerRule] = {
    # The unit or the person the address links to (exactly one is set)
    "address_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "address_terminate": lambda input: address(input.uuid),
    "address_update": lambda input: all_of(
        address(input.uuid),
        org_unit_or_person(input.org_unit, input.person or input.employee),
    ),
    "addresses_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person or input.employee)
    ),
    # The unit of the association
    "association_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "association_terminate": lambda input: association(input.uuid),
    "association_update": lambda input: all_of(
        association(input.uuid),
        org_unit_or_person(input.org_unit, input.person or input.employee),
    ),
    # The employee itself
    "employee_create": lambda input: person(input.uuid),
    "employee_terminate": lambda input: person(input.uuid),
    "employee_update": lambda input: person(input.uuid),
    # The unit of the engagement
    "engagement_create": lambda input: org_unit_or_person(
        input.org_unit, input.person or input.employee
    ),
    "engagement_terminate": lambda input: engagement(input.uuid),
    "engagement_update": lambda input: all_of(
        engagement(input.uuid),
        org_unit_or_person(input.org_unit, input.person or input.employee),
    ),
    "engagements_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person or input.employee)
    ),
    "engagements_update": each(
        lambda input: all_of(
            engagement(input.uuid),
            org_unit_or_person(input.org_unit, input.person or input.employee),
        )
    ),
    # The unit of the IT-association, whose update cannot name a person
    "itassociation_create": lambda input: org_unit_or_person(
        input.org_unit, input.person
    ),
    "itassociation_terminate": lambda input: association(input.uuid),
    "itassociation_update": lambda input: all_of(
        association(input.uuid), org_unit(input.org_unit)
    ),
    # The unit or the person the IT-user belongs to (exactly one is set)
    "ituser_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    "ituser_terminate": lambda input: ituser(input.uuid),
    "ituser_update": lambda input: all_of(
        ituser(input.uuid), org_unit_or_person(input.org_unit, input.person)
    ),
    "itusers_create": each(
        lambda input: org_unit_or_person(input.org_unit, input.person)
    ),
    # The annotated unit
    "kle_create": lambda input: org_unit(input.org_unit),
    "kle_terminate": lambda input: kle(input.uuid),
    "kle_update": lambda input: all_of(kle(input.uuid), org_unit(input.org_unit)),
    # The person on leave
    "leave_create": lambda input: person(input.person),
    "leave_terminate": lambda input: leave(input.uuid),
    "leave_update": lambda input: all_of(leave(input.uuid), person(input.person)),
    # The unit of the manager
    "manager_create": lambda input: org_unit_or_person(input.org_unit, input.person),
    "manager_terminate": lambda input: manager(input.uuid),
    "manager_update": lambda input: all_of(
        manager(input.uuid), org_unit_or_person(input.org_unit, input.person)
    ),
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
    "owner_terminate": lambda input: owner(input.uuid),
    "owner_update": lambda input: all_of(
        owner(input.uuid), org_unit_or_person(input.org_unit, input.person)
    ),
    # The origin of the relation
    "related_units_update": lambda input: org_unit(input.origin),
    # The unit of the role-binding, if one is named
    "rolebinding_create": lambda input: org_unit(input.org_unit),
    "rolebinding_terminate": lambda input: rolebinding(input.uuid),
    "rolebinding_update": lambda input: all_of(
        rolebinding(input.uuid), org_unit(input.org_unit)
    ),
    "rolebindings_create": each(lambda input: org_unit(input.org_unit)),
}
