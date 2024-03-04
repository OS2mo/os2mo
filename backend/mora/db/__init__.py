# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# flake8: noqa
from fastapi import Request
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from starlette_context import context
from starlette_context import request_cycle_context

from . import files
from ._amqp import AMQPSubsystem
from ._audit import AuditLogOperation
from ._audit import AuditLogRead
from ._bruger import Bruger
from ._bruger import BrugerAttrEgenskaber
from ._bruger import BrugerAttrUdvidelser
from ._bruger import BrugerRegistrering
from ._bruger import BrugerRelation
from ._bruger import BrugerRelationKode
from ._bruger import BrugerTilsGyldighed
from ._common import Gyldighed
from ._common import HasValidity
from ._common import LivscyklusKode
from ._common import PubliceretStatus
from ._facet import Facet
from ._facet import FacetAttrEgenskaber
from ._facet import FacetRegistrering
from ._facet import FacetRelation
from ._facet import FacetRelationKode
from ._facet import FacetTilsPubliceret
from ._itsystem import ITSystem
from ._itsystem import ITSystemAttrEgenskaber
from ._itsystem import ITSystemRegistrering
from ._itsystem import ITSystemRelation
from ._itsystem import ITSystemRelationKode
from ._itsystem import ITSystemTilsGyldighed
from ._klasse import Klasse
from ._klasse import KlasseAttrEgenskaber
from ._klasse import KlasseRegistrering
from ._klasse import KlasseRelation
from ._klasse import KlasseRelationKode
from ._klasse import KlasseTilsPubliceret
from ._organisation import Organisation
from ._organisation import OrganisationAttrEgenskaber
from ._organisation import OrganisationRegistrering
from ._organisation import OrganisationRelation
from ._organisation import OrganisationRelationKode
from ._organisation import OrganisationTilsGyldighed
from ._organisationsenhed import OrganisationEnhed
from ._organisationsenhed import OrganisationEnhedAttrEgenskaber
from ._organisationsenhed import OrganisationEnhedRegistrering
from ._organisationsenhed import OrganisationEnhedRelation
from ._organisationsenhed import OrganisationEnhedRelationKode
from ._organisationsenhed import OrganisationEnhedTilsGyldighed
from ._organisationsfunktion import OrganisationFunktion
from ._organisationsfunktion import OrganisationFunktionAttrEgenskaber
from ._organisationsfunktion import OrganisationFunktionRegistrering
from ._organisationsfunktion import OrganisationFunktionRelation
from ._organisationsfunktion import OrganisationFunktionRelationKode
from ._organisationsfunktion import OrganisationFunktionTilsGyldighed
from .files import FileToken


def create_engine(user, password, host, name) -> AsyncEngine:
    return create_async_engine(
        f"postgresql+psycopg://{user}:{password}@{host}/{name}",
        # Transparently reconnect on connection errors so the calling application does
        # not need to be concerned with error handling. This is required for the
        # testing APIs to function correctly.
        pool_pre_ping=True,
    )


def create_sessionmaker(user, password, host, name) -> async_sessionmaker:
    engine = create_engine(user, password, host, name)
    return async_sessionmaker(engine)


def _get_sessionmaker(request: Request):
    return request.app.state.sessionmaker


_DB_SESSION_CONTEXT_KEY = "db_session"


async def transaction_per_request(request: Request):
    """Start a new transaction per request.

    This is a global dependency - called for each request.

    The database session can be accessed through the FastAPI dependency (called
    `Session`) or side-step the stack (discouraged) with `get_session` below.
    """
    async with _get_sessionmaker(request)() as session, session.begin():
        data = {**context, _DB_SESSION_CONTEXT_KEY: session}
        with request_cycle_context(data):
            yield
            # At this point, the transaction will be committed. However, the
            # GraphQL extension `RollbackOnError` will call `.rollback` on the
            # session if there are any errors. This is what allows us to call
            # multiple mutators in a single GraphQL mutation and have them be
            # atomic.


def get_session() -> AsyncSession:
    return context[_DB_SESSION_CONTEXT_KEY]
