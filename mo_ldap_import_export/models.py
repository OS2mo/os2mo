# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from ramodels.mo.details.address import Address as RAAddress
from ramodels.mo.details.engagement import Engagement as RAEngagement
from ramodels.mo.details.it_system import ITUser as RAITUser
from ramodels.mo.employee import Employee as RAEmployee


class Address(RAAddress):
    pass


class Employee(RAEmployee):
    pass


class Engagement(RAEngagement):
    pass


class ITUser(RAITUser):
    pass
