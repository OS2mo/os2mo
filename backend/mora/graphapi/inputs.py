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
)
class OrganizationUnitTerminateInput:
    """Data representation of the input fields required to terminate an organization unit.

    OBS: We specify the fields manually and set their type using strawberry.auto in
    order for our pre-commit hook "mypy" to pass - if using this class without
    specifying the fields manually errors like the following will occur:
    "error: "OrganizationUnitTerminateInput" has no attribute "uuid"".
    """

    uuid: strawberry.auto
    from_date: strawberry.auto
    to_date: strawberry.auto
