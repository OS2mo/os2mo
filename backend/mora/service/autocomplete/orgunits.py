# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date

from mora import util
from mora.db import OrganisationEnhedAttrEgenskaber
from mora.db import OrganisationEnhedRegistrering
from mora.db._common import LivscyklusKode
from mora.service.autocomplete.shared import UUID_SEARCH_MIN_PHRASE_LENGTH
from mora.service.autocomplete.shared import get_at_date_sql
from sqlalchemy import Select
from sqlalchemy import Text
from sqlalchemy import Tuple
from sqlalchemy import cast
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import union


def search_orgunits_query(
    query: str,
    at: date | None = None,
) -> Select[Tuple]:
    at_sql, _ = get_at_date_sql(at)
    return _sqlalchemy_generate_query(query, at_sql)


def _sqlalchemy_generate_query(query: str, at_sql: str) -> Select[Tuple]:
    selects = [
        select(cte.c.uuid)
        for cte in (
            _get_cte_orgunit_uuid_hits(query, at_sql),
            _get_cte_orgunit_name_hits(query, at_sql),
        )
    ]
    all_hits = union(*selects).cte()

    query_final = (
        select(
            OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"),
        )
        .where(OrganisationEnhedRegistrering.organisationenhed_id == all_hits.c.uuid)
        .group_by(OrganisationEnhedRegistrering.organisationenhed_id)
    )

    return query_final


def _get_cte_orgunit_uuid_hits(query: str, at_sql: str):
    search_phrase = util.query_to_search_phrase(query)
    return (
        select(OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"))
        .join(
            OrganisationEnhedAttrEgenskaber,
            OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
            == OrganisationEnhedRegistrering.id,
        )
        .where(
            OrganisationEnhedRegistrering.lifecycle != cast("Slettet", LivscyklusKode),
            OrganisationEnhedRegistrering.registrering_period.contains(func.now()),
            func.char_length(search_phrase) > UUID_SEARCH_MIN_PHRASE_LENGTH,
            OrganisationEnhedRegistrering.organisationenhed_id != None,  # noqa: E711
            cast(OrganisationEnhedRegistrering.organisationenhed_id, Text).ilike(
                search_phrase
            ),
        )
        .cte()
    )


def _get_cte_orgunit_name_hits(query: str, at_sql: str):
    search_phrase = util.query_to_search_phrase(query)
    return (
        select(OrganisationEnhedRegistrering.organisationenhed_id.label("uuid"))
        .join(
            OrganisationEnhedAttrEgenskaber,
            OrganisationEnhedAttrEgenskaber.organisationenhed_registrering_id
            == OrganisationEnhedRegistrering.id,
        )
        .where(
            OrganisationEnhedRegistrering.lifecycle != cast("Slettet", LivscyklusKode),
            OrganisationEnhedRegistrering.registrering_period.contains(func.now()),
            OrganisationEnhedRegistrering.organisationenhed_id != None,  # noqa: E711
            (
                OrganisationEnhedAttrEgenskaber.enhedsnavn.ilike(search_phrase)
                | OrganisationEnhedAttrEgenskaber.brugervendtnoegle.ilike(search_phrase)
            ),
        )
        .cte()
    )
