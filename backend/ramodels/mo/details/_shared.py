# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ramodels.base import RABase
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import OrgUnitRef


class Details(RABase):
    employee: EmployeeRef | None
    org_unit: OrgUnitRef | None
