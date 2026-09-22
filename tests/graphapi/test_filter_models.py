# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Test the pydantic filter models."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from mora.graphapi.filter_models import EmployeeFilter
from mora.graphapi.filter_models import OrganisationUnitFilter


def test_unknown_field_is_rejected() -> None:
    """Test that a mistyped filter field is rejected rather than dropped.

    A dropped field leaves a filter matching everything, and an access rule
    built on it granting everything.
    """
    with pytest.raises(ValidationError, match="extra fields not permitted"):
        EmployeeFilter(uuid=[uuid4()])


def test_nested_unknown_field_is_rejected() -> None:
    """Test that the same holds for a filter nested inside another."""
    with pytest.raises(ValidationError, match="extra fields not permitted"):
        OrganisationUnitFilter(ancestor={"uuid": [uuid4()]})
