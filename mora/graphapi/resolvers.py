# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import dataclasses
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
from more_itertools import unique_everseen
from psycopg.types.range import TimestamptzRange
from pydantic import ValidationError
from sqlalchemy import ColumnElement
from sqlalchemy import CompoundSelect
from sqlalchemy import Select
from sqlalchemy import all_
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
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import aliased
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
from mora.db import OrganisationRegistrering
from mora.graphapi.context import MOInfo
from mora.graphapi.custom_schema import get_version
from mora.graphapi.gmodels.base import tz_isodate
from mora.graphapi.version import Version
from mora.service.autocomplete.employees import search_employees_predicate
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


def employee_subfilter(filter: Any) -> EmployeeFilter:
    employee_filter = filter.employee or EmployeeFilter()
    # Handle deprecated filter
    extend_uuids(employee_filter, filter.employees)
    return employee_filter


def org_unit_subfilter(filter: Any) -> OrganisationUnitFilter:
    org_unit_filter = filter.org_unit or OrganisationUnitFilter()
    # Handle deprecated filter
    extend_uuids(org_unit_filter, filter.org_units)
    return org_unit_filter


def engagement_subfilter(filter: Any) -> EngagementFilter:
    engagement_filter = filter.engagement or EngagementFilter()
    # Handle deprecated filter
    extend_uuids(engagement_filter, filter.engagements)
    return engagement_filter


def itsystem_subfilter(filter: Any) -> ITSystemFilter:
    itsystem_filter = filter.itsystem or ITSystemFilter()
    # Handle deprecated filter
    extend_uuids(itsystem_filter, filter.itsystem_uuids)
    return itsystem_filter


def facet_parent_subfilter(filter: Any) -> FacetFilter:
    parent_filter = filter.parent or FacetFilter()
    # Handle deprecated filter
    extend_uuids(parent_filter, filter.parents)
    extend_user_keys(parent_filter, filter.parent_user_keys)
    return parent_filter


def class_facet_subfilter(filter: Any) -> FacetFilter:
    facet_filter = filter.facet or FacetFilter()
    # Handle deprecated filter
    extend_uuids(facet_filter, filter.facets)
    extend_user_keys(facet_filter, filter.facet_user_keys)
    return facet_filter


def class_parent_subfilter(filter: Any) -> ClassFilter:
    parent_filter = filter.parent or ClassFilter()
    # Handle deprecated filter
    extend_uuids(parent_filter, filter.parents)
    extend_user_keys(parent_filter, filter.parent_user_keys)
    return parent_filter


def address_type_subfilter(filter: Any) -> ClassFilter:
    address_type_filter = filter.address_type or ClassFilter()
    # Handle deprecated filter
    extend_uuids(address_type_filter, filter.address_types)
    extend_user_keys(address_type_filter, filter.address_type_user_keys)
    return address_type_filter


def association_type_subfilter(filter: Any) -> ClassFilter:
    association_type_filter = filter.association_type or ClassFilter()
    # Handle deprecated filter
    extend_uuids(association_type_filter, filter.association_types)
    extend_user_keys(association_type_filter, filter.association_type_user_keys)
    return association_type_filter


def hierarchy_subfilter(filter: Any) -> ClassFilter:
    hierarchy_filter = filter.hierarchy or ClassFilter()
    # Handle deprecated filter
    extend_uuids(hierarchy_filter, filter.hierarchies)
    return hierarchy_filter


