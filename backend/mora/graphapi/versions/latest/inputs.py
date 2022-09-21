# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from .models import AddressTerminate
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate
from .models import EngagementTerminate
from .models import ITUserTerminate
from .models import Organisation
from .models import OrganisationUnit
from .models import OrganisationUnitTerminate
from .models import OrganisationUnitUpdate
from .models import Validity


# Various
# -------
@strawberry.experimental.pydantic.input(
    model=Validity,
    all_fields=True,
)
class ValidityInput:
    pass


# Root Organisation
# -----------------
@strawberry.experimental.pydantic.input(
    model=Organisation,
    all_fields=True,
)
class OrganisationInput:
    """input model for terminating organisation units."""

    pass


@strawberry.experimental.pydantic.input(
    model=OrganisationUnit,
    all_fields=True
)
class OrganisationUnitInput:
    """Input model for an organisation unit. """

    pass


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitUpdate,
    all_fields=True
)
class OrganisationUnitUpdateInput:
    """Input model for updating organisation units."""

    pass


# Addresses
# ---------
@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    all_fields=True,
)
class OrganisationUnitTerminateInput:
    """input model for terminating organisations units."""

    pass


@strawberry.experimental.pydantic.input(
    model=AddressTerminate,
    all_fields=True,
)
class AddressTerminateInput:
    """input model for terminating addresses."""


# Associations
# ------------

# Classes
# -------

# Employees
# ---------
@strawberry.experimental.pydantic.input(
    model=EmployeeCreate,
    all_fields=True,
)
class EmployeeCreateInput:
    """Input model for creating an employee."""


@strawberry.experimental.pydantic.input(
    model=EmployeeTerminate,
    all_fields=True,
)
class EmployeeTerminateInput:
    pass


@strawberry.experimental.pydantic.input(
    model=EmployeeUpdate,
    all_fields=True,
)
class EmployeeUpdateInput:
    """Input model for updating an employee."""


# Engagements
# -----------
@strawberry.experimental.pydantic.input(
    model=EngagementTerminate,
    all_fields=True,
)
class EngagementTerminateInput:
    """input model for terminating Engagements."""


# EngagementsAssociations
# -----------------------

# Facets
# ------

# ITSystems
# ---------

# ITUsers
# -------
@strawberry.experimental.pydantic.input(
    model=ITUserTerminate,
    all_fields=True,
)
class ITUserTerminateInput:
    """input model for terminating IT-user."""


# KLEs
# ----

# Leave
# -----

# Managers
# --------

# Organisational Units
# --------------------
@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    all_fields=True,
)
class OrganizationUnitTerminateInput:
    """input model for terminating organizations units."""

# Related Units
# -------------

# Roles
# -----

# Health
# ------

# Files
# -----
