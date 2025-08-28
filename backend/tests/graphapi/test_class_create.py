# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import timedelta

from psycopg.types.range import TimestamptzRange

from mora.db import AsyncSession
from mora.db._klasse import KlasseRegistrering
from mora.db._klasse import KlasseAttrEgenskaber
from mora.db._klasse import KlasseAttrEgenskaberSoegeord
from mora.db._klasse import KlasseRelation
from mora.db._klasse import KlasseTilsPubliceret
from collections.abc import Callable
from typing import Any
from uuid import uuid4
from uuid import UUID
import pytest
from sqlalchemy import select


async def create_class_sql(empty_db: AsyncSession, input: dict[str, Any]) -> UUID:
    return uuid4()


def compare_timestamptz_range(
    a: TimestamptzRange,
    b: TimestamptzRange
) -> None:
    assert a.lower_inf == b.lower_inf
    assert b.upper_inf == b.upper_inf
    assert a.bounds == b.bounds
    assert a.lower_inc == b.lower_inc
    assert a.upper_inc == b.upper_inc

    if a.lower is not None:
        assert b.lower is not None
        assert a.lower - b.lower < timedelta(seconds=5)
    if a.upper is not None:
        assert b.upper is not None
        assert a.upper - b.upper < timedelta(seconds=5)


async def compare_class_registration(
    empty_db: AsyncSession,
    graphql_uuid: UUID,
    sql_uuid: UUID
) -> tuple[int, int]:
    graphql_registration = await empty_db.scalar(
        select(KlasseRegistrering).where(KlasseRegistrering.uuid==graphql_uuid)
    )
    sql_registration = await empty_db.scalar(
        select(KlasseRegistrering).where(KlasseRegistrering.uuid==sql_uuid)
    )
    assert graphql_registration is not None
    assert sql_registration is not None

    assert graphql_registration.id != sql_registration.id
    
    assert graphql_registration.actor == sql_registration.actor
    assert graphql_registration.note == sql_registration.note
    assert graphql_registration.lifecycle == sql_registration.lifecycle

    compare_timestamptz_range(graphql_registration.registrering_period, sql_registration.registrering_period)

    return graphql_registration.id, sql_registration.id


async def compare_class_attributes(
    empty_db: AsyncSession,
    graphql_registration_id: int,
    sql_registration_id: int
) -> None:
    graphql_attributes = (await empty_db.scalars(
        select(KlasseAttrEgenskaber).where(KlasseAttrEgenskaber.klasse_registrering_id==graphql_registration_id)
    )).all()
    sql_attributes = (await empty_db.scalars(
        select(KlasseAttrEgenskaber).where(KlasseAttrEgenskaber.klasse_registrering_id==sql_registration_id)
    )).all()

    assert len(graphql_attributes) == len(sql_attributes)
    for graphql_attribute, sql_attribute in zip(graphql_attributes, sql_attributes, strict=True):
        assert graphql_attribute.id != sql_attribute.id
        assert graphql_attribute.brugervendtnoegle == sql_attribute.brugervendtnoegle

        assert graphql_attribute.titel == sql_attribute.titel
        assert graphql_attribute.beskrivelse == sql_attribute.beskrivelse
        assert graphql_attribute.eksempel == sql_attribute.eksempel
        assert graphql_attribute.omfang == sql_attribute.omfang
        assert graphql_attribute.retskilde == sql_attribute.retskilde
        assert graphql_attribute.aendringsnotat == sql_attribute.aendringsnotat

        compare_timestamptz_range(graphql_attribute.virkning_period, sql_attribute.virkning_period)

        await compare_class_attributes_soegeord(
            empty_db, graphql_attribute.id, sql_attribute.id
        )


