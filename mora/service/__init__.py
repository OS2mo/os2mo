#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import address
from . import employee
from . import engagement
from . import facet
from . import itsystem
from . import org

blueprints = (
    address.blueprint,
    employee.blueprint,
    engagement.blueprint,
    facet.blueprint,
    itsystem.blueprint,
    org.blueprint,
)
