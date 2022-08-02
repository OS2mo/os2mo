#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import strawberry

from .models import OrganisationUnitTerminate
from mora.graphapi.models import ITSystemWrite


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    all_fields=True,
)
class OrganizationUnitTerminateInput:
    """input model for terminating organizations units."""
    pass

# --------------------------------------------------------------------------------------
# Graphapi input models
# --------------------------------------------------------------------------------------


@strawberry.experimental.pydantic.input(model=ITSystemWrite)
class ITSystemInput:
    """Pydantic -> Strawberry model for class mutator."""

    user_key: strawberry.auto
    type_: strawberry.auto
    name: strawberry.auto
    system_type: strawberry.auto
