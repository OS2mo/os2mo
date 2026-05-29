# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import dataclasses
from collections.abc import Callable
from collections.abc import Sequence
from datetime import date
from datetime import datetime
from datetime import timedelta
from functools import lru_cache
from itertools import starmap
from textwrap import dedent
from typing import Annotated
from typing import Any
from typing import cast as tcast
from uuid import UUID

import strawberry
from more_itertools import only
from more_itertools import unique_everseen
from psycopg.types.range import TimestamptzRange
from pydantic import ValidationError
from sqlalchemy import ColumnElement
from sqlalchemy import Select
from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import cast
from sqlalchemy import column
from sqlalchemy import distinct
from sqlalchemy import exists
from sqlalchemy import func
from sqlalchemy import literal
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy import true
from sqlalchemy import union
from sqlalchemy.sql.functions import now as SQLNOW
from sqlalchemy.types import Text
from starlette_context import context
from strawberry import UNSET
from strawberry.dataloader import DataLoader
from strawberry.types.unset import UnsetType

from mora import util
from mora.access_log import access_log
from mora.db import AsyncSession
from mora.db import BrugerAttrEgenskaber
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import BrugerRelationKode
from mora.db import BrugerTilsGyldighed
from mora.db import FacetAttrEgenskaber
from mora.db import FacetRegistrering
from mora.db import FacetRelation
from mora.db import FacetRelationKode
from mora.db import FacetTilsPubliceret
from mora.db import HasValidity
from mora.db import ITSystemAttrEgenskaber
from mora.db import ITSystemRegistrering
from mora.db import ITSystemTilsGyldighed
from mora.db import KlasseAttrEgenskaber
from mora.db import KlasseRegistrering
from mora.db import KlasseRelation
from mora.db import KlasseRelationKode
from mora.db import KlasseTilsPubliceret
from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationEnhedRelation
from mora.db import OrganisationEnhedRelationKode
from mora.db import OrganisationEnhedTilsGyldighed
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionAttrUdvidelser
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.db import OrganisationFunktionTilsGyldighed
from mora.graphapi.context import MOInfo
from mora.graphapi.custom_schema import get_version
from mora.graphapi.gmodels.base import tz_isodate
from mora.graphapi.version import Version
from mora.service.autocomplete.employees import search_employees
from mora.service.autocomplete.shared import UUID_SEARCH_MIN_PHRASE_LENGTH

from .filters import AddressFilter
from .filters import AssociationFilter
from .filters import BaseFilter
from .filters import ClassFilter
from .filters import EmployeeFilter
from .filters import EngagementFilter
from .filters import FacetFilter
from .filters import ITSystemFilter
from .filters import ITUserFilter
from .filters import KLEFilter
from .filters import LeaveFilter
from .filters import ManagerFilter
from .filters import OrganisationUnitFilter
from .filters import OwnerFilter
from .filters import RegistrationFilter
from .filters import RelatedUnitFilter
from .filters import RoleBindingFilter
from .graphql_utils import LoadKey
from .paged import CursorType
from .paged import LimitType
from .registrationbase import RegistrationBase
from .validity import OpenValidityModel


async def filter2uuids_func(
    resolver_func: Callable,
    info: MOInfo,
    filter: BaseFilter,
    mapper: Callable[[Any], list[UUID]] | None = None,
) -> list[UUID]:
    """Resolve into a list of UUIDs with the given filter.

    Args:
        resolver: The resolver used to resolve filters to UUIDs.
        info: The strawberry execution context.
        filter: Filter instance passed to the resolver.
        mapper: Mapping function from resolver return to UUIDs.

    Returns:
        A list of UUIDs.
    """
    mapper = mapper or (lambda objects: list(objects.keys()))

    # The current resolver implementation disallows combining UUIDs with other filters.
    # As the UUIDs returned from this function are only used for further filtering,
    # we can simply return them as-is, bypassing another lookup.
    # This is purely a performance optimization
    if filter.uuids is not None:
        return filter.uuids

    return mapper(await resolver_func(info, filter=filter))


def extend_uuids(output_filter: BaseFilter, input: list[UUID] | None) -> None:
    if input is None:
        return
    output_filter.uuids = output_filter.uuids or []
    output_filter.uuids.extend(input)


def extend_user_keys(output_filter: BaseFilter, input: list[str] | None) -> None:
    if input is None:
        return
    output_filter.user_keys = output_filter.user_keys or []
    output_filter.user_keys.extend(input)


async def get_employee_uuids(info: MOInfo, filter: Any) -> list[UUID]:
    employee_filter = filter.employee or EmployeeFilter()
    # Handle deprecated filter
    extend_uuids(employee_filter, filter.employees)
    return await filter2uuids_func(employee_resolver, info, employee_filter)


async def get_engagement_uuids(info: MOInfo, filter: Any) -> list[UUID]:
    engagement_filter = filter.engagement or EngagementFilter()
    # Handle deprecated filter
    extend_uuids(engagement_filter, filter.engagements)
    return await filter2uuids_func(engagement_resolver, info, engagement_filter)


async def get_itsystem_uuids(info: MOInfo, filter: Any) -> list[UUID]:
    itsystem_filter = filter.itsystem or ITSystemFilter()
    # Handle deprecated filter
    extend_uuids(itsystem_filter, filter.itsystem_uuids)
    return await filter2uuids_func(it_system_resolver, info, itsystem_filter)


async def get_org_unit_uuids(info: MOInfo, filter: Any) -> list[UUID]:
    org_unit_filter = filter.org_unit or OrganisationUnitFilter()
    # Handle deprecated filter
    extend_uuids(org_unit_filter, filter.org_units)
    return await filter2uuids_func(organisation_unit_resolver, info, org_unit_filter)


