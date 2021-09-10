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
from . import itsystem
from . import kle
from . import leave  # noqa
from . import manager  # noqa
from . import owner  # noqa
from . import org
from . import orgunit
from . import related  # noqa
from . import role  # noqa
from .validation import validate

routers = {
    "Address": address.router,
    "CPR": cpr.router,
    "DetailReading": detail_reading.router,
    "DetailWriting": detail_writing.router,
    "Employee": employee.router,
    "Exports": exports.router,
    "Facet": facet.router,
    "ITSystem": itsystem.router,
    "KLE": kle.router,
    "Organisation": org.router,
    "OrganisationUnit": orgunit.router,
    "Related": related.router,
    "Configuration": configuration.router,
    "Validate": validate.router,
}
