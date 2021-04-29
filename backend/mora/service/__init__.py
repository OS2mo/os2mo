# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from . import address
from . import association  # noqa
from . import configuration
from . import cpr
from . import detail_reading
from . import detail_writing
from . import employee
from . import engagement  # noqa
from . import engagement_association  # noqa
from . import exports
from . import facet
from . import integration_data
from . import itsystem
from . import kle
from . import leave  # noqa
from . import manager  # noqa
from . import org
from . import orgunit
from . import related  # noqa
from . import role  # noqa
from .validation import validate

routers = (
    address.router,
    cpr.router,
    detail_reading.router,
    detail_writing.router,
    employee.router,
    exports.router,
    facet.router,
    integration_data.router,
    itsystem.router,
    kle.router,
    org.router,
    orgunit.router,
    related.router,
    configuration.router,
    validate.router,
)
