# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from uuid import UUID

from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import update
from structlog import get_logger

from mora.auth.middleware import NO_AUTH_MIDDLEWARE_UUID
from mora.db import AsyncSession
from mora.db import BrugerRegistrering
from mora.db import BrugerRelation
from mora.db import FacetRegistrering
from mora.db import FacetRelation
from mora.db import ITSystemRegistrering
from mora.db import ITSystemRelation
from mora.db import KlasseAttrEgenskaber
from mora.db import KlasseRegistrering
from mora.db import KlasseRelation
from mora.db import KlasseRelationKode
from mora.db import LivscyklusKode
from mora.db import OrganisationEnhedRegistrering
from mora.db import OrganisationEnhedRelation
from mora.db import OrganisationFunktionRegistrering
from mora.db import OrganisationFunktionRelation
from mora.db import OrganisationRegistrering
from mora.db import OrganisationRelation
from mora.db import RolebindingRuleRevision
from mora.db import add_rolebinding_rule_revision

logger = get_logger()

_RELATIONS: list[tuple[str, Any, Any]] = [
    ("bruger", BrugerRelation, BrugerRegistrering),
    ("facet", FacetRelation, FacetRegistrering),
    ("itsystem", ITSystemRelation, ITSystemRegistrering),
    ("klasse", KlasseRelation, KlasseRegistrering),
    ("organisation", OrganisationRelation, OrganisationRegistrering),
    ("organisationenhed", OrganisationEnhedRelation, OrganisationEnhedRegistrering),
    (
        "organisationfunktion",
        OrganisationFunktionRelation,
        OrganisationFunktionRegistrering,
    ),
]


async def find_classes(
    session: AsyncSession, facet_uuid: UUID, user_key: str
) -> list[UUID]:
    """Find classes in *facet_uuid* with *user_key*."""
    current_registration = select(KlasseRegistrering.id).where(
        KlasseRegistrering.registrering_period.contains(func.now()),
        KlasseRegistrering.lifecycle != cast("Slettet", LivscyklusKode),
    )
    in_facet = select(KlasseRelation.klasse_registrering_id).where(
        KlasseRelation.rel_type == KlasseRelationKode.facet,
        KlasseRelation.rel_maal_uuid == facet_uuid,
    )
    with_user_key = select(KlasseAttrEgenskaber.klasse_registrering_id).where(
        KlasseAttrEgenskaber.brugervendtnoegle == user_key,
    )
    # A class is matched, if the current registration is in the facet and has
    # the user key we are looking for.
    matching = select(KlasseRegistrering.klasse_id).where(
        KlasseRegistrering.id.in_(current_registration),
        KlasseRegistrering.id.in_(in_facet),
        KlasseRegistrering.id.in_(with_user_key),
    )
    query = (
        select(KlasseRegistrering.klasse_id)
        .where(KlasseRegistrering.klasse_id.in_(matching))
        .group_by(KlasseRegistrering.klasse_id)
        .order_by(
            func.min(func.lower(KlasseRegistrering.registrering_period)),
            KlasseRegistrering.klasse_id,
        )
    )
    return list(await session.scalars(query))


async def merge_duplicate_classes(
    session: AsyncSession, facet_uuid: UUID, user_key: str
) -> list[UUID]:
    """Merge duplicate classes into the oldest one.

    Every reference to a duplicate is changed to point to the original instead,
    and the duplicates are deleted. This means that every registration is
    re-written in-place so reading the past is still consistent. This is in
    conflict with the bitemporal model.

    Rolebinding rules are not bitemporal, but versioned, so the current
    revision of each affected rule gets a successor with the original role.
    """
    classes = await find_classes(session, facet_uuid, user_key)
    if len(classes) < 2:
        return classes  # pragma: no cover
    original, *duplicates = classes
    log = logger.bind(original=original, duplicates=duplicates)

    # Rewriting the original's own references to a duplicate would make it
    # reference itself, e.g. as its own parent.
    original_references = await session.scalar(
        select(func.count())
        .select_from(KlasseRelation)
        .join(
            KlasseRegistrering,
            KlasseRegistrering.id == KlasseRelation.klasse_registrering_id,
        )
        .where(
            KlasseRegistrering.klasse_id == original,
            KlasseRelation.rel_maal_uuid.in_(duplicates),
        )
    )
    if original_references:
        raise ValueError(
            f"The original class {original} references a duplicate. "
            "Fix it manually before merging."
        )

    # LoRa relations
    for lora_type, relation, registration in _RELATIONS:
        registration_ids = set(
            await session.scalars(
                update(relation)
                .where(relation.rel_maal_uuid.in_(duplicates))
                .values(rel_maal_uuid=original)
                .returning(getattr(relation, f"{lora_type}_registrering_id"))
                .execution_options(synchronize_session=False)
            )
        )
        if not registration_ids:
            continue

        # The event generator emits events for registrations committed since
        # its last run, judged by `xmin`. Touching the registrations owning
        # the rewritten relations updates their `xmin`, so the event generator
        # emits events for the changed objects 👌
        table = registration.__table__
        await session.execute(
            update(table).where(table.c.id.in_(registration_ids)).values(id=table.c.id)
        )
        log.info("rewrote references", lora_type=lora_type, count=len(registration_ids))

    # Rolebinding rules
    revisions = await session.scalars(
        select(RolebindingRuleRevision).where(
            RolebindingRuleRevision.is_current(),
            RolebindingRuleRevision.role.in_(duplicates),
        )
    )
    for revision in revisions.all():
        await add_rolebinding_rule_revision(
            session, revision, actor=NO_AUTH_MIDDLEWARE_UUID, role=original
        )
        log.info("rewrote rolebinding rule", rule=revision.rule_fk)

    for duplicate in duplicates:
        await session.execute(
            text(
                "SELECT _as_create_klasse_registrering(:uuid, 'Slettet'::livscykluskode, :actor, :note)"
            ),
            {
                "uuid": duplicate,
                "actor": NO_AUTH_MIDDLEWARE_UUID,
                "note": f"Merged into class {original}",
            },
        )

    log.info("merged duplicate classes")
    return classes
