# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import datetime
from itertools import starmap
from typing import Annotated
from typing import Any
from uuid import UUID

import strawberry
from sqlalchemy import Text
from sqlalchemy import case
from sqlalchemy import column
from sqlalchemy import literal
from sqlalchemy import select
from sqlalchemy import union
from sqlalchemy.sql.expression import Select
from starlette_context import context
from strawberry.types import Info

from mora.audit import audit_log
from mora.db import BrugerRegistrering
from mora.db import FacetRegistrering
from mora.db import ITSystemRegistrering
from mora.db import KlasseRegistrering
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRegistrering
from mora.util import parsedatetime

from .filters import RegistrationFilter
from .paged import CursorType
from .paged import LimitType
from .resolvers import get_sqlalchemy_date_interval

LazyRegistration = Annotated["Registration", strawberry.lazy(".registration")]  # type: ignore  # noqa: F821


def row2registration(
    model: str, id: int, uuid: UUID, actor: UUID, note: str, start_t: Any, end_t: Any
) -> LazyRegistration:
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
    start: datetime = parsedatetime(start_t)
    end: datetime | None = parsedatetime(end_t)
    assert end is not None
    if end.date() == date(9999, 12, 31):
        end = None

    from .registration import Registration

    return Registration(  # type: ignore
        model=model,
        uuid=uuid,
        registration_id=id,
        start=start,
        end=end,
        actor=actor,
        note=note,
    )


async def registration_resolver(
    info: Info,
    filter: RegistrationFilter | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[LazyRegistration]:
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
        "kle": KlasseRegistrering,
        "leave": OrganisationFunktionRegistrering,
        "manager": OrganisationFunktionRegistrering,
        "org_unit": OrganisationEnhedRegistrering,
        "role": OrganisationFunktionRegistrering,
        # TODO: Owner
        # TODO: RelatedUnit
    }

    tables = set(model2table.values())
    # If given a model filter, only query relevant tables
    if filter.models is not None:
        valid_keys = set(filter.models) & model2table.keys()
        tables = {model2table[key] for key in valid_keys}
        # If only invalid model names were given, we can early return
        if not tables:
            return []

    def generate_query(table: Any) -> Select:
        common_fields = [
            table.id.label("id"),
            table.uuid.label("uuid"),
            table.actor.label("actor"),
            table.note.label("note"),
            table.registreringstid_start.label("start"),
            table.registreringstid_slut.label("end"),
        ]

        if table == OrganisationFunktionRegistrering:
            return select(
                case(
                    # Mapping from LoRa funktionsnavn to GraphQL names
                    {
                        "Adresse": "address",
                        "Engagement": "engagement",
                        "IT-system": "ituser",
                        "Leder": "manager",
                        "Orlov": "leave",
                        "Rolle": "role",
                        "Tilknytning": "association",
                    },
                    value=OrganisationFunktionAttrEgenskaber.funktionsnavn.cast(Text),
                    else_="unknown",
                ).label("model"),
                *common_fields,
            ).where(
                OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
                == table.id
            )
        return select(
            case(
                # Mapping from table names to GraphQL names
                {
                    "BrugerRegistrering": "employee",
                    "FacetRegistrering": "facet",
                    "ITSystemRegistrering": "itsystem",
                    "KlasseRegistrering": "class",
                    "OrganisationEnhedRegistrering": "org_unit",
                    # TODO: Handle KLE
                    # "kle": KlasseRegistrering,
                },
                value=literal(table.__name__),
                else_="unknown",
            ).label("model"),
            *common_fields,
        )

    # Query all requested registation tables using a big union query
    union_query = union(*map(generate_query, tables)).subquery()
    # Select using a subquery so we can filter and order the unioned result
    # Note: I have no idea why mypy dislikes this.
    query = select("*").select_from(union_query).distinct()  # type: ignore

    if filter.uuids is not None:
        query = query.where(column("uuid").in_(filter.uuids))

    if filter.actors is not None:
        query = query.where(column("actor").in_(filter.actors))

    if filter.models is not None:
        query = query.where(column("model").in_(filter.models))

    if filter.start is not None or filter.end is not None:
        start, end = get_sqlalchemy_date_interval(filter.start, filter.end)
        query = query.where(
            column("start") <= end,
            column("end") > start,
        )

    # Pagination
    if cursor:
        query = query.where(column("start") <= cursor.registration_time)
    # Order by time, then by UUID so the order of pagination is well-defined
    query = query.order_by(column("start"), column("uuid"))
    if limit is not None:
        # Fetch one extra element to see if there is another page
        query = query.limit(limit + 1)
    query = query.offset(cursor.offset if cursor else 0)

    session = info.context["session"]
    result = list(await session.execute(query))
    audit_log(
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
        if len(result) <= limit:
            context["lora_page_out_of_range"] = True
        # Strip the extra element that was only used for page-checking
        elif len(result) == limit + 1:
            result = result[:-1]

    result = list(starmap(row2registration, result))
    return result
