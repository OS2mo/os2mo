#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import strawberry

from .models import AddressTerminate
from .models import EngagementTerminate
from .models import OrganisationUnitTerminate


@strawberry.experimental.pydantic.input(
    model=AddressTerminate,
    all_fields=True,
)
class AddressTerminateInput:
    """input model for terminating addresses."""

    pass


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    all_fields=True,
)
class OrganizationUnitTerminateInput:
    """input model for terminating organizations units."""

    pass


@strawberry.experimental.pydantic.input(
    model=EngagementTerminate,
    all_fields=True,
)
class EngagementTerminateInput:
    """input model for terminating Engagements."""

    pass
