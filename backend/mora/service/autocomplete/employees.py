# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from datetime import date
from uuid import UUID

from mora import util
from mora.access_log import access_log
from mora.db import AsyncSession
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.graphapi.versions.latest.paged import CursorType
from mora.graphapi.versions.latest.paged import LimitType
from mora.service.autocomplete.shared import UUID_SEARCH_MIN_PHRASE_LENGTH
from mora.service.autocomplete.shared import get_at_date_sql
from mora.service.autocomplete.shared import read_sqlalchemy_result
from mora.service.autocomplete.shared import string_to_urn
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import cast
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import union


async def search_employees(
    session: AsyncSession,
    query: str,
    at: date | None = None,
    limit: LimitType = None,
    cursor: CursorType = None,
) -> list[UUID]:
    at_sql, at_sql_bind_params = get_at_date_sql(at)

    ctes = await asyncio.gather(
        _get_cte_uuid_hits(query),
        _get_cte_user_key_hits(query),
        _get_cte_name_hits(query),
        _get_cte_cpr_hits(query),
        _get_cte_itsystem_hits(query),
    )
    selects = [select(cte.c.uuid) for cte in ctes]
    all_hits = union(*selects).cte()

    employee_id = BrugerRegistrering.bruger_id.label("uuid")
    query_final = (
        select(employee_id).where(employee_id == all_hits.c.uuid).group_by(employee_id)
    )

    # Pagination
    if limit is not None:
        query_final = query_final.limit(limit)
    if cursor is not None:
        query_final = query_final.offset(cursor.offset)

    # Execute & parse results
    result = read_sqlalchemy_result(
        await session.execute(query_final, {**at_sql_bind_params})
    )
    uuids = [employee.uuid for employee in result]
    access_log(session, "search_employees", "Bruger", {"query": query, "at": at}, uuids)
    return uuids


async def _get_cte_uuid_hits(query: str):
    search_phrase = util.query_to_search_phrase(query)

    return (
        select(BrugerRegistrering.bruger_id.label("uuid"))
        .join(
            # OBS: We join on this table to get validity of the UUID
            # QUESTION: Should we change this join on "BrugerAttrEgenskaber" where the BVN resides,
            # which should work as an alias for the UUID ?
            BrugerAttrUdvidelser,
            BrugerAttrUdvidelser.bruger_registrering_id == BrugerRegistrering.id,
        )
        .where(
            func.char_length(search_phrase) > UUID_SEARCH_MIN_PHRASE_LENGTH,
            BrugerRegistrering.bruger_id != None,  # noqa: E711
            cast(BrugerRegistrering.bruger_id, Text).ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_name_hits(query: str):
    search_phrase = util.query_to_search_phrase(query)

    name_concated = func.concat(
        BrugerAttrUdvidelser.fornavn,
        " ",
        BrugerAttrUdvidelser.efternavn,
        " ",
        BrugerAttrUdvidelser.kaldenavn_fornavn,
        " ",
        BrugerAttrUdvidelser.kaldenavn_efternavn,
    )

    return (
        select(BrugerRegistrering.bruger_id.label("uuid"))
        .join(
            BrugerAttrUdvidelser,
            BrugerAttrUdvidelser.bruger_registrering_id == BrugerRegistrering.id,
        )
        .where(
            BrugerRegistrering.bruger_id != None,  # noqa: E711
            name_concated.ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_cpr_hits(query: str):
    # NOTE: CPR is persisted as a URN in the relation tabel
    query = await string_to_urn(query)
    search_phrase = util.query_to_search_phrase(query)

    return (
        select(BrugerRegistrering.bruger_id.label("uuid"))
        .join(
            BrugerRelation,
            BrugerRelation.bruger_registrering_id == BrugerRegistrering.id,
        )
        .where(
            BrugerRegistrering.bruger_id != None,  # noqa: E711
            BrugerRelation.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_itsystem_hits(query: str):
    search_phrase = util.query_to_search_phrase(query)
    return (
        select(OrganisationFunktionRelation.rel_maal_uuid.label("uuid"))
        .outerjoin(
            OrganisationFunktionAttrEgenskaber,
            OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            == OrganisationFunktionRelation.organisationfunktion_registrering_id,
        )
        .where(
            OrganisationFunktionRelation.rel_maal_uuid != None,  # noqa: E711
            cast(OrganisationFunktionRelation.rel_type, String)
            == OrganisationFunktionRelationKode.tilknyttedebrugere,
            OrganisationFunktionAttrEgenskaber.funktionsnavn == "IT-system",
            OrganisationFunktionAttrEgenskaber.brugervendtnoegle.ilike(search_phrase),
        )
        .cte()
    )


async def _get_cte_user_key_hits(query: str):
    search_phrase = util.query_to_search_phrase(query)
    return (
        select(OrganisationFunktionRelation.rel_maal_uuid.label("uuid"))
        .outerjoin(
            OrganisationFunktionAttrEgenskaber,
            OrganisationFunktionAttrEgenskaber.organisationfunktion_registrering_id
            == OrganisationFunktionRelation.organisationfunktion_registrering_id,
        )
        .where(
            OrganisationFunktionRelation.rel_maal_uuid != None,  # noqa: E711
            cast(OrganisationFunktionRelation.rel_type, String)
            == OrganisationFunktionRelationKode.tilknyttedebrugere,
            OrganisationFunktionAttrEgenskaber.funktionsnavn == "Engagement",
            OrganisationFunktionAttrEgenskaber.brugervendtnoegle.ilike(search_phrase),
        )
        .cte()
    )
