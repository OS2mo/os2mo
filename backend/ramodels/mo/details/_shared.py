# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Optional

from ramodels.base import RABase
from ramodels.mo._shared import EmployeeRef
from ramodels.mo._shared import OrgUnitRef


class Details(RABase):
    employee: Optional[EmployeeRef]
    org_unit: Optional[OrgUnitRef]
