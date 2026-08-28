# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import get_args

from mora.graphapi import resolvers
from mora.graphapi.collection_registry import COLLECTION_PREDICATES
from mora.graphapi.collection_registry import collection_predicate
from mora.graphapi.permissions import Collections


def test_every_collection_is_registered() -> None:
    """Every named collection maps to a predicate."""
    assert set(COLLECTION_PREDICATES) == set(get_args(Collections))


def test_collection_predicate() -> None:
    """The accessor returns the registered predicate."""
    assert collection_predicate("employee") is resolvers.employee_predicate
    # A pseudo-collection selects everything
    assert str(collection_predicate("health")()) == "true"
