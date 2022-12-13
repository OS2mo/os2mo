# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import json
from base64 import b64decode
from base64 import b64encode
from typing import NewType
from uuid import UUID

import strawberry

from .models import Address as AddressModel
from .models import AddressCreateResponse
from .models import Association as AssociationModel
from .models import Employee as EmployeeModel
from .models import EmployeeUpdateResponse
from .models import Engagement as EngagementModel
from mora.util import CPR

# Various
# -------
# https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
CPRType = strawberry.scalar(
    CPR,
    serialize=str,
    parse_value=CPR.validate,
)

Cursor = strawberry.scalar(
    NewType("Cursor", str),
    serialize=lambda v: b64encode(json.dumps(v).encode("ascii")).decode("ascii"),
    parse_value=lambda v: int(b64decode(v)),
)


@strawberry.type
class UUIDReturn:
    uuid: UUID


# Addresses
# ---------
@strawberry.experimental.pydantic.type(
    model=AddressModel,
    all_fields=True,
)
class AddressType:
    """GraphQL type for/of an address (detail)."""


@strawberry.experimental.pydantic.type(
    model=AddressCreateResponse,
    all_fields=True,
)
class AddressCreateType:
    """GraphQL response type for address creation."""


@strawberry.experimental.pydantic.type(
    model=AddressModel,
    all_fields=True,
)
class AddressTerminateType:
    """GraphQL response type for address termination."""


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

# ITSystems
# ---------

# ITUsers
# -------

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

# Related Units
# -------------

# Roles
# -----


@strawberry.experimental.pydantic.type(
    model=EmployeeUpdateResponse,
    all_fields=True,
)
class EmployeeUpdateResponseType:
    pass
