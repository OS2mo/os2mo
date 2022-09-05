# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from .models import AddressCreate
from .models import AddressTerminate
from .models import AddressVisibility
from .models import EmployeeCreate
from .models import EmployeeTerminate
from .models import EmployeeUpdate
from .models import EngagementTerminate
from .models import ITUserTerminate
from .models import Organisation
from .models import OrganisationUnitTerminate
from .models import Validity


@strawberry.experimental.pydantic.input(
    model=Validity,
    all_fields=True,
)
class ValidityInput:
    pass


@strawberry.experimental.pydantic.input(
    model=Organisation,
    all_fields=True,
)
class OrganizationInput:
    """input model for terminating organizations units."""

    pass


@strawberry.experimental.pydantic.input(
    model=AddressCreate,
    all_fields=True,
)
class AddressCreateInput:
    """input model for address creation."""

    pass


@strawberry.experimental.pydantic.input(
    model=AddressTerminate,
    all_fields=True,
)
class AddressTerminateInput:
    """input model for terminating addresses."""

    pass


@strawberry.experimental.pydantic.input(
    model=AddressVisibility,
    all_fields=True,
)
class AddressVisibilityInput:
    """input model for terminating addresses."""

    pass


@strawberry.experimental.pydantic.input(
    model=OrganisationUnitTerminate,
    all_fields=True,
)
class OrganizationUnitTerminateInput:
    """input model for terminating organizations units."""

    pass


@strawberry.experimental.pydantic.input(
    model=EngagementTerminate,
    all_fields=True,
)
class EngagementTerminateInput:
    """input model for terminating Engagements."""

    pass


@strawberry.experimental.pydantic.input(
    model=EmployeeCreate,
    all_fields=True,
)
class EmployeeCreateInput:
    """Input model for creating an employee."""

    pass


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

    pass


@strawberry.experimental.pydantic.input(
    model=ITUserTerminate,
    all_fields=True,
)
class ITUserTerminateInput:
    """input model for terminating IT-user."""

    pass
