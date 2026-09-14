# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import get_type_hints
from uuid import UUID

from sqlalchemy import ColumnElement
from sqlalchemy import exists
from sqlalchemy import or_
from structlog import get_logger

from mora.auth.keycloak.models import Token
from mora.config import Settings
from mora.graphapi import resolvers
from mora.graphapi.filters import EmployeeFilter
from mora.graphapi.filters import ITSystemFilter
from mora.graphapi.filters import ITUserFilter
from mora.graphapi.filters import OrganisationUnitFilter
from mora.graphapi.filters import OwnerFilter
from mora.graphapi.permissions import Collections
from mora.graphapi.resolvers import employee_predicate
from mora.graphapi.resolvers import organisation_unit_predicate
from mora.graphapi.version import Version

logger = get_logger()


def _actor_filter(settings: Settings, token: Token) -> EmployeeFilter:
    """The employee filter matching the calling actor.

    With `KEYCLOAK_RBAC_AUTHORITATIVE_IT_SYSTEM_FOR_OWNERS` configured, the
    actor is the employee holding the token's uuid as an external id in that
    IT system; otherwise the employee with the token's uuid itself.
    """
    # A token with no uuid never gets this far, see `owner_policy`
    assert token.uuid is not None
    it_system = settings.keycloak_rbac_authoritative_it_system_for_owners
    if it_system is not None:
        return EmployeeFilter(
            ituser=ITUserFilter(
                itsystem=ITSystemFilter(uuids=[it_system]),
                external_ids=[str(token.uuid)],
            )
        )
    return EmployeeFilter(uuids=[token.uuid])


def _is_owner_org_unit(
    settings: Settings,
    version: Version,
    actor: EmployeeFilter,
    entity_uuid: UUID | None,
) -> ColumnElement | None:
    """Check org-unit ownership via the GraphQL org-unit owner filter.

    Owning any ancestor also grants ownership: the `descendant` filter matches
    the unit together with all of its ancestors. No org unit named is nothing
    to own, and thus nothing to check.
    """
    if entity_uuid is None:
        return None
    predicate = organisation_unit_predicate(
        settings=settings,
        version=version,
        filter=OrganisationUnitFilter(
            descendant=OrganisationUnitFilter(uuids=[entity_uuid]),
            owner=OwnerFilter(owner=actor),
        ),
    )
    return exists().where(predicate)


def _is_owner_employee(
    settings: Settings,
    version: Version,
    actor: EmployeeFilter,
    entity_uuid: UUID | None,
) -> ColumnElement | None:
    """Check employee ownership via the GraphQL employee owner filter.

    No employee named is nothing to own, and thus nothing to check.
    """
    if entity_uuid is None:
        return None
    predicate = employee_predicate(
        settings=settings,
        version=version,
        filter=EmployeeFilter(
            uuids=[entity_uuid],
            owner=OwnerFilter(owner=actor),
        ),
    )
    return exists().where(predicate)


def _is_owner_detail(
    settings: Settings,
    version: Version,
    actor: EmployeeFilter,
    collection: Collections,
    entity_uuid: UUID,
) -> ColumnElement:
    """Check detail ownership via the GraphQL filter of its own collection."""
    # The detail collections, each the predicate selecting its objects
    predicate = {
        "address": resolvers.address_predicate,
        "association": resolvers.association_predicate,
        "engagement": resolvers.engagement_predicate,
        "ituser": resolvers.it_user_predicate,
        "kle": resolvers.kle_predicate,
        "leave": resolvers.leave_predicate,
        "manager": resolvers.manager_predicate,
        "owner": resolvers.owner_predicate,
        "rolebinding": resolvers.rolebinding_predicate,
    }[collection]
    filter = get_type_hints(predicate)["filter"]
    owner = OwnerFilter(owner=actor)
    # A detail is owned by whoever owns the org unit or the person it links.
    # Every collection can name an org unit, only some can name a person
    via_org_unit = exists().where(
        predicate(
            settings=settings,
            version=version,
            filter=filter(
                uuids=[entity_uuid],
                org_unit=OrganisationUnitFilter(
                    ancestor=OrganisationUnitFilter(owner=owner)
                ),
            ),
        )
    )
    if "employee" not in get_type_hints(filter):
        return via_org_unit
    via_person = exists().where(
        predicate(
            settings=settings,
            version=version,
            filter=filter(uuids=[entity_uuid], employee=EmployeeFilter(owner=owner)),
        )
    )
    return or_(via_org_unit, via_person)
