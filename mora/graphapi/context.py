# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import TypeAlias
from uuid import UUID

from fastramqpi.ramqp import AMQPSystem
from strawberry import Info
from strawberry.dataloader import DataLoader
from strawberry.fastapi import BaseContext

from mora import db
from mora.auth.keycloak.models import Token
from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OrganisationRead
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
from mora.graphapi.graphql_utils import LoadKey
from mora.graphapi.models import AddressRead
from mora.graphapi.models import ClassRead
from mora.graphapi.models import FacetRead
from mora.graphapi.models import RoleBindingRead


@dataclass
class MOLoaders:
    access_log_read_loader: DataLoader[UUID, list[UUID]]
    actor_name_loader: DataLoader[UUID, str | None]
    address_loader: DataLoader[LoadKey, list[AddressRead]]
    association_loader: DataLoader[LoadKey, list[AssociationRead]]
    class_loader: DataLoader[LoadKey, list[ClassRead]]
    employee_loader: DataLoader[LoadKey, list[EmployeeRead]]
    engagement_loader: DataLoader[LoadKey, list[EngagementRead]]
    facet_loader: DataLoader[LoadKey, list[FacetRead]]
    itsystem_loader: DataLoader[LoadKey, list[ITSystemRead]]
    ituser_loader: DataLoader[LoadKey, list[ITUserRead]]
    kle_loader: DataLoader[LoadKey, list[KLERead]]
    leave_loader: DataLoader[LoadKey, list[LeaveRead]]
    manager_loader: DataLoader[LoadKey, list[ManagerRead]]
    org_loader: DataLoader[int, OrganisationRead]
    org_unit_loader: DataLoader[LoadKey, list[OrganisationUnitRead]]
    owner_loader: DataLoader[LoadKey, list[OwnerRead]]
    rel_unit_loader: DataLoader[LoadKey, list[RelatedUnitRead]]
    rolebinding_loader: DataLoader[LoadKey, list[RoleBindingRead]]


@dataclass
class MOContext(BaseContext):
    get_token: Callable[[], Awaitable[Token]]
    amqp_system: AMQPSystem
    session: db.AsyncSession
    dataloaders: MOLoaders
    # Per-request authorization cache. Every field resolve consults the policy
    # engine (`actor_grants_field`); since the caller is constant within a
    # request, the caller's applicable policy rules are fetched once and cached
    # here, indexed by `(type, field)`.
    applicable_policy_rules: dict[tuple[str, str], list[Any]] | None = None


MOInfo: TypeAlias = Info[MOContext, None]
