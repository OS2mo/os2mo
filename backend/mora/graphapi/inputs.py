#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import strawberry

from .models import EmployeeTermination


@strawberry.experimental.pydantic.input(
    model=EmployeeTermination,
    all_fields=True,
    description="Input type for terminating employees",
)
class EmployeeTerminationInput:
    """Data representation of the input fields required to terminate an employee."""

    pass
