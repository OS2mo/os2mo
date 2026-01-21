# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Awaitable
from collections.abc import Callable
from dataclasses import dataclass
from textwrap import dedent
from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastramqpi.ramqp import AMQPSystem
from starlette.responses import PlainTextResponse
from starlette.responses import RedirectResponse
from strawberry.dataloader import DataLoader
from strawberry.printer import print_schema

from mora import db
from mora import depends
from mora.auth.keycloak.models import Token
from mora.auth.keycloak.oidc import token_getter
from mora.graphapi.custom_router import CustomGraphQLRouter
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
from mora.graphapi.schema import get_schema
from mora.graphapi.version import LATEST_VERSION
from mora.graphapi.version import Version
from mora.graphapi.versions.latest.access_log import get_access_log_loaders
from mora.graphapi.versions.latest.actor import get_actor_loaders
from mora.graphapi.versions.latest.dataloaders import get_loaders
from mora.graphapi.versions.latest.graphql_utils import LoadKey
from mora.graphapi.versions.latest.models import AddressRead
from mora.graphapi.versions.latest.models import ClassRead
from mora.graphapi.versions.latest.models import FacetRead
from mora.graphapi.versions.latest.models import RoleBindingRead

router = APIRouter()


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


@dataclass
class MOContext(MOLoaders):
    get_token: Callable[[], Awaitable[Token]]
    amqp_system: AMQPSystem
    session: db.AsyncSession

    # AccessLog Loaders
    access_log_read_loader: DataLoader[UUID, list[UUID]]

    # Actor Loaders
    actor_name_loader: DataLoader[UUID, str | None]

    # Hack to allow old dictionary style access to the context
    # TODO: Convert all context uses to attr access then remove this
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


async def get_context(
    # NOTE: If you add or remove any parameters, make sure to keep the
    # execute_graphql parameters synchronised!
    get_token: Callable[[], Awaitable[Token]] = Depends(token_getter),
    amqp_system: AMQPSystem = Depends(depends.get_amqp_system),
    session: db.AsyncSession = Depends(db.get_session),
) -> MOContext:
    return MOContext(
        get_token=get_token,
        amqp_system=amqp_system,
        session=session,
        # TODO: Construct typed contexts directly
        **get_access_log_loaders(session),  # type: ignore
        **get_actor_loaders(session),  # type: ignore
        **await get_loaders(),  # type: ignore
    )


def get_router(version: Version) -> APIRouter:
    """Get Strawberry FastAPI router serving this GraphQL API version."""
    schema = get_schema(version)
    router = CustomGraphQLRouter(
        schema=schema,
        context_getter=get_context,  # type: ignore
        multipart_uploads_enabled=True,
    )

    @router.get("/schema.graphql", response_class=PlainTextResponse)
    async def sdl() -> str:  # pragma: no cover
        """Return the GraphQL version's schema definition in SDL format."""
        header = dedent(
            f"""\
            # SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
            # SPDX-License-Identifier: MPL-2.0
            #
            # OS2mo GraphQL API schema definition (v{version.value}).
            # https://os2mo.eksempel.dk/graphql/v{version.value}/schema.graphql

            """
        )
        return header + print_schema(schema)

    return router


@router.get("/graphql")
@router.get("/graphql/")
async def redirect_to_latest_graphiql() -> RedirectResponse:
    """Redirect unversioned GraphiQL so developers can pin to the newest version."""
    return RedirectResponse(f"/graphql/v{LATEST_VERSION.value}")


for version in Version:
    router.include_router(
        prefix=f"/graphql/v{version.value}", router=get_router(version)
    )
