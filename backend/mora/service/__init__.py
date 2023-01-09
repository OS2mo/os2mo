# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from . import address
from . import association
from . import configuration
from . import cpr
from . import detail_reading
from . import detail_writing
from . import employee
from . import engagement
from . import engagement_association
from . import exports
from . import facet
from . import insight
from . import itsystem
from . import kle
from . import leave
from . import manager
from . import org
from . import orgunit
from . import owner
from . import related
from . import role
from . import shimmed
from .validation import validate

__all__ = [
    "address",
    "association",
    "configuration",
    "cpr",
    "detail_reading",
    "detail_writing",
    "employee",
    "engagement",
    "engagement_association",
    "exports",
    "facet",
    "insight",
    "itsystem",
    "kle",
    "leave",
    "manager",
    "org",
    "orgunit",
    "owner",
    "related",
    "role",
    "shimmed",
    "validate",
]

routers = {
    "Address": address.router,
    "CPR": cpr.router,
    "DetailReading": detail_reading.router,
    "DetailWriting": detail_writing.router,
    "Employee": employee.router,
    "Facet": facet.router,
    "Insight": insight.router,
    "ITSystem": itsystem.router,
    "KLE": kle.router,
    "Organisation": org.router,
    "OrganisationUnit": orgunit.router,
    "Related": related.router,
    "Configuration": configuration.router,
    "Validate": validate.router,
}
no_auth_routers = {
    "Exports": exports.router,
}
