# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from .models import AddressTerminate
from .models import ClassCreate
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate
from .models import EngagementTerminate
from .models import ITUserTerminate
from .models import Organisation
from .models import OrganisationUnitCreate
from .models import OrganisationUnitTerminate
from .models import Validity
from ramodels.mo import Validity as RAValidity


# Various
# -------
@strawberry.experimental.pydantic.input(
    model=Validity,
    all_fields=True,
)
class ValidityInput:
    pass


@strawberry.experimental.pydantic.input(
    model=RAValidity,
    all_fields=True,
)
class RAValidityInput:
    pass


# Root Organisation
# -----------------
@strawberry.experimental.pydantic.input(
    model=Organisation,
    all_fields=True,
)
class OrganizationInput:
    """input model for terminating organizations units."""


# Addresses
# ---------
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
@strawberry.experimental.pydantic.input(
    model=ClassCreate,
    all_fields=True,
)
class ClassCreateInput:
    """Input model for creating a mo-class."""


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


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitCreate,
    all_fields=True,
)
class OrganizationUnitCreateInput:
    """input model for creating org-units."""


# Related Units
# -------------

# Roles
# -----

# Health
# ------

# Files
# -----
