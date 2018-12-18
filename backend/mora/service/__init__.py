#
# Copyright (c) 2017-2018, Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from . import address
from . import association  # noqa
from . import cpr
from . import detail_reading
from . import detail_writing
from . import employee
from . import engagement  # noqa
from . import exports
from . import facet
from . import itsystem
from . import leave  # noqa
from . import manager  # noqa
from . import org
from . import orgunit
from . import related  # noqa
from . import role  # noqa

blueprints = (
    address.blueprint,
    cpr.blueprint,
    employee.blueprint,
    detail_reading.blueprint,
    detail_writing.blueprint,
    facet.blueprint,
    itsystem.blueprint,
    org.blueprint,
    orgunit.blueprint,
    exports.blueprint,
)
