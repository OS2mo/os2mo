# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from sqlalchemy import ColumnElement
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import cast
from sqlalchemy import exists
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy.sql import union

from mora import config
from mora import util
from mora.db import BrugerAttrUdvidelser
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import OrganisationFunktionAttrEgenskaber
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationFunktionRelationKode
from mora.service.autocomplete.shared import UUID_SEARCH_MIN_PHRASE_LENGTH
from mora.service.autocomplete.shared import string_to_urn


def search_employees_predicate(query: str) -> ColumnElement:
    settings = config.get_settings()

    ctes = [
        _get_cte_uuid_hits(query),
        _get_cte_user_key_hits(query),
        _get_cte_name_hits(query),
        _get_cte_cpr_hits(query),
        _get_cte_itsystem_hits(query),
    ]
    if settings.person_address_search_enabled:
        ctes.append(_get_cte_addr_hits(query))

    selects = [select(cte.c.uuid) for cte in ctes]
    all_hits = union(*selects).cte()

    return exists(
        select(1)
        .select_from(all_hits)
        .where(all_hits.c.uuid == BrugerRegistrering.bruger_id)
    )


def _get_cte_uuid_hits(query: str):
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


def _get_cte_name_hits(query: str):
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


def _get_cte_cpr_hits(query: str):
    # NOTE: CPR is persisted as a URN in the relation tabel
    query = string_to_urn(query)
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


def _get_cte_itsystem_hits(query: str):
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


def _get_cte_user_key_hits(query: str):
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


def _get_cte_addr_hits(query: str):
    # Addresses are stored as URNs in the relation table, not in the attributes table,
    # so we self-join the relation table to find the person (tilknyttedebrugere) and
    # the address value (adresser) on the same registration.
    orgfunc_tbl_rels_1 = aliased(OrganisationFunktionRelation)
    orgfunc_tbl_rels_2 = aliased(OrganisationFunktionRelation)

    query = string_to_urn(query)
    search_phrase = util.query_to_search_phrase(query)

    return (
        select(orgfunc_tbl_rels_1.rel_maal_uuid.label("uuid"))
        .outerjoin(
            orgfunc_tbl_rels_2,
            orgfunc_tbl_rels_2.organisationfunktion_registrering_id
            == orgfunc_tbl_rels_1.organisationfunktion_registrering_id,
        )
        .where(
            orgfunc_tbl_rels_1.rel_maal_uuid != None,  # noqa: E711
            cast(orgfunc_tbl_rels_1.rel_type, String)
            == OrganisationFunktionRelationKode.tilknyttedebrugere,
            cast(orgfunc_tbl_rels_2.rel_type, String)
            == OrganisationFunktionRelationKode.adresser,
            orgfunc_tbl_rels_2.rel_maal_urn.ilike(search_phrase),
        )
        .cte()
    )
