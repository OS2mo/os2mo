# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from mora.graphapi.gmodels.base import RABase
from mora.graphapi.gmodels.mo._shared import EmployeeRef
from mora.graphapi.gmodels.mo._shared import OrgUnitRef


class Details(RABase):
    employee: EmployeeRef | None
    org_unit: OrgUnitRef | None