async def compare_class_attributes_soegeord(
    empty_db: AsyncSession,
    graphql_attr_egenskaber_id: int,
    sql_attr_egenskaber_id: int
) -> None:
    graphql_attributes = (await empty_db.scalars(
        select(KlasseAttrEgenskaberSoegeord).where(KlasseAttrEgenskaberSoegeord.klasse_attr_egenskaber_id==graphql_attr_egenskaber_id)
    )).all()
    sql_attributes = (await empty_db.scalars(
        select(KlasseAttrEgenskaberSoegeord).where(KlasseAttrEgenskaberSoegeord.klasse_attr_egenskaber_id==sql_attr_egenskaber_id)
    )).all()

    assert len(graphql_attributes) == len(sql_attributes)
    for graphql_attribute, sql_attribute in zip(graphql_attributes, sql_attributes, strict=True):
        assert graphql_attribute.id != sql_attribute.id

        assert graphql_attribute.soegeordidentifikator == sql_attribute.soegeordidentifikator
        assert graphql_attribute.beskrivelse == sql_attribute.beskrivelse
        assert graphql_attribute.soegeordskategori == sql_attribute.soegeordskategori

        compare_timestamptz_range(graphql_attribute.virkning_period, sql_attribute.virkning_period)


async def compare_class_relations(
    empty_db: AsyncSession,
    graphql_registration_id: int,
    sql_registration_id: int
) -> None:
    graphql_relations = (await empty_db.scalars(
        select(KlasseRelation).where(KlasseRelation.klasse_registrering_id==graphql_registration_id)
    )).all()
    sql_relations = (await empty_db.scalars(
        select(KlasseRelation).where(KlasseRelation.klasse_registrering_id==sql_registration_id)
    )).all()

    assert len(graphql_relations) == len(sql_relations)
    for graphql_relation, sql_relation in zip(graphql_relations, sql_relations, strict=True):
        assert graphql_relation.id != sql_relation.id

        assert graphql_relation.rel_maal_uuid == sql_relation.rel_maal_uuid
        assert graphql_relation.rel_maal_urn == sql_relation.rel_maal_urn
        assert graphql_relation.objekt_type == sql_relation.objekt_type
        assert graphql_relation.rel_type == sql_relation.rel_type

        compare_timestamptz_range(graphql_relation.virkning_period, sql_relation.virkning_period)


async def compare_class_published(
    empty_db: AsyncSession,
    graphql_registration_id: int,
    sql_registration_id: int
) -> None:
    graphql_publisheds = (await empty_db.scalars(
        select(KlasseTilsPubliceret).where(KlasseTilsPubliceret.klasse_registrering_id==graphql_registration_id)
    )).all()
    sql_publisheds = (await empty_db.scalars(
        select(KlasseTilsPubliceret).where(KlasseTilsPubliceret.klasse_registrering_id==sql_registration_id)
    )).all()

    assert len(graphql_publisheds) == len(sql_publisheds)
    for graphql_published, sql_published in zip(graphql_publisheds, sql_publisheds, strict=True):
        assert graphql_published.id != sql_published.id

        assert graphql_published.publiceret == sql_published.publiceret

        compare_timestamptz_range(graphql_published.virkning_period, sql_published.virkning_period)


@pytest.mark.integration_test
async def test_class_create(
    empty_db: AsyncSession,
    role_facet: UUID,
    create_class: Callable[[dict[str, Any]], UUID]
) -> None:
    class_create_payload = {
        "user_key": "admin",
        "name": "Administrator",
        "facet_uuid": str(role_facet),
        "validity": {"from": "1970-01-01"},
    }

    # Create a class using GraphQL
    graphql_class_uuid = create_class(class_create_payload)
    # Create a class using SQL
    # sql_class_uuid = create_class(class_create_payload)
    sql_class_uuid = await create_class_sql(empty_db, class_create_payload)

    assert graphql_class_uuid != sql_class_uuid
    graphql_registration_id, sql_registration_id = await compare_class_registration(
        empty_db, graphql_class_uuid, sql_class_uuid
    )
    await compare_class_attributes(
        empty_db, graphql_registration_id, sql_registration_id
    )
    await compare_class_relations(
        empty_db, graphql_registration_id, sql_registration_id
    )
    await compare_class_published(
        empty_db, graphql_registration_id, sql_registration_id
    )
