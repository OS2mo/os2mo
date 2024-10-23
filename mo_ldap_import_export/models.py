# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ramodels.mo.details.engagement import Engagement as RAEngagement
from ramodels.mo.employee import Employee as RAEmployee


class Employee(RAEmployee):
    pass


class Engagement(RAEngagement):
    pass
