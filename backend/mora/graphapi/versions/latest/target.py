# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from strawberry.types import Info

from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationUnitRead
from mora.graphapi.gmodels.mo.details import AssociationRead
from mora.graphapi.gmodels.mo.details import EngagementRead
from mora.graphapi.gmodels.mo.details import ITSystemRead
from mora.graphapi.gmodels.mo.details import ITUserRead
from mora.graphapi.gmodels.mo.details import KLERead
from mora.graphapi.gmodels.mo.details import LeaveRead
from mora.graphapi.gmodels.mo.details import ManagerRead
from mora.graphapi.gmodels.mo.details import OwnerRead
from mora.graphapi.gmodels.mo.details import RelatedUnitRead

from .models import AddressRead
from .models import ClassRead
from .models import FacetRead
from .models import RoleBindingRead
from .response import Response
from .schema import MOBaseType


async def uuid_to_target(uuid: UUID, model: str, info: Info) -> Response[MOBaseType]:
    model2class = {
        "address": AddressRead,
        "association": AssociationRead,
        "class": ClassRead,
        "employee": EmployeeRead,
        "engagement": EngagementRead,
        "facet": FacetRead,
        "itsystem": ITSystemRead,
        "ituser": ITUserRead,
        "kle": KLERead,
        "leave": LeaveRead,
        "manager": ManagerRead,
        "org_unit": OrganisationUnitRead,
        "role": RoleBindingRead,
        "owner": OwnerRead,
        "relatedunit": RelatedUnitRead,
    }
    clazz = model2class[model]
    return Response[clazz](uuid=uuid)
