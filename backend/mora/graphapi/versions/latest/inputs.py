# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import strawberry

from .models import AddressCreate
from .models import AddressTerminate
from .models import AddressUpdate
from .models import AssociationCreate
from .models import AssociationTerminate
from .models import AssociationUpdate
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate
from .models import EngagementCreate
from .models import EngagementTerminate
from .models import EngagementUpdate
from .models import ITAssociationCreate
from .models import ITAssociationTerminate
from .models import ITAssociationUpdate
from .models import ITSystemCreate
from .models import ITSystemTerminate
from .models import ITSystemUpdate
from .models import ITUserCreate
from .models import ITUserTerminate
from .models import ITUserUpdate
from .models import KLECreate
from .models import KLETerminate
from .models import KLEUpdate
from .models import LeaveCreate
from .models import LeaveTerminate
from .models import LeaveUpdate
from .models import ManagerCreate
from .models import ManagerTerminate
from .models import ManagerUpdate
from .models import Organisation
from .models import OrganisationUnitCreate
from .models import OrganisationUnitTerminate
from .models import OrganisationUnitUpdate
from .models import RoleCreate
from .models import RoleTerminate
from .models import RoleUpdate
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
class OrganisationInput:
    """input model for terminating organisation units."""


# Addresses
# ---------
@strawberry.experimental.pydantic.input(
    model=AddressCreate,
    all_fields=True,
)
class AddressCreateInput:
    """input model for creating addresses."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=AddressTerminate,
    all_fields=True,
)
class AddressTerminateInput:
    """input model for terminating addresses."""


@strawberry.experimental.pydantic.input(
    model=AddressUpdate,
    all_fields=True,
)
class AddressUpdateInput:
    """input model for updating addresses."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


# Associations
# ------------
@strawberry.experimental.pydantic.input(
    model=AssociationCreate,
    all_fields=True,
)
class AssociationCreateInput:
    """input model for creating associations."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=AssociationUpdate,
    all_fields=True,
)
class AssociationUpdateInput:
    """input model for updating associations."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=AssociationTerminate,
    all_fields=True,
)
class AssociationTerminateInput:
    """input model for terminating associations."""


# Employees
# ---------
@strawberry.experimental.pydantic.input(
    model=EmployeeCreate,
    all_fields=True,
)
class EmployeeCreateInput:
    """Input model for creating an employee."""


@strawberry.experimental.pydantic.input(
    model=EmployeeUpdate,
    all_fields=True,
)
class EmployeeUpdateInput:
    """Input model for updating an employee."""


@strawberry.experimental.pydantic.input(
    model=EmployeeTerminate,
    all_fields=True,
)
class EmployeeTerminateInput:
    pass


# Engagements
# -----------
@strawberry.experimental.pydantic.input(
    model=EngagementTerminate,
    all_fields=True,
)
class EngagementTerminateInput:
    """input model for terminating Engagements."""


@strawberry.experimental.pydantic.input(
    model=EngagementCreate,
    all_fields=True,
)
class EngagementCreateInput:
    """input model for creating engagements."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=EngagementUpdate,
    all_fields=True,
)
class EngagementUpdateInput:
    """input model for updating Engagements."""

    employee: UUID | None = strawberry.field(
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo."
    )


# EngagementsAssociations
# -----------------------


# ITAssociations
# ---------
@strawberry.experimental.pydantic.input(
    model=ITAssociationCreate,
    all_fields=True,
)
class ITAssociationCreateInput:
    """input model for creating IT-associations."""


@strawberry.experimental.pydantic.input(
    model=ITAssociationUpdate,
    all_fields=True,
)
class ITAssociationUpdateInput:
    """input model for updating IT-associations."""


@strawberry.experimental.pydantic.input(
    model=ITAssociationTerminate,
    all_fields=True,
)
class ITAssociationTerminateInput:
    """input model for terminating IT-associations."""


# ITSystems
# ---------
@strawberry.experimental.pydantic.input(
    model=ITSystemCreate,
    all_fields=True,
)
class ITSystemCreateInput:
    """input model for creating ITSystems."""


@strawberry.experimental.pydantic.input(
    model=ITSystemUpdate,
    all_fields=True,
)
class ITSystemUpdateInput:
    """Input model for updating ITSystems."""


@strawberry.experimental.pydantic.input(
    model=ITSystemTerminate,
    all_fields=True,
)
class ITSystemTerminateInput:
    """Input model for terminating ITSystems."""


# ITUsers
# -------
@strawberry.experimental.pydantic.input(
    model=ITUserCreate,
    all_fields=True,
)
class ITUserCreateInput:
    """input model for creating IT-Users."""


@strawberry.experimental.pydantic.input(
    model=ITUserUpdate,
    all_fields=True,
)
class ITUserUpdateInput:
    """input model for creating IT-Users."""


@strawberry.experimental.pydantic.input(
    model=ITUserTerminate,
    all_fields=True,
)
class ITUserTerminateInput:
    """input model for terminating IT-user."""


# KLEs
# ----


@strawberry.experimental.pydantic.input(
    model=KLECreate,
    all_fields=True,
)
class KLECreateInput:
    """Input model for creating a KLE annotation."""


@strawberry.experimental.pydantic.input(
    model=KLEUpdate,
    all_fields=True,
)
class KLEUpdateInput:
    """Input model for updating a KLE annotation."""


@strawberry.experimental.pydantic.input(
    model=KLETerminate,
    all_fields=True,
)
class KLETerminateInput:
    """Input model for terminating a KLE annotation."""


# Leave
# -----
@strawberry.experimental.pydantic.input(
    model=LeaveCreate,
    all_fields=True,
)
class LeaveCreateInput:
    """Input model for creating a leave."""


@strawberry.experimental.pydantic.input(
    model=LeaveUpdate,
    all_fields=True,
)
class LeaveUpdateInput:
    """Input model for updating a leave."""


@strawberry.experimental.pydantic.input(
    model=LeaveTerminate,
    all_fields=True,
)
class LeaveTerminateInput:
    """Input model for terminating a leave."""


# Managers
# --------


@strawberry.experimental.pydantic.input(
    model=ManagerCreate,
    all_fields=True,
)
class ManagerCreateInput:
    """Input model for creating a manager."""


@strawberry.experimental.pydantic.input(
    model=ManagerUpdate,
    all_fields=True,
)
class ManagerUpdateInput:
    """Input model for updating a manager."""


@strawberry.experimental.pydantic.input(
    model=ManagerTerminate,
    all_fields=True,
)
class ManagerTerminateInput:
    """Input model for terminating a manager."""


# Organisational Units
# --------------------
@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    all_fields=True,
)
class OrganisationUnitTerminateInput:
    """Input model for terminating organisation units."""


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitCreate,
    all_fields=True,
)
class OrganisationUnitCreateInput:
    """Input model for creating organisation units."""


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitUpdate,
    all_fields=True,
)
class OrganisationUnitUpdateInput:
    """Input model for updating organisation units."""


# Related Units
# -------------


# Roles
# -----
@strawberry.experimental.pydantic.input(
    model=RoleCreate,
    all_fields=True,
)
class RoleCreateInput:
    """Input model for creating roles."""


@strawberry.experimental.pydantic.input(
    model=RoleUpdate,
    all_fields=True,
)
class RoleUpdateInput:
    """Input model for updating roles."""


@strawberry.experimental.pydantic.input(
    model=RoleTerminate,
    all_fields=True,
)
class RoleTerminateInput:
    """Input model for terminating roles."""


# Health
# ------

# Files
# -----
