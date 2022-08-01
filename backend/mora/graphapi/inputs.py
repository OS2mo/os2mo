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


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    description="Input type for terminating organization units",
    all_fields=True,
)
class OrganizationUnitTerminateInput:
    """Data representation of the input fields required to terminate an organization unit."""

    pass
    # uuid: strawberry.auto
    # from_date: strawberry.auto
    # to_date: strawberry.auto
    # trigger_less: strawberry.auto