async def facet_predicate(
    info: MOInfo,
    filter: FacetFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    async def _get_parent_uuids() -> list[UUID]:
        parent_filter = filter.parent or FacetFilter()
        # Handle deprecated filter
        extend_uuids(parent_filter, filter.parents)
        extend_user_keys(parent_filter, filter.parent_user_keys)
        return await filter2uuids_func(facet_resolver, info, parent_filter)

    predicates = [
        _get_registrering_clause(
            FacetRegistrering,
            registration_time,
        ),
        FacetRegistrering.id.in_(
            select(FacetTilsPubliceret.facet_registrering_id).where(
                FacetTilsPubliceret.publiceret == "Publiceret",
                _get_virkning_clause(FacetTilsPubliceret, filter),
            )
        ),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            FacetRegistrering.uuid.in_(
                select(FacetRegistrering.uuid).where(
                    registration_predicate(FacetRegistrering, filter.registration)
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(FacetRegistrering.facet_id.in_(filter.uuids))

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            FacetRegistrering.id.in_(
                select(FacetAttrEgenskaber.facet_registrering_id).where(
                    FacetAttrEgenskaber.brugervendtnoegle.in_(filter.user_keys),
                    _get_virkning_clause(FacetAttrEgenskaber, filter),
                )
            )
        )

    # Parents
    if (
        filter.parents is not None
        or filter.parent_user_keys is not None
        or filter.parent is not None
    ):
        parent_uuids = await _get_parent_uuids()
        predicates.append(
            FacetRegistrering.id.in_(
                select(FacetRelation.facet_registrering_id).where(
                    FacetRelation.rel_type == FacetRelationKode.facettilhoerer,
                    FacetRelation.rel_maal_uuid.in_(parent_uuids),
                    _get_virkning_clause(FacetRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def facet_resolver(
    info: MOInfo,
    filter: FacetFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve facets."""
    if filter is None:
        filter = FacetFilter()

    predicate = await facet_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(FacetRegistrering.facet_id))
        .where(predicate)
        .order_by(FacetRegistrering.facet_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_facets",
        "Facet",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.facet_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def class_predicate(
    info: MOInfo,
    filter: ClassFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    async def _get_facet_uuids() -> list[UUID]:
        facet_filter = filter.facet or FacetFilter()
        # Handle deprecated filter
        extend_uuids(facet_filter, filter.facets)
        extend_user_keys(facet_filter, filter.facet_user_keys)
        return await filter2uuids_func(facet_resolver, info, facet_filter)

    async def _get_parent_uuids() -> list[UUID]:
        class_filter = filter.parent or ClassFilter()
        # Handle deprecated filter
        extend_uuids(class_filter, filter.parents)
        extend_user_keys(class_filter, filter.parent_user_keys)
        return await filter2uuids_func(class_resolver, info, class_filter)

    predicates = [
        _get_registrering_clause(
            KlasseRegistrering,
            registration_time,
        ),
        KlasseRegistrering.id.in_(
            select(KlasseTilsPubliceret.klasse_registrering_id).where(
                KlasseTilsPubliceret.publiceret == "Publiceret",
                _get_virkning_clause(KlasseTilsPubliceret, filter),
            )
        ),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            KlasseRegistrering.uuid.in_(
                select(KlasseRegistrering.uuid).where(
                    registration_predicate(KlasseRegistrering, filter.registration)
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(KlasseRegistrering.klasse_id.in_(filter.uuids))

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseAttrEgenskaber.klasse_registrering_id).where(
                    KlasseAttrEgenskaber.brugervendtnoegle.in_(filter.user_keys),
                    _get_virkning_clause(KlasseAttrEgenskaber, filter),
                )
            )
        )

    # Name
    if filter.name is not None:
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseAttrEgenskaber.klasse_registrering_id).where(
                    KlasseAttrEgenskaber.titel.in_(filter.name),
                    _get_virkning_clause(KlasseAttrEgenskaber, filter),
                )
            )
        )

    # Scope
    if filter.scope is not None:
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseAttrEgenskaber.klasse_registrering_id).where(
                    KlasseAttrEgenskaber.omfang.in_(filter.scope),
                    _get_virkning_clause(KlasseAttrEgenskaber, filter),
                )
            )
        )

    # Facets
    if (
        filter.facets is not None
        or filter.facet_user_keys is not None
        or filter.facet is not None
    ):
        facet_uuids = await _get_facet_uuids()
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseRelation.klasse_registrering_id).where(
                    KlasseRelation.rel_type == KlasseRelationKode.facet,
                    KlasseRelation.rel_maal_uuid.in_(facet_uuids),
                    _get_virkning_clause(KlasseRelation, filter),
                )
            )
        )

    # Parents
    if (
        filter.parents is not None
        or filter.parent_user_keys is not None
        or filter.parent is not None
    ):
        parent_uuids = await _get_parent_uuids()
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseRelation.klasse_registrering_id).where(
                    KlasseRelation.rel_type == KlasseRelationKode.overordnetklasse,
                    KlasseRelation.rel_maal_uuid.in_(parent_uuids),
                    _get_virkning_clause(KlasseRelation, filter),
                )
            )
        )

    # IT system
    if filter.it_system is not None:
        it_system_uuids = await filter2uuids_func(
            it_system_resolver, info, filter.it_system
        )
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseRelation.klasse_registrering_id).where(
                    KlasseRelation.rel_type == KlasseRelationKode.mapninger,
                    KlasseRelation.rel_maal_uuid.in_(it_system_uuids),
                    _get_virkning_clause(KlasseRelation, filter),
                )
            )
        )

    # Owner
    if filter.owner is not None:
        owner_uuids = await filter2uuids_func(
            organisation_unit_resolver, info, filter.owner
        )
        matched_owner = KlasseRegistrering.id.in_(
            select(KlasseRelation.klasse_registrering_id).where(
                KlasseRelation.rel_type == KlasseRelationKode.ejer,
                KlasseRelation.rel_maal_uuid.in_(owner_uuids),
                _get_virkning_clause(KlasseRelation, filter),
            )
        )
        if filter.owner.include_none:
            no_owner = ~exists().where(
                KlasseRelation.klasse_registrering_id == KlasseRegistrering.id,
                KlasseRelation.rel_type == KlasseRelationKode.ejer,
                KlasseRelation.rel_maal_uuid.is_not(None),
                _get_virkning_clause(KlasseRelation, filter),
            )
            predicates.append(or_(matched_owner, no_owner))
        else:
            predicates.append(matched_owner)

    return and_(*predicates)


async def class_resolver(
    info: MOInfo,
    filter: ClassFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve classes."""
    if filter is None:
        filter = ClassFilter()

    predicate = await class_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(KlasseRegistrering.klasse_id))
        .where(predicate)
        .order_by(KlasseRegistrering.klasse_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_classes",
        "Klasse",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.class_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def address_predicate(
    info: MOInfo,
    filter: AddressFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    async def _get_address_type_uuids(
        info: MOInfo, filter: AddressFilter
    ) -> list[UUID]:
        class_filter = filter.address_type or ClassFilter()
        # Handle deprecated filter
        extend_uuids(class_filter, filter.address_types)
        extend_user_keys(class_filter, filter.address_type_user_keys)
        return await filter2uuids_func(class_resolver, info, class_filter)

    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "Adresse",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Employees
    if (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        employee_uuids = await get_employee_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Address type
    if (
        filter.address_types is not None
        or filter.address_type_user_keys is not None
        or filter.address_type is not None
    ):
        address_type_uuids = await _get_address_type_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(address_type_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Visibility
    # rel_type "opgaver" with objekt_type "synlighed" in mox
    # TODO: Support finding entries with visibility=None
    if filter.visibility is not None:
        visibility_uuids = await filter2uuids_func(
            class_resolver, info, filter.visibility
        )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.opgaver,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(visibility_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Engagement / IT user (both filter on `tilknyttedefunktioner`, OR-combined)
    if (
        filter.engagement is not None
        or filter.engagements is not None
        or filter.ituser is not None
    ):
        tilknyttedefunktioner: list[UUID] = []
        if filter.engagement is not None or filter.engagements is not None:
            tilknyttedefunktioner.extend(await get_engagement_uuids(info, filter))
        if filter.ituser is not None:
            tilknyttedefunktioner.extend(
                await filter2uuids_func(it_user_resolver, info, filter.ituser)
            )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        tilknyttedefunktioner
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def address_resolver(
    info: MOInfo,
    filter: AddressFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve addresses."""
    if filter is None:
        filter = AddressFilter()

    predicate = await address_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_addresses",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.address_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def association_predicate(
    info: MOInfo,
    filter: AssociationFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    async def _get_association_type_uuids(
        info: MOInfo, filter: AssociationFilter
    ) -> list[UUID]:
        class_filter = filter.association_type or ClassFilter()
        # Handle deprecated filter
        extend_uuids(class_filter, filter.association_types)
        extend_user_keys(class_filter, filter.association_type_user_keys)
        return await filter2uuids_func(class_resolver, info, class_filter)

    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "Tilknytning",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Employees
    if (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        employee_uuids = await get_employee_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Association type
    if (
        filter.association_types is not None
        or filter.association_type_user_keys is not None
        or filter.association_type is not None
    ):
        association_type_uuids = await _get_association_type_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        association_type_uuids
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def association_resolver(
    info: MOInfo,
    filter: AssociationFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve associations."""
    if filter is None:
        filter = AssociationFilter()

    predicate = await association_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_associations",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    associations = await generic_resolver(
        info.context.dataloaders.association_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )

    if filter.it_association is not None:
        filtered_data = {}
        for uuid, association_fields in associations.items():
            if filter.it_association:
                filtered_associations = [
                    association
                    for association in association_fields
                    if association.it_user_uuid is not None
                ]
            else:
                filtered_associations = [
                    association
                    for association in association_fields
                    if association.it_user_uuid is None
                ]
            if filtered_associations:
                filtered_data[uuid] = filtered_associations
        associations = filtered_data

    return associations


async def employee_predicate(
    info: MOInfo,
    filter: EmployeeFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    predicates = [
        _get_registrering_clause(
            BrugerRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            BrugerRegistrering,
            BrugerTilsGyldighed,
            filter,
        ),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            BrugerRegistrering.uuid.in_(
                select(BrugerRegistrering.uuid).where(
                    registration_predicate(BrugerRegistrering, filter.registration)
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(BrugerRegistrering.bruger_id.in_(filter.uuids))

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            BrugerRegistrering.id.in_(
                select(BrugerAttrEgenskaber.bruger_registrering_id).where(
                    BrugerAttrEgenskaber.brugervendtnoegle.in_(filter.user_keys),
                    _get_virkning_clause(BrugerAttrEgenskaber, filter),
                )
            )
        )

    # CPR numbers
    if filter.cpr_numbers is not None:
        predicates.append(
            BrugerRegistrering.id.in_(
                select(BrugerRelation.bruger_registrering_id).where(
                    BrugerRelation.rel_type == BrugerRelationKode.tilknyttedepersoner,
                    BrugerRelation.rel_maal_urn.in_(
                        f"urn:dk:cpr:person:{c}" for c in filter.cpr_numbers
                    ),
                    _get_virkning_clause(BrugerRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def employee_resolver(
    info: MOInfo,
    filter: EmployeeFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve employees."""
    if filter is None:
        filter = EmployeeFilter()

    # Searching is implemented by an sqlalchemy query, returning UUIDs which
    # are passsed to generic_resolver's `uuid` filter. Supplying UUIDs to
    # generic_resolver ignores all other filter arguments, so we short-circuit
    # here to make that fact obvious.
    if filter.query:
        other_fields = (filter.uuids, filter.user_keys, filter.cpr_numbers)
        if any(other_fields):
            raise ValueError("filter.query must be used alone")
        r = await generic_resolver(
            info.context.dataloaders.employee_loader,
            uuids=await search_employees(
                session=info.context.session,
                query=filter.query,
                limit=limit,
                cursor=cursor,
            ),
            from_date=filter.from_date,
            to_date=filter.to_date,
            registration_time=filter.registration_time,
        )
        # We don't pass limit/cursor to generic_resolver, since that isn't
        # supported together with `uuid`, so we have to mange pagination.
        if not r:
            context["lora_page_out_of_range"] = True
        return r

    predicate = await employee_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(BrugerRegistrering.bruger_id))
        .where(predicate)
        .order_by(BrugerRegistrering.bruger_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_employees",
        "Bruger",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.employee_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def engagement_predicate(
    info: MOInfo,
    filter: EngagementFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "Engagement",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Employees
    if (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        employee_uuids = await get_employee_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Job function
    if filter.job_function is not None:
        job_function_uuids = await filter2uuids_func(
            class_resolver, info, filter.job_function
        )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.opgaver,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(job_function_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Engagement type
    if filter.engagement_type is not None:
        engagement_type_uuids = await filter2uuids_func(
            class_resolver, info, filter.engagement_type
        )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        engagement_type_uuids
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # IT user
    # The `tilknyttedefunktioner` relation lives on the ITUser's registration
    # pointing at the engagement UUID; resolve via the ituser predicate.
    if filter.ituser is not None:
        ituser_pred = await it_user_predicate(
            info,
            filter.ituser,
            registration_time=registration_time,
        )
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(
                select(OrganisationFunktionRelation.rel_maal_uuid).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.organisationfunktion_registrering_id.in_(
                        select(OrganisationFunktionRegistrering.id).where(ituser_pred)
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def engagement_resolver(
    info: MOInfo,
    filter: EngagementFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve engagements."""
    if filter is None:
        filter = EngagementFilter()

    predicate = await engagement_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_engagements",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.engagement_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def manager_predicate(
    info: MOInfo,
    filter: ManagerFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "Leder",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Employees
    if get_version(info.schema) >= Version.VERSION_25:
        if filter.employee is None:
            # Vacant managers are encoded in two ways, either:
            # * As a tilknyttedebrugere row with nulls in both UUID and URN, or
            # * A missing tilknyttedebrugere row
            # Depending on whether other validities exist within the same registration.
            bruger_row_exists = exists(
                select(OrganisationFunktionRelation.id).where(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                    == OrganisationFunktionRegistrering.id,
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
            vacant_row_exists = exists(
                select(OrganisationFunktionRelation.id).where(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                    == OrganisationFunktionRegistrering.id,
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.is_(None),
                    OrganisationFunktionRelation.rel_maal_urn.is_(None),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
            predicates.append(
                or_(
                    # This handles the case where no row exists
                    # This situation occurs when a vacant manager is created as the sole validity
                    ~bruger_row_exists,
                    vacant_row_exists,
                )
            )
        elif filter.employee is not UNSET or filter.employees is not None:
            employee_uuids = await get_employee_uuids(info, filter)
            predicates.append(
                OrganisationFunktionRegistrering.id.in_(
                    select(
                        OrganisationFunktionRelation.organisationfunktion_registrering_id
                    ).where(
                        OrganisationFunktionRelation.rel_type
                        == OrganisationFunktionRelationKode.tilknyttedebrugere,
                        OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                        _get_virkning_clause(OrganisationFunktionRelation, filter),
                    )
                )
            )
    elif (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        employee_uuids = await get_employee_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Responsibility
    if filter.responsibility is not None:
        responsibility_uuids = await filter2uuids_func(
            class_resolver, info, filter.responsibility
        )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.opgaver,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        responsibility_uuids
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Manager type
    if filter.manager_type is not None:
        manager_type_uuids = await filter2uuids_func(
            class_resolver, info, filter.manager_type
        )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(manager_type_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Engagement
    if filter.engagement is not None:
        engagement_uuids = await filter2uuids_func(
            engagement_resolver, info, filter.engagement
        )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(engagement_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def manager_resolver(
    info: MOInfo,
    filter: ManagerFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
    inherit: Annotated[
        bool,
        strawberry.argument(
            description=dedent(
                """\
                Whether to inherit managerial roles or not.

                If managerial roles exist directly on this organisation unit, the flag does nothing and these managerial roles are returned.
                However if no managerial roles exist directly, and this flag is:
                * False: An empty list is returned.
                * True: The result from calling `managers` with `inherit=True` on the parent of this organistion unit is returned.

                Calling with `inherit=True` can help ensure that a manager is always found.
                """
            )
        ),
    ] = False,
) -> Any:
    """Resolve managers."""
    if filter is None:
        filter = ManagerFilter()

    predicate = await manager_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_managers",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    result = await generic_resolver(
        info.context.dataloaders.manager_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )
    if filter.exclude is not None:
        exclude_uuids = set(
            await filter2uuids_func(employee_resolver, info, filter.exclude)
        )
        result = {
            key: value
            for key, value in result.items()
            if all(validity.employee_uuid not in exclude_uuids for validity in value)
        }

    if result or not inherit:
        return result

    if filter.org_units is None and filter.org_unit is None:
        raise ValueError("The inherit flag requires an organizational unit filter")
    org_unit_uuids = await get_org_unit_uuids(info, filter)

    org_unit = only(
        org_unit_uuids,
        too_long=ValueError(
            "The inherit flag only works with at most one organisational unit"
        ),
    )
    if org_unit is None:
        return {}
    # Recurse up the tree using the parent org-unit
    child_filter = dataclasses.replace(
        filter,
        org_units=None,
        org_unit=OrganisationUnitFilter(child=OrganisationUnitFilter(uuids=[org_unit])),
    )
    return await manager_resolver(info, filter=child_filter, inherit=True)


async def owner_predicate(
    info: MOInfo,
    filter: OwnerFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    # TODO: this function should not be an awaitable

    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "owner",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Employees
    if (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        employee_uuids = await get_employee_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Owner
    if filter.owner is not None:
        owner_uuids = await filter2uuids_func(employee_resolver, info, filter.owner)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedepersoner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(owner_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def owner_resolver(
    info: MOInfo,
    filter: OwnerFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve owners."""
    if filter is None:
        filter = OwnerFilter()

    predicate = await owner_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_owners",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.owner_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


def _get_registration_time(
    filter: BaseFilter,
    cursor: CursorType,
) -> datetime | SQLNOW:
    if (
        cursor is not None
        and filter.registration_time
        and filter.registration_time != cursor.registration_time
    ):
        raise ValueError("Cannot change registration_time during pagination")

    if cursor is not None:
        return tz_isodate(cursor.registration_time)
    if filter.registration_time:
        return tz_isodate(filter.registration_time)
    return func.now()


def _get_registrering_clause(
    cls: type[
        BrugerRegistrering
        | FacetRegistrering
        | ITSystemRegistrering
        | KlasseRegistrering
        | OrganisationEnhedRegistrering
        | OrganisationFunktionRegistrering
    ],
    time: datetime | SQLNOW,
) -> ColumnElement:
    return and_(
        cls.lifecycle != "Slettet",
        cls.registrering_period.contains(time),
    )


def _get_virkning_clause(
    cls: type[HasValidity],
    filter: BaseFilter,
) -> ColumnElement:
    start, end = get_sqlalchemy_date_interval(filter.from_date, filter.to_date)
    return cls.virkning_period.overlaps(TimestamptzRange(start, end))


def _get_gyldighed_clause(
    registrering_cls: type[
        BrugerRegistrering
        | ITSystemRegistrering
        | OrganisationEnhedRegistrering
        | OrganisationFunktionRegistrering
    ],
    gyldighed_cls: type[
        BrugerTilsGyldighed
        | ITSystemTilsGyldighed
        | OrganisationEnhedTilsGyldighed
        | OrganisationFunktionTilsGyldighed
    ],
    filter: BaseFilter,
) -> ColumnElement:
    fk_column = getattr(gyldighed_cls, f"{registrering_cls.__tablename__}_id")
    return registrering_cls.id.in_(
        select(fk_column).where(
            gyldighed_cls.gyldighed == "Aktiv",
            _get_virkning_clause(gyldighed_cls, filter),
        )
    )


async def organisation_unit_predicate(
    info: MOInfo,
    filter: OrganisationUnitFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    async def _get_parent_uuids() -> list[UUID] | Select:
        org_unit_filter = filter.parent or OrganisationUnitFilter()
        # Handle deprecated filter
        # parents vs parent values
        #       | UNSET | None    | xs
        # UNSET | noop  | root    | xs
        # None  | root  | root    | root+xs
        # ys    | ys    | root+ys | xs+ys
        #
        # The above assignment handles all parent=ys cases
        # Thus we only need to check for parents=xs and Nones

        # The root unit isn't really an org unit in the database, so we can't
        # craft a query which will fetch it. We assume the user didn't supply
        # any other filters if they're looking for the root unit and return its
        # UUID directly.
        root_org: UUID = (await info.context.dataloaders.org_loader.load(0)).uuid
        if filter.parents is None or filter.parent is None:
            return [root_org]
        if filter.parents is not UNSET and root_org in filter.parents:
            if filter.parents != [root_org]:
                raise ValueError(
                    "Cannot filter root org unit with other org units"
                )  # pragma: no cover
            return [root_org]
        if (
            org_unit_filter.uuids is not None and root_org in org_unit_filter.uuids
        ):  # pragma: no cover
            if org_unit_filter.uuids != [root_org]:
                raise ValueError("Cannot filter root org unit with other org units")
            return [root_org]
        if filter.parents is not UNSET:
            extend_uuids(org_unit_filter, filter.parents)
        sub_predicate = await organisation_unit_predicate(
            info=info,
            filter=org_unit_filter,
            registration_time=registration_time,
        )
        return (
            select(distinct(OrganisationEnhedRegistrering.organisationenhed_id))
            .where(sub_predicate)
            .order_by(OrganisationEnhedRegistrering.organisationenhed_id)
        )

    async def _get_hierarchy_uuids() -> list[UUID]:
        class_filter = filter.hierarchy or ClassFilter()
        # Handle deprecated filter
        extend_uuids(class_filter, filter.hierarchies)
        return await filter2uuids_func(class_resolver, info, class_filter)

    predicates = [
        _get_registrering_clause(
            OrganisationEnhedRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationEnhedRegistrering,
            OrganisationEnhedTilsGyldighed,
            filter,
        ),
    ]

    if filter.engagement is not None:
        predicates.append(
            OrganisationEnhedRegistrering.organisationenhed_id.in_(
                select(OrganisationFunktionRelation.rel_maal_uuid).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.organisationfunktion_registrering_id.in_(
                        select(OrganisationFunktionRegistrering.id).where(
                            await engagement_predicate(
                                info=info,
                                filter=filter.engagement,
                                registration_time=registration_time,
                            )
                        )
                    ),
                    _get_virkning_clause(
                        OrganisationFunktionRelation, filter.engagement
                    ),
                )
            )
        )

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationEnhedRegistrering.uuid.in_(
                select(OrganisationEnhedRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationEnhedRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationEnhedRegistrering.organisationenhed_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationEnhedRegistrering.id.in_(
                select(
                    OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
                ).where(
                    OrganisationEnhedAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationEnhedAttrEgenskaber, filter),
                )
            )
        )

    # Name
    if filter.names is not UNSET and filter.names is not None:
        predicates.append(
            OrganisationEnhedRegistrering.id.in_(
                select(
                    OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
                ).where(
                    OrganisationEnhedAttrEgenskaber.enhedsnavn.in_(filter.names),
                    _get_virkning_clause(OrganisationEnhedAttrEgenskaber, filter),
                )
            )
        )

    # Parents
    if filter.parent is not UNSET or filter.parents is not UNSET:
        parent_uuids = await _get_parent_uuids()
        predicates.append(
            OrganisationEnhedRegistrering.id.in_(
                select(
                    OrganisationEnhedRelation.organisationenhed_registrering_id
                ).where(
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.overordnet,
                    OrganisationEnhedRelation.rel_maal_uuid.in_(parent_uuids),
                    _get_virkning_clause(OrganisationEnhedRelation, filter),
                )
            )
        )

    # Hierarchies
    if filter.hierarchy is not None or filter.hierarchies is not None:
        # TODO: _get_hierarchy_uuids should not be an awaitable
        hierarchy_uuids = await _get_hierarchy_uuids()
        predicates.append(
            OrganisationEnhedRegistrering.id.in_(
                select(
                    OrganisationEnhedRelation.organisationenhed_registrering_id
                ).where(
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.opmærkning,
                    OrganisationEnhedRelation.rel_maal_uuid.in_(hierarchy_uuids),
                    _get_virkning_clause(OrganisationEnhedRelation, filter),
                )
            )
        )

    # Descendant
    if filter.descendant is not UNSET or filter.subtree is not UNSET:
        # Find all matching children and then recursively find their parents.
        if filter.descendant is not UNSET and filter.subtree is not UNSET:
            raise ValueError(
                "Cannot use both `descendant` and `subtree` filter"
            )  # pragma: no cover
        org_unit_filter = (
            filter.descendant or filter.subtree or OrganisationUnitFilter()
        )
        base_leafs_predicate = await organisation_unit_predicate(
            info=info,
            filter=org_unit_filter,
            registration_time=registration_time,
        )
        base_leafs = (
            select(distinct(OrganisationEnhedRegistrering.organisationenhed_id))
            .where(base_leafs_predicate)
            .order_by(OrganisationEnhedRegistrering.organisationenhed_id)
        )
        leafs = (
            select(
                OrganisationEnhedRegistrering.organisationenhed_id,
            )
            .where(OrganisationEnhedRegistrering.organisationenhed_id.in_(base_leafs))
            .cte(recursive=True)
        )
        parents = (
            select(
                OrganisationEnhedRelation.rel_maal_uuid,
            )
            .join(
                OrganisationEnhedRegistrering,
            )
            .where(
                _get_registrering_clause(
                    OrganisationEnhedRegistrering,
                    registration_time,
                ),
            )
            .join(
                leafs,
                and_(
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.overordnet,
                    OrganisationEnhedRegistrering.organisationenhed_id
                    == leafs.c.organisationenhed_id,
                    _get_virkning_clause(OrganisationEnhedRelation, filter),
                ),
            )
        )
        ancestors = leafs.union(parents)
        predicates.append(
            OrganisationEnhedRegistrering.organisationenhed_id.in_(
                select(ancestors.c.organisationenhed_id)
            )
        )

    # Child
    if filter.child is None:
        # Find parents having no children whatsoever
        predicates.append(
            ~exists(
                # An org-unit has children iff it is referred to by `rel_maal_uuid`
                # in an `overordnet` type relation within OrganisationEnhedRelation
                # This selects all active parent relations
                select(OrganisationEnhedRelation.rel_maal_uuid)
                .where(
                    _get_registrering_clause(
                        OrganisationEnhedRegistrering,
                        registration_time,
                    ),
                    _get_virkning_clause(OrganisationEnhedRelation, filter),
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.overordnet,
                    OrganisationEnhedRelation.rel_maal_uuid
                    == OrganisationEnhedRegistrering.organisationenhed_id,
                )
                .correlate(OrganisationEnhedRegistrering)
            )
        )
    elif filter.child is not UNSET:
        # Find parents having one of the provided children as a direct child
        child_predicate = await organisation_unit_predicate(
            info=info,
            filter=filter.child,
            registration_time=registration_time,
        )
        base_query = (
            select(distinct(OrganisationEnhedRegistrering.organisationenhed_id))
            .where(child_predicate)
            .order_by(OrganisationEnhedRegistrering.organisationenhed_id)
        )
        predicates.append(
            # An org-unit is a parent to one of our provided children iff its
            # UUID is pointed to by `rel_maal_uuid` in an `overordnet` type
            # relation within OrganisationEnhedRelation
            OrganisationEnhedRegistrering.organisationenhed_id.in_(
                # This selects all active parent relations for our children
                select(OrganisationEnhedRelation.rel_maal_uuid)
                .join(OrganisationEnhedRegistrering)
                .where(
                    _get_registrering_clause(
                        OrganisationEnhedRegistrering,
                        registration_time,
                    ),
                    _get_virkning_clause(OrganisationEnhedRelation, filter),
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.overordnet,
                    OrganisationEnhedRegistrering.organisationenhed_id.in_(base_query),
                )
            )
        )

    # Ancestor
    if filter.ancestor is not UNSET:
        # Find all matching parents and then recursively find their children.
        org_unit_filter = filter.ancestor or OrganisationUnitFilter()
        ancestor_predicate = await organisation_unit_predicate(
            info=info,
            filter=org_unit_filter,
            registration_time=registration_time,
        )
        base_query = (
            select(distinct(OrganisationEnhedRegistrering.organisationenhed_id))
            .where(ancestor_predicate)
            .order_by(OrganisationEnhedRegistrering.organisationenhed_id)
        )
        base = (
            select(
                OrganisationEnhedRegistrering.organisationenhed_id,
            )
            .where(OrganisationEnhedRegistrering.organisationenhed_id.in_(base_query))
            .cte(recursive=True)
        )
        children = (
            select(
                OrganisationEnhedRegistrering.organisationenhed_id,
            )
            .join(
                OrganisationEnhedRelation,
            )
            .where(
                _get_registrering_clause(
                    OrganisationEnhedRegistrering,
                    registration_time,
                ),
                _get_virkning_clause(OrganisationEnhedRelation, filter),
            )
            .join(
                base,
                and_(
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.overordnet,
                    OrganisationEnhedRelation.rel_maal_uuid
                    == base.c.organisationenhed_id,
                ),
            )
        )
        descendants = base.union(children)
        predicates.append(
            OrganisationEnhedRegistrering.organisationenhed_id.in_(
                select(descendants.c.organisationenhed_id)
            )
        )

    # Query search
    if filter.query:
        search_phrase = util.query_to_search_phrase(filter.query)

        clauses = [
            OrganisationEnhedRegistrering.id.in_(
                select(
                    OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
                ).where(
                    or_(
                        OrganisationEnhedAttrEgenskaber.brugervendtnoegle.ilike(
                            search_phrase
                        ),
                        OrganisationEnhedAttrEgenskaber.enhedsnavn.ilike(search_phrase),
                    ),
                    _get_virkning_clause(OrganisationEnhedAttrEgenskaber, filter),
                )
            ),
        ]

        if len(filter.query) > UUID_SEARCH_MIN_PHRASE_LENGTH:
            clauses.append(
                cast(OrganisationEnhedRegistrering.organisationenhed_id, Text).ilike(
                    search_phrase
                )
            )

        predicates.append(or_(*clauses))

    return and_(*predicates)


async def organisation_unit_resolver(
    info: MOInfo,
    filter: OrganisationUnitFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve organisation units."""
    if filter is None:
        filter = OrganisationUnitFilter()

    predicate = await organisation_unit_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationEnhedRegistrering.organisationenhed_id))
        .where(predicate)
        .order_by(OrganisationEnhedRegistrering.organisationenhed_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_orgunits",
        "OrganisationEnhed",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.org_unit_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def organisation_unit_has_children(
    info: MOInfo,
    filter: OrganisationUnitFilter | None,
) -> bool:
    """Resolve whether an organisation unit has children."""
    assert filter is not None  # cannot be None, but signature required for seeding
    predicate = await organisation_unit_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, None),
    )
    query = (
        select(distinct(OrganisationEnhedRegistrering.organisationenhed_id))
        .where(predicate)
        .order_by(OrganisationEnhedRegistrering.organisationenhed_id)
    )
    session: AsyncSession = info.context.session
    return (await session.scalars(select(exists(query)))).one()


async def organisation_unit_child_count(
    info: MOInfo,
    filter: OrganisationUnitFilter | None,
) -> int:
    """Resolve the number of children of an organisation unit."""
    assert filter is not None  # cannot be None, but signature required for seeding
    predicate = await organisation_unit_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, None),
    )
    query = (
        select(distinct(OrganisationEnhedRegistrering.organisationenhed_id))
        .where(predicate)
        .order_by(OrganisationEnhedRegistrering.organisationenhed_id)
    )
    session: AsyncSession = info.context.session
    return (
        await session.scalars(select(func.count()).select_from(query.subquery()))
    ).one()


async def it_system_predicate(
    info: MOInfo,
    filter: ITSystemFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    predicates = [
        _get_registrering_clause(
            ITSystemRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            ITSystemRegistrering,
            ITSystemTilsGyldighed,
            filter,
        ),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            ITSystemRegistrering.uuid.in_(
                select(ITSystemRegistrering.uuid).where(
                    registration_predicate(ITSystemRegistrering, filter.registration)
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(ITSystemRegistrering.itsystem_id.in_(filter.uuids))

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            ITSystemRegistrering.id.in_(
                select(ITSystemAttrEgenskaber.itsystem_registrering_id).where(
                    ITSystemAttrEgenskaber.brugervendtnoegle.in_(filter.user_keys),
                    _get_virkning_clause(ITSystemAttrEgenskaber, filter),
                )
            )
        )

    return and_(*predicates)


async def it_system_resolver(
    info: MOInfo,
    filter: ITSystemFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve IT systems."""
    if filter is None:
        filter = ITSystemFilter()

    predicate = await it_system_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(ITSystemRegistrering.itsystem_id))
        .where(predicate)
        .order_by(ITSystemRegistrering.itsystem_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_itsystems",
        "ITSystem",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.itsystem_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def it_user_predicate(
    info: MOInfo,
    filter: ITUserFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "IT-system",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Employees
    if (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        employee_uuids = await get_employee_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # IT systems
    if filter.itsystem_uuids is not None or filter.itsystem is not None:
        itsystem_uuids = await get_itsystem_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeitsystemer,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(itsystem_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Engagement
    if filter.engagement is not None:  # pragma: no cover
        engagement_uuids = await filter2uuids_func(
            engagement_resolver, info, filter.engagement
        )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(engagement_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # In v29 and prior None and UNSET were handled identically (no filtering),
    # this branch ensures backwards compatability with this behavior.
    if get_version(info.schema) <= Version.VERSION_29 and filter.external_ids is None:
        filter.external_ids = UNSET

    # External IDs
    if filter.external_ids is None:
        # Filter `null` returns only it-users without `external_id` set
        predicates.append(
            ~exists().where(
                OrganisationFunktionAttrUdvidelser.organisationfunktion_registrering_id
                == OrganisationFunktionRegistrering.id,
                OrganisationFunktionAttrUdvidelser.udvidelse_1.is_not(None),
                _get_virkning_clause(OrganisationFunktionAttrUdvidelser, filter),
            )
        )
    elif filter.external_ids is not UNSET:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrUdvidelser.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrUdvidelser.udvidelse_1.in_(
                        filter.external_ids
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrUdvidelser, filter),
                )
            )
        )

    # Binding types
    if filter.binding_types is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrUdvidelser.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrUdvidelser.udvidelse_2.in_(
                        filter.binding_types
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrUdvidelser, filter),
                )
            )
        )

    return and_(*predicates)


async def it_user_resolver(
    info: MOInfo,
    filter: ITUserFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve it-users."""
    if filter is None:
        filter = ITUserFilter()

    predicate = await it_user_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_itusers",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.ituser_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def kle_predicate(
    info: MOInfo,
    filter: KLEFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "KLE",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def kle_resolver(
    info: MOInfo,
    filter: KLEFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve kle."""
    if filter is None:
        filter = KLEFilter()

    predicate = await kle_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_kles",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.kle_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def leave_predicate(
    info: MOInfo,
    filter: LeaveFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "Orlov",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Employees
    if (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        employee_uuids = await get_employee_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(employee_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def leave_resolver(
    info: MOInfo,
    filter: LeaveFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve leaves."""
    if filter is None:
        filter = LeaveFilter()

    predicate = await leave_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_leaves",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.leave_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


# type: ignore[no-untyped-def,override]
async def get_by_uuid(
    dataloader: DataLoader, keys: list[LoadKey]
) -> dict[UUID, dict[str, Any]]:
    deduplicated_keys = list(unique_everseen(keys))
    responses = await dataloader.load_many(deduplicated_keys)
    # Filter empty objects, see: https://redmine.magenta-aps.dk/issues/51523.
    return {
        key.uuid: objects
        for key, objects in zip(deduplicated_keys, responses)
        if objects != []
    }


async def generic_resolver(
    loader: DataLoader,
    uuids: Sequence[UUID],
    from_date: datetime | UnsetType | None = UNSET,
    to_date: datetime | UnsetType | None = UNSET,
    registration_time: datetime | None = None,
) -> Any:
    """The internal resolve interface."""
    # Dates
    dates = get_date_interval(from_date, to_date)

    # Early return on empty UUID list
    if not uuids:
        return dict()

    return await get_by_uuid(
        dataloader=loader,
        keys=[
            LoadKey(uuid, dates.from_date, dates.to_date, registration_time)
            for uuid in uuids
        ],
    )


async def related_unit_predicate(
    info: MOInfo,
    filter: RelatedUnitFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    # TODO: this function should not be an awaitable

    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "Relateret Enhed",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def related_unit_resolver(
    info: MOInfo,
    filter: RelatedUnitFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve related units."""
    if filter is None:
        filter = RelatedUnitFilter()

    predicate = await related_unit_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_related_units",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.rel_unit_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


async def rolebinding_predicate(
    info: MOInfo,
    filter: RoleBindingFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    def _funktionsnavn() -> ColumnElement:
        return OrganisationFunktionRegistrering.id.in_(
            select(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            ).where(
                OrganisationFunktionAttrEgenskaber.funktionsnavn == "Rollebinding",
                _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
            )
        )

    predicates = [
        _get_registrering_clause(
            OrganisationFunktionRegistrering,
            registration_time,
        ),
        _get_gyldighed_clause(
            OrganisationFunktionRegistrering,
            OrganisationFunktionTilsGyldighed,
            filter,
        ),
        _funktionsnavn(),
    ]

    # Registration
    if filter.registration is not None:
        predicates.append(
            OrganisationFunktionRegistrering.uuid.in_(
                select(OrganisationFunktionRegistrering.uuid).where(
                    registration_predicate(
                        OrganisationFunktionRegistrering, filter.registration
                    )
                )
            )
        )

    # UUIDs
    if filter.uuids is not None:
        predicates.append(
            OrganisationFunktionRegistrering.organisationfunktion_id.in_(filter.uuids)
        )

    # User keys
    if filter.user_keys is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionAttrEgenskaber.brugervendtnoegle.in_(
                        filter.user_keys
                    ),
                    _get_virkning_clause(OrganisationFunktionAttrEgenskaber, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        org_unit_uuids = await get_org_unit_uuids(info, filter)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(org_unit_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # IT-user
    if filter.ituser is not None:
        ituser_uuids = await filter2uuids_func(it_user_resolver, info, filter.ituser)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(ituser_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Role
    if filter.role is not None:
        role_uuids = await filter2uuids_func(class_resolver, info, filter.role)
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(role_uuids),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    return and_(*predicates)


async def rolebinding_resolver(
    info: MOInfo,
    filter: RoleBindingFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> Any:
    """Resolve rolebindings."""
    if filter is None:
        filter = RoleBindingFilter()

    predicate = await rolebinding_predicate(
        info=info,
        filter=filter,
        registration_time=_get_registration_time(filter, cursor),
    )
    query = (
        select(distinct(OrganisationFunktionRegistrering.organisationfunktion_id))
        .where(predicate)
        .order_by(OrganisationFunktionRegistrering.organisationfunktion_id)
    )
    # Pagination must be done here since the generic_resolver (lora) does not
    # support filtering on UUIDs and limit/cursor at the same time.
    if limit is not None:
        query = query.limit(limit)
    if cursor is not None:
        query = query.offset(cursor.offset)

    # Execute
    session: AsyncSession = info.context.session
    uuids = (await session.scalars(query)).all()

    # Pagination
    is_paged = limit != 0 and cursor is not None and cursor.offset > 0
    if not uuids and is_paged:
        context["lora_page_out_of_range"] = True

    access_log(
        session,
        "filter_rolebindings",
        "OrganisationFunktion",
        {
            "filter": filter,
            "limit": limit,
            "cursor": cursor,
        },
        uuids,
    )

    return await generic_resolver(
        info.context.dataloaders.rolebinding_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


@lru_cache(maxsize=128)
def _get_open_validity(
    from_date: datetime | None, to_date: datetime | None
) -> OpenValidityModel:
    try:
        return OpenValidityModel(from_date=from_date, to_date=to_date)
    except ValidationError as v_error:
        # Pydantic errors are ugly in GraphQL, so we get the msg part only
        message = ", ".join([err["msg"] for err in v_error.errors()])
        raise ValueError(message)


def unset2date(dt: datetime | UnsetType | None) -> datetime | None:
    """Convert a potentially unset datetime to a non-unset datetime.

    If the input has UNSET as a value, the current time in utc will be returned.

    Args:
        dt: A potentially unset or null datetime.

    Returns:
        A potentially null datetime.
    """
    if dt is UNSET:
        return util.now()
    return tcast(datetime | None, dt)


def get_date_interval(
    from_date: datetime | UnsetType | None = UNSET,
    to_date: datetime | UnsetType | None = UNSET,
) -> OpenValidityModel:
    """Get the date interval for GraphQL queries to support bitemporal lookups.

    Args:
        from_date: The lower bound of the request interval
        to_date: The upper bound of the request interval

    Raises:
        ValueError: If lower bound is none and upper bound is unset
        ValueError: If the interval is invalid, e.g. lower > upper
    """
    from_date = unset2date(from_date)
    if to_date is UNSET:
        if from_date is None:
            raise ValueError(
                "Cannot infer UNSET to_date from interval starting at -infinity"
            )
        to_date = from_date + timedelta(milliseconds=1)
    return _get_open_validity(from_date, to_date)


def get_sqlalchemy_date_interval(
    from_date: datetime | None = UNSET, to_date: datetime | None = UNSET
) -> tuple[datetime, datetime]:
    """Get the date interval for SQLAlchemy where-clauses to support bitemporal lookups."""
    dates = get_date_interval(from_date, to_date)
    return (
        dates.from_date or util.NEGATIVE_INFINITY,
        dates.to_date or util.POSITIVE_INFINITY,
    )


def registration_predicate(table: Any, filter: RegistrationFilter) -> ColumnElement:
    # Seed with true() so an unfiltered (empty) predicate is a valid no-op WHERE.
    predicates: list[ColumnElement] = [true()]

    if filter.uuids is not None:
        predicates.append(table.uuid.in_(filter.uuids))

    if filter.actors is not None:  # pragma: no cover
        predicates.append(table.actor.in_(filter.actors))

    if filter.start is not None or filter.end is not None:
        start, end = get_sqlalchemy_date_interval(filter.start, filter.end)
        predicates.append(func.lower(table.registrering_period) <= end)
        predicates.append(func.upper(table.registrering_period) > start)

    return and_(*predicates)


def row2registration(
    model: str, id: int, uuid: UUID, actor: UUID, note: str, start_t: Any, end_t: Any
) -> RegistrationBase:
    """Construct a registration model.

    Args:
        model: The name of the entity model.
        id: Internal ID for the registrationself.
        uuid: UUID of the modified entryself.
        actor: UUID of the actor whom made the change.
        start_t: Start of the active interval.
        start_t: End of the active interval.

    Returns:
        The constructed registration model.
    """
    start: datetime = util.parsedatetime(start_t)
    end: datetime | None = util.parsedatetime(end_t)
    assert end is not None
    if end.date() == date(9999, 12, 31):
        end = None

    from .model_registration import AddressRegistration
    from .model_registration import AssociationRegistration
    from .model_registration import ClassRegistration
    from .model_registration import EngagementRegistration
    from .model_registration import FacetRegistration
    from .model_registration import ITSystemRegistration
    from .model_registration import ITUserRegistration
    from .model_registration import KLERegistration
    from .model_registration import LeaveRegistration
    from .model_registration import ManagerRegistration
    from .model_registration import OrganisationUnitRegistration
    from .model_registration import OwnerRegistration
    from .model_registration import PersonRegistration
    from .model_registration import RelatedUnitRegistration
    from .model_registration import RoleBindingRegistration

    lookup = {
        "address": AddressRegistration,
        "association": AssociationRegistration,
        "class": ClassRegistration,
        "employee": PersonRegistration,
        "engagement": EngagementRegistration,
        "facet": FacetRegistration,
        "itsystem": ITSystemRegistration,
        "ituser": ITUserRegistration,
        "kle": KLERegistration,
        "leave": LeaveRegistration,
        "manager": ManagerRegistration,
        "owner": OwnerRegistration,
        "org_unit": OrganisationUnitRegistration,
        "related": RelatedUnitRegistration,
        "role": RoleBindingRegistration,
    }
    cls = lookup.get(model)

    return cls(  # type: ignore
        model=model,
        uuid=uuid,
        registration_id=id,
        start=start,
        end=end,
        actor=actor,
        note=note,
    )


async def registration_resolver(
    info: MOInfo,
    filter: RegistrationFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[Any]:
    if filter is None:
        filter = RegistrationFilter()

    model2table = {
        "address": OrganisationFunktionRegistrering,
        "association": OrganisationFunktionRegistrering,
        "class": KlasseRegistrering,
        "employee": BrugerRegistrering,
        "engagement": OrganisationFunktionRegistrering,
        "facet": FacetRegistrering,
        "itsystem": ITSystemRegistrering,
        "ituser": OrganisationFunktionRegistrering,
        "kle": OrganisationFunktionRegistrering,
        "leave": OrganisationFunktionRegistrering,
        "manager": OrganisationFunktionRegistrering,
        "org_unit": OrganisationEnhedRegistrering,
        "role": OrganisationFunktionRegistrering,
        "owner": OrganisationFunktionRegistrering,
        "related": OrganisationFunktionRegistrering,
    }

    tables = set(model2table.values())
    # If given a model filter, only query relevant tables
    if filter.models is not None:
        valid_keys = set(filter.models) & model2table.keys()
        tables = {model2table[key] for key in valid_keys}
        # If only invalid model names were given, we can early return
        if not tables:  # pragma: no cover
            return []

    def generate_query(table: Any) -> Select:
        common_fields = [
            table.id.label("id"),
            table.uuid.label("uuid"),
            table.actor.label("actor"),
            table.note.label("note"),
            func.lower(table.registrering_period).label("start"),
            func.upper(table.registrering_period).label("end"),
        ]

        if table == OrganisationFunktionRegistrering:
            model = case(
                # Mapping from LoRa funktionsnavn to GraphQL names
                {
                    "Adresse": "address",
                    "Engagement": "engagement",
                    "IT-system": "ituser",
                    "Leder": "manager",
                    "Orlov": "leave",
                    "Rollebinding": "role",
                    "Tilknytning": "association",
                    "KLE": "kle",
                    "owner": "owner",
                    "Relateret Enhed": "related",
                },
                value=OrganisationFunktionAttrEgenskaber.funktionsnavn.cast(Text),
                else_="unknown",
            )
            query = select(model.label("model"), *common_fields).where(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                == table.id,
                registration_predicate(table, filter),
            )
            # This is the only table backing multiple models, so it is the only
            # one whose rows need filtering by model; the others are pinned by
            # the table selection above.
            if filter.models is not None:
                query = query.where(model.in_(filter.models))
            return query
        return select(
            case(
                # Mapping from table names to GraphQL names
                {
                    "BrugerRegistrering": "employee",
                    "FacetRegistrering": "facet",
                    "ITSystemRegistrering": "itsystem",
                    "KlasseRegistrering": "class",
                    "OrganisationEnhedRegistrering": "org_unit",
                },
                value=literal(table.__name__),
                else_="unknown",
            ).label("model"),
            *common_fields,
        ).where(registration_predicate(table, filter))

    # Query all requested registation tables using a big union query
    union_query = union(*map(generate_query, tables)).subquery()
    # Select using a subquery so we can order the unioned result
    # Note: I have no idea why mypy dislikes this.
    query = select("*").select_from(union_query).distinct()  # type: ignore

    # Pagination
    if cursor:  # pragma: no cover
        query = query.where(column("start") <= cursor.registration_time)
    # Order by time, then by UUID so the order of pagination is well-defined
    query = query.order_by(column("start"), column("uuid"))
    if limit is not None:
        # Fetch one extra element to see if there is another page
        query = query.limit(limit + 1)  # pragma: no cover
    query = query.offset(cursor.offset if cursor else 0)

    session: AsyncSession = info.context.session
    result = list(await session.execute(query))
    access_log(
        session,
        "resolve_registrations",
        "Registration",
        {
            "limit": limit,
            "cursor": cursor,
            "uuids": filter.uuids,
            "actors": filter.actors,
            "models": filter.models,
            "start": filter.start,
            "end": filter.end,
        },
        [uuid for _, _, uuid, _, _, _, _ in result],
    )

    if limit is not None:
        # Not enough results == no more pages
        if len(result) <= limit:  # pragma: no cover
            context["lora_page_out_of_range"] = True
        # Strip the extra element that was only used for page-checking
        elif len(result) == limit + 1:  # pragma: no cover
            result = result[:-1]

    return list(starmap(row2registration, result))
