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
    all_fields=True,
    description="Input type for terminating organization units",
)
class OrganizationUnitTerminateInput:
    """Data representation of the input fields required to terminate an organization unit."""

    pass
