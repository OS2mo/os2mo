# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The collections a policy may name, and the predicate selecting their objects.

Every collection maps to the resolver predicate that selects its matching
objects. Collections backed by real database tables reuse the resolvers' own
predicates; pseudo-collections (health, version, ...) have no database table
and so select everything (`true`).
"""

from collections.abc import Callable
from typing import get_args

from sqlalchemy import ColumnElement
from sqlalchemy import true

from mora.graphapi import resolvers
from mora.graphapi.permissions import Collections

# A predicate selecting a collection's objects, given an `MOInfo` and a filter
Predicate = Callable[..., ColumnElement]


def _everything(**kwargs: object) -> ColumnElement:
    """The predicate for a pseudo-collection: it selects everything."""
    return true()


# Real collections reuse their resolver predicate; pseudo-collections select all
COLLECTION_PREDICATES: dict[str, Predicate] = {
    "address": resolvers.address_predicate,
    "association": resolvers.association_predicate,
    "class": resolvers.class_predicate,
    "employee": resolvers.employee_predicate,
    "engagement": resolvers.engagement_predicate,
    "facet": resolvers.facet_predicate,
    "itsystem": resolvers.it_system_predicate,
    "ituser": resolvers.it_user_predicate,
    "kle": resolvers.kle_predicate,
    "leave": resolvers.leave_predicate,
    "manager": resolvers.manager_predicate,
    "org_unit": resolvers.organisation_unit_predicate,
    "owner": resolvers.owner_predicate,
    "related_unit": resolvers.related_unit_predicate,
    "rolebinding": resolvers.rolebinding_predicate,
    # Pseudo-collections: no database table, so nothing to filter
    "accesslog": _everything,
    "actor": _everything,
    "configuration": _everything,
    "event": _everything,
    "event_listener": _everything,
    "event_namespace": _everything,
    "file": _everything,
    "health": _everything,
    "org": _everything,
    "registration": _everything,
    "version": _everything,
}

# Every named collection must be registered exactly once
assert set(COLLECTION_PREDICATES) == set(get_args(Collections)), set(
    get_args(Collections)
) ^ set(COLLECTION_PREDICATES)


def collection_predicate(collection: Collections) -> Predicate:
    """The predicate selecting `collection`'s objects."""
    return COLLECTION_PREDICATES[collection]
