#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from mora.graphapi.inputs import EmployeeTerminationInput
from mora.graphapi.models import Employee


async def terminate_employee(terminationInput: EmployeeTerminationInput) -> Employee:
    pass
