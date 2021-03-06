# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from . import address
from . import association  # noqa
from . import cpr
from . import detail_reading
from . import detail_writing
from . import employee
from . import engagement  # noqa
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
from . import configuration
from .validation import validate

blueprints = (
    address.blueprint,
    cpr.blueprint,
    detail_reading.blueprint,
    detail_writing.blueprint,
    employee.blueprint,
    exports.blueprint,
    facet.blueprint,
    integration_data.blueprint,
    itsystem.blueprint,
    kle.blueprint,
    org.blueprint,
    orgunit.blueprint,
    related.blueprint,
    configuration.blueprint,
    validate.blueprint,
)
