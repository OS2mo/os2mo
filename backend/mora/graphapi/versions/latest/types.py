# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from .models import Address as AddressModel
from .models import Association as AssociationModel
from .models import Employee as EmployeeModel
from .models import Engagement as EngagementModel
from .models import OrganisationUnit as OrganisationUnitModel
from mora.util import CPR
from ramodels.mo._shared import UUIDBase

# Various
# -------
# https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
CPRType = strawberry.scalar(
    CPR,
    serialize=str,
    parse_value=CPR.validate,
)


# Addresses
# ---------
@strawberry.experimental.pydantic.type(
    model=AddressModel,
    all_fields=True,
)
class AddressTerminateType:
    """GraphQL type for/of an address (detail)."""


# Associations
# ------------
@strawberry.experimental.pydantic.type(
    model=AssociationModel,
    all_fields=True,
)
class AssociationType:
    """GraphQL type for an association."""


# Classes
# -------


@strawberry.experimental.pydantic.type(
    model=UUIDBase,
    all_fields=True,
)
class ClassCreateType:
    """GraphQL type for a Class."""


# Employees
# ---------
@strawberry.experimental.pydantic.type(
    model=EmployeeModel,
    all_fields=True,
)
class EmployeeType:
    pass


# Engagements
# -----------
@strawberry.experimental.pydantic.type(
    model=EngagementModel,
    all_fields=True,
)
class EngagementTerminateType:
    """GraphQL type for an engagement."""


@strawberry.experimental.pydantic.type(
    model=EngagementModel,
    all_fields=True,
)
class EngagementType:
    """GraphQL type for an engagement."""


# EngagementsAssociations
# -----------------------

# Facets
# ------
@strawberry.experimental.pydantic.type(
    model=UUIDBase,
    all_fields=True,
)
class FacetType:
    """GraphQL type for an creating facets."""


# ITSystems
# ---------

# ITUsers
# -------
@strawberry.experimental.pydantic.type(
    model=UUIDBase,
    all_fields=True,
)
class ITUserType:
    """Generic UUID model for return types."""


# KLEs
# ----

# Leave
# -----

# Managers
# --------

# Root Organisation
# -----------------

# Organisational Units
# --------------------
@strawberry.experimental.pydantic.type(
    model=OrganisationUnitModel,
    all_fields=True,
)
class OrganizationUnit:
    """GraphQL type for/of a organization unit."""


# Related Units
# -------------

# Roles
# -----
