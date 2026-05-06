# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# TODO: Consider what auditing is still required from shimmed functions
from . import address
from . import association
from . import cpr
from . import detail_reading
from . import detail_writing
from . import employee
from . import engagement
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
    "cpr",
    "detail_reading",
    "detail_writing",
    "employee",
    "engagement",
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
    "Validate": validate.router,
}
no_auth_routers = {
    "Exports": exports.router,
}