def facet_predicate(
    info: MOInfo,
    filter: FacetFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
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
        predicates.append(
            FacetRegistrering.id.in_(
                select(FacetRelation.facet_registrering_id).where(
                    FacetRelation.rel_type == FacetRelationKode.facettilhoerer,
                    FacetRelation.rel_maal_uuid.in_(
                        select(FacetRegistrering.facet_id).where(
                            facet_predicate(
                                info, facet_parent_subfilter(filter), registration_time
                            )
                        )
                    ),
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

    predicate = facet_predicate(
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


def class_predicate(
    info: MOInfo,
    filter: ClassFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
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
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseRelation.klasse_registrering_id).where(
                    KlasseRelation.rel_type == KlasseRelationKode.facet,
                    KlasseRelation.rel_maal_uuid.in_(
                        select(FacetRegistrering.facet_id).where(
                            facet_predicate(
                                info, class_facet_subfilter(filter), registration_time
                            )
                        )
                    ),
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
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseRelation.klasse_registrering_id).where(
                    KlasseRelation.rel_type == KlasseRelationKode.overordnetklasse,
                    KlasseRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info, class_parent_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(KlasseRelation, filter),
                )
            )
        )

    # IT system
    if filter.it_system is not None:
        predicates.append(
            KlasseRegistrering.id.in_(
                select(KlasseRelation.klasse_registrering_id).where(
                    KlasseRelation.rel_type == KlasseRelationKode.mapninger,
                    KlasseRelation.rel_maal_uuid.in_(
                        select(ITSystemRegistrering.itsystem_id).where(
                            it_system_predicate(
                                info, filter.it_system, registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(KlasseRelation, filter),
                )
            )
        )

    # Owner
    if filter.owner is not None:
        matched_owner = KlasseRegistrering.id.in_(
            select(KlasseRelation.klasse_registrering_id).where(
                KlasseRelation.rel_type == KlasseRelationKode.ejer,
                KlasseRelation.rel_maal_uuid.in_(
                    select(OrganisationEnhedRegistrering.organisationenhed_id).where(
                        organisation_unit_predicate(
                            info, filter.owner, registration_time
                        )
                    )
                ),
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

    predicate = class_predicate(
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


def address_predicate(
    info: MOInfo,
    filter: AddressFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(BrugerRegistrering.bruger_id).where(
                            employee_predicate(
                                info, employee_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info, address_type_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Visibility
    # rel_type "opgaver" with objekt_type "synlighed" in mox
    # TODO: Support finding entries with visibility=None
    if filter.visibility is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.opgaver,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(info, filter.visibility, registration_time)
                        )
                    ),
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
        tilknyttedefunktioner: list[Select] = []
        if filter.engagement is not None or filter.engagements is not None:
            tilknyttedefunktioner.append(
                select(OrganisationFunktionRegistrering.organisationfunktion_id).where(
                    engagement_predicate(
                        info, engagement_subfilter(filter), registration_time
                    )
                )
            )
        if filter.ituser is not None:
            tilknyttedefunktioner.append(
                select(OrganisationFunktionRegistrering.organisationfunktion_id).where(
                    it_user_predicate(info, filter.ituser, registration_time)
                )
            )
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        union(*tilknyttedefunktioner)
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

    predicate = address_predicate(
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


def association_predicate(
    info: MOInfo,
    filter: AssociationFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(BrugerRegistrering.bruger_id).where(
                            employee_predicate(
                                info, employee_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info,
                                association_type_subfilter(filter),
                                registration_time,
                            )
                        )
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

    predicate = association_predicate(
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


def employee_predicate(
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

    # Query search
    if filter.query:
        predicates.append(search_employees_predicate(filter.query))

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

    predicate = employee_predicate(
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


def engagement_predicate(
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(BrugerRegistrering.bruger_id).where(
                            employee_predicate(
                                info, employee_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Job function
    if filter.job_function is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.opgaver,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info, filter.job_function, registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Engagement type
    if filter.engagement_type is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info, filter.engagement_type, registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # IT user
    # The `tilknyttedefunktioner` relation lives on the ITUser's registration
    # pointing at the engagement UUID; resolve via the ituser predicate.
    if filter.ituser is not None:
        ituser_pred = it_user_predicate(
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

    predicate = engagement_predicate(
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


def _managers_for_employee(
    info: MOInfo,
    employee_filter: EmployeeFilter,
    filter: BaseFilter,
    registration_time: datetime | SQLNOW,
) -> Select:
    """Registrering ids of managers whose person matches `employee_filter`.

    The manager's person is the `tilknyttedebrugere` relation target.
    """
    return select(
        OrganisationFunktionRelation.organisationfunktion_registrering_id
    ).where(
        OrganisationFunktionRelation.rel_type
        == OrganisationFunktionRelationKode.tilknyttedebrugere,
        OrganisationFunktionRelation.rel_maal_uuid.in_(
            select(BrugerRegistrering.bruger_id).where(
                employee_predicate(info, employee_filter, registration_time)
            )
        ),
        _get_virkning_clause(OrganisationFunktionRelation, filter),
    )


def manager_predicate(
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
            predicates.append(
                OrganisationFunktionRegistrering.id.in_(
                    _managers_for_employee(
                        info, employee_subfilter(filter), filter, registration_time
                    )
                )
            )
    elif (
        filter.employee is not None and filter.employee is not UNSET
    ) or filter.employees is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                _managers_for_employee(
                    info, employee_subfilter(filter), filter, registration_time
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Responsibility
    if filter.responsibility is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.opgaver,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info, filter.responsibility, registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Manager type
    if filter.manager_type is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info, filter.manager_type, registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Engagement
    if filter.engagement is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationFunktionRegistrering.organisationfunktion_id
                        ).where(
                            engagement_predicate(
                                info, filter.engagement, registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Exclude: drop managers whose person matches `filter.exclude`.
    if filter.exclude is not None:
        predicates.append(
            ~OrganisationFunktionRegistrering.id.in_(
                _managers_for_employee(info, filter.exclude, filter, registration_time)
            )
        )

    return and_(*predicates)


def _inherited_managers_query(
    info: MOInfo,
    filter: ManagerFilter,
    registration_time: datetime | SQLNOW,
) -> Select:
    """Manager UUIDs of the nearest ancestor (incl. itself) of the filtered units.

    `managers(inherit: true)` returns the managers of an organisation unit, or -- if
    it has none -- those of its nearest ancestor that does. This walks the org tree
    upwards in a single recursive CTE and returns the manager org-function UUIDs at
    the smallest depth that has matching managers, rather than issuing one query per
    tree level as the previous Python recursion did.
    """
    # Ancestor chain, one per starting unit. Like the `descendant`/`ancestor`
    # org-unit filters this walks `overordnet` parents in a recursive CTE, but it
    # also carries:
    # * `origin` -- the starting unit, so the nearest ancestor is chosen per unit
    #   rather than globally (different units inherit independently);
    # * `depth`  -- distance from `origin`, to rank ancestors;
    # * `path`   -- the units visited so far, to terminate on cyclic data (the
    #   plain `uuid`-deduplicating CTEs can't, once `depth` makes rows distinct).
    # Only active (`Aktiv`) units are traversed, matching the starting set and the
    # old recursion which routed every ancestor through `organisation_unit_predicate`.
    anchor = select(
        OrganisationEnhedRegistrering.organisationenhed_id.label("origin"),
        OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"),
        literal(0).label("depth"),
        array([OrganisationEnhedRegistrering.organisationenhed_id]).label("path"),
    ).where(
        organisation_unit_predicate(info, org_unit_subfilter(filter), registration_time)
    )
    ancestors = anchor.cte("ancestors", recursive=True)
    # Independent subquery of all active units. Used to gate parents to active units
    # without a second `organisationenhed_registrering` in the recursive FROM (its
    # `(registrering)` composite would be ambiguous with the child's). `correlate`
    # keeps it from being folded into the outer query.
    active_units = (
        select(OrganisationEnhedRegistrering.organisationenhed_id)
        .where(
            organisation_unit_predicate(
                info, OrganisationUnitFilter(), registration_time
            )
        )
        .correlate(None)
    )
    parents = (
        select(
            ancestors.c.origin,
            OrganisationEnhedRelation.rel_maal_uuid,
            ancestors.c.depth + 1,
            func.array_append(
                ancestors.c.path, OrganisationEnhedRelation.rel_maal_uuid
            ),
        )
        .select_from(ancestors)
        .join(
            OrganisationEnhedRegistrering,
            OrganisationEnhedRegistrering.organisationenhed_id == ancestors.c.uuid,
        )
        .join(
            OrganisationEnhedRelation,
            and_(
                OrganisationEnhedRelation.organisationenhed_registrering_id
                == OrganisationEnhedRegistrering.id,
                OrganisationEnhedRelation.rel_type
                == OrganisationEnhedRelationKode.overordnet,
                _get_virkning_clause(OrganisationEnhedRelation, filter),
            ),
        )
        .where(
            _get_registrering_clause(OrganisationEnhedRegistrering, registration_time),
            OrganisationEnhedRelation.rel_maal_uuid != all_(ancestors.c.path),
            OrganisationEnhedRelation.rel_maal_uuid.in_(active_units),
        )
    )
    ancestors = ancestors.union_all(parents)

    # All manager constraints except the org unit, which is supplied via the
    # ancestor join below. `exclude` lives in `manager_predicate`, so a level whose
    # managers are all excluded is naturally skipped (the old recursion moved on
    # when a level came back empty).
    base_filter = dataclasses.replace(filter, org_units=None, org_unit=None)
    base_predicate = manager_predicate(info, base_filter, registration_time)

    # Managers attached to any ancestor, tagged with the starting unit and depth. A
    # separate alias for the org-unit relation keeps it distinct from the relation
    # used inside `manager_predicate`'s own subqueries.
    org_unit_relation = aliased(OrganisationFunktionRelation)
    attached = (
        select(
            OrganisationFunktionRegistrering.organisationfunktion_id.label("uuid"),
            ancestors.c.origin.label("origin"),
            ancestors.c.depth.label("depth"),
        )
        .select_from(ancestors)
        .join(
            org_unit_relation,
            and_(
                org_unit_relation.rel_maal_uuid == ancestors.c.uuid,
                org_unit_relation.rel_type
                == OrganisationFunktionRelationKode.tilknyttedeenheder,
                _get_virkning_clause(org_unit_relation, filter),
            ),
        )
        .join(
            OrganisationFunktionRegistrering,
            OrganisationFunktionRegistrering.id
            == org_unit_relation.organisationfunktion_registrering_id,
        )
        .where(base_predicate)
    ).cte("attached_managers")

    # For each starting unit keep the managers at its smallest depth that has any --
    # i.e. those of that unit's nearest ancestor (incl. itself) with managers.
    same_origin = attached.alias("same_origin")
    nearest_depth = (
        select(func.min(same_origin.c.depth))
        .where(same_origin.c.origin == attached.c.origin)
        .scalar_subquery()
    )
    return select(distinct(attached.c.uuid)).where(attached.c.depth == nearest_depth)


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
    registration_time = _get_registration_time(filter, cursor)

    if inherit:
        # `inherit` matches the managers of the nearest ancestor that has any
        # (including the unit itself), resolved in a single recursive query.
        if filter.org_units is None and filter.org_unit is None:
            raise ValueError("The inherit flag requires an organizational unit filter")
        predicate = OrganisationFunktionRegistrering.organisationfunktion_id.in_(
            _inherited_managers_query(info, filter, registration_time)
        )
    else:
        predicate = manager_predicate(info, filter, registration_time)

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

    return await generic_resolver(
        info.context.dataloaders.manager_loader,
        uuids=uuids,
        from_date=filter.from_date,
        to_date=filter.to_date,
        registration_time=filter.registration_time,
    )


def owner_predicate(
    info: MOInfo,
    filter: OwnerFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(BrugerRegistrering.bruger_id).where(
                            employee_predicate(
                                info, employee_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Owner
    if filter.owner is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedepersoner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(BrugerRegistrering.bruger_id).where(
                            employee_predicate(info, filter.owner, registration_time)
                        )
                    ),
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

    predicate = owner_predicate(
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


def organisation_unit_predicate(
    info: MOInfo,
    filter: OrganisationUnitFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
    def _parents_subquery() -> Select | CompoundSelect:
        org_unit_filter = filter.parent or OrganisationUnitFilter()
        # parents vs parent values
        #       | UNSET | None    | xs
        # UNSET | noop  | root    | xs
        # None  | root  | root    | root+xs
        # ys    | ys    | root+ys | xs+ys
        #
        # The above assignment handles all parent=ys cases
        # Thus we only need to check for parents=xs and Nones

        # Top-level units don't have parent=null, they have
        # parent=root-org-uuid, which isn't even an org unit in the database.
        if filter.parents is None or filter.parent is None:
            return select(OrganisationRegistrering.organisation_id)
        if filter.parents is not UNSET:
            extend_uuids(org_unit_filter, filter.parents)
        return union(
            select(OrganisationEnhedRegistrering.organisationenhed_id).where(
                organisation_unit_predicate(info, org_unit_filter, registration_time)
            ),
            # Because the root unit isn't an org unit in the database, the
            # organisation_unit_predicate can't fetch it. Instead, we include
            # the root organisation's UUID directly whenever it's among the
            # requested parent UUIDs.
            select(OrganisationRegistrering.organisation_id).where(
                OrganisationRegistrering.organisation_id.in_(
                    org_unit_filter.uuids or []
                )
            ),
        )

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
                            engagement_predicate(
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
        predicates.append(
            OrganisationEnhedRegistrering.id.in_(
                select(
                    OrganisationEnhedRelation.organisationenhed_registrering_id
                ).where(
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.overordnet,
                    OrganisationEnhedRelation.rel_maal_uuid.in_(_parents_subquery()),
                    _get_virkning_clause(OrganisationEnhedRelation, filter),
                )
            )
        )

    # Hierarchies
    if filter.hierarchy is not None or filter.hierarchies is not None:
        predicates.append(
            OrganisationEnhedRegistrering.id.in_(
                select(
                    OrganisationEnhedRelation.organisationenhed_registrering_id
                ).where(
                    OrganisationEnhedRelation.rel_type
                    == OrganisationEnhedRelationKode.opmærkning,
                    OrganisationEnhedRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(
                                info, hierarchy_subfilter(filter), registration_time
                            )
                        )
                    ),
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
        base_leafs_predicate = organisation_unit_predicate(
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
        child_predicate = organisation_unit_predicate(
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
        ancestor_predicate = organisation_unit_predicate(
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

    predicate = organisation_unit_predicate(
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
    predicate = organisation_unit_predicate(
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
    predicate = organisation_unit_predicate(
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


def it_system_predicate(
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

    predicate = it_system_predicate(
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


def it_user_predicate(
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(BrugerRegistrering.bruger_id).where(
                            employee_predicate(
                                info, employee_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # IT systems
    if filter.itsystem_uuids is not None or filter.itsystem is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeitsystemer,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(ITSystemRegistrering.itsystem_id).where(
                            it_system_predicate(
                                info, itsystem_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Engagement
    if filter.engagement is not None:  # pragma: no cover
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationFunktionRegistrering.organisationfunktion_id
                        ).where(
                            engagement_predicate(
                                info, filter.engagement, registration_time
                            )
                        )
                    ),
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

    predicate = it_user_predicate(
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


def kle_predicate(
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
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

    predicate = kle_predicate(
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


def leave_predicate(
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedebrugere,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(BrugerRegistrering.bruger_id).where(
                            employee_predicate(
                                info, employee_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Org units
    if filter.org_units is not None or filter.org_unit is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
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

    predicate = leave_predicate(
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


def related_unit_predicate(
    info: MOInfo,
    filter: RelatedUnitFilter,
    registration_time: datetime | SQLNOW,
) -> ColumnElement:
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
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

    predicate = related_unit_predicate(
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


def rolebinding_predicate(
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
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedeenheder,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationEnhedRegistrering.organisationenhed_id
                        ).where(
                            organisation_unit_predicate(
                                info, org_unit_subfilter(filter), registration_time
                            )
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # IT-user
    if filter.ituser is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.tilknyttedefunktioner,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(
                            OrganisationFunktionRegistrering.organisationfunktion_id
                        ).where(
                            it_user_predicate(info, filter.ituser, registration_time)
                        )
                    ),
                    _get_virkning_clause(OrganisationFunktionRelation, filter),
                )
            )
        )

    # Role
    if filter.role is not None:
        predicates.append(
            OrganisationFunktionRegistrering.id.in_(
                select(
                    OrganisationFunktionRelation.organisationfunktion_registrering_id
                ).where(
                    OrganisationFunktionRelation.rel_type
                    == OrganisationFunktionRelationKode.organisatoriskfunktionstype,
                    OrganisationFunktionRelation.rel_maal_uuid.in_(
                        select(KlasseRegistrering.klasse_id).where(
                            class_predicate(info, filter.role, registration_time)
                        )
                    ),
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

    predicate = rolebinding_predicate(
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

    if filter.actors is not None:
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
