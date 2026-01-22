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
from mora.graphapi.versions.latest.graphql_utils import LoadKey
from mora.graphapi.versions.latest.models import AddressRead
from mora.graphapi.versions.latest.models import ClassRead
from mora.graphapi.versions.latest.models import FacetRead
from mora.graphapi.versions.latest.models import RoleBindingRead


@dataclass
class MOLoaders:
    org_loader: DataLoader[int, OrganisationRead]
    # Organisation Unit
    org_unit_loader: DataLoader[LoadKey, list[OrganisationUnitRead]]
    org_unit_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Person
    employee_loader: DataLoader[LoadKey, list[EmployeeRead]]
    employee_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Engagement
    engagement_loader: DataLoader[LoadKey, list[EngagementRead]]
    engagement_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # KLE
    kle_loader: DataLoader[LoadKey, list[KLERead]]
    kle_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Address
    address_loader: DataLoader[LoadKey, list[AddressRead]]
    address_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Leave
    leave_loader: DataLoader[LoadKey, list[LeaveRead]]
    leave_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Association
    association_loader: DataLoader[LoadKey, list[AssociationRead]]
    association_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Rolebinding
    rolebinding_loader: DataLoader[LoadKey, list[RoleBindingRead]]
    rolebinding_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # ITUser
    ituser_loader: DataLoader[LoadKey, list[ITUserRead]]
    ituser_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Manager
    manager_loader: DataLoader[LoadKey, list[ManagerRead]]
    manager_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Owner
    owner_loader: DataLoader[LoadKey, list[OwnerRead]]
    owner_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Class
    class_loader: DataLoader[LoadKey, list[ClassRead]]
    class_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Related Organisation Unit
    rel_unit_loader: DataLoader[LoadKey, list[RelatedUnitRead]]
    rel_unit_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # Facet
    facet_loader: DataLoader[LoadKey, list[FacetRead]]
    facet_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # ITSysterm
    itsystem_loader: DataLoader[LoadKey, list[ITSystemRead]]
    itsystem_getter: Callable[..., Awaitable[dict[UUID, list]]]
    # AccessLog Loaders
    access_log_read_loader: DataLoader[UUID, list[UUID]]


@dataclass
class MOContext(BaseContext):
    get_token: Callable[[], Awaitable[Token]]
    amqp_system: AMQPSystem
    session: db.AsyncSession
    dataloaders: MOLoaders

    # Actor Loaders
    actor_name_loader: DataLoader[UUID, str | None]

    # Hack to allow old dictionary style access to the context
    # TODO: Convert all context uses to attr access then remove this
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


MOInfo: TypeAlias = Info[MOContext, None]
