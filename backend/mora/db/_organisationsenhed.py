# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy import and_
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import synonym

from ._common import Base
from ._common import _AttrEgenskaberMixin
from ._common import _OIOEntityMixin
from ._common import _RegistreringMixin
from ._common import _RelationMixin
from ._common import _TilsGyldighedMixin


class OrganisationEnhed(_OIOEntityMixin, Base):
    __tablename__ = "organisationenhed"


class OrganisationEnhedRegistrering(_RegistreringMixin, Base):
    __tablename__ = "organisationenhed_registrering"
    organisationenhed_id = Column(ForeignKey("organisationenhed.id"), index=True)
    uuid = synonym("organisationenhed_id")

    # Base
    attr_egenskaber: Mapped[list["OrganisationEnhedAttrEgenskaber"]] = relationship(
        back_populates="registrering",
        order_by=lambda: OrganisationEnhedAttrEgenskaber.virkning_period.asc(),
    )
    relationer: Mapped[list["OrganisationEnhedRelation"]] = relationship(
        back_populates="registrering",
        order_by=lambda: OrganisationEnhedRelation.virkning_period.asc(),
    )
    tils_gyldighed: Mapped[list["OrganisationEnhedTilsGyldighed"]] = relationship(
        back_populates="registrering",
        order_by=lambda: OrganisationEnhedTilsGyldighed.virkning_period.asc(),
    )

    # Relationer
    enhedstype: Mapped[list["OrganisationEnhedRelation"]] = relationship(
        primaryjoin=lambda: and_(
            OrganisationEnhedRegistrering.id
            == OrganisationEnhedRelation.organisationenhed_registrering_id,
            OrganisationEnhedRelation.rel_type
            == cast("enhedstype", OrganisationEnhedRelationKode),
        ),
        viewonly=True,
        order_by=lambda: OrganisationEnhedRelation.virkning_period.asc(),
    )
    niveau: Mapped[list["OrganisationEnhedRelation"]] = relationship(
        primaryjoin=lambda: and_(
            OrganisationEnhedRegistrering.id
            == OrganisationEnhedRelation.organisationenhed_registrering_id,
            OrganisationEnhedRelation.rel_type
            == cast("niveau", OrganisationEnhedRelationKode),
        ),
        viewonly=True,
        order_by=lambda: OrganisationEnhedRelation.virkning_period.asc(),
    )
    opmærkning: Mapped[list["OrganisationEnhedRelation"]] = relationship(
        primaryjoin=lambda: and_(
            OrganisationEnhedRegistrering.id
            == OrganisationEnhedRelation.organisationenhed_registrering_id,
            OrganisationEnhedRelation.rel_type
            == cast("opmærkning", OrganisationEnhedRelationKode),
        ),
        viewonly=True,
        order_by=lambda: OrganisationEnhedRelation.virkning_period.asc(),
    )
    overordnet: Mapped[list["OrganisationEnhedRelation"]] = relationship(
        primaryjoin=lambda: and_(
            OrganisationEnhedRegistrering.id
            == OrganisationEnhedRelation.organisationenhed_registrering_id,
            OrganisationEnhedRelation.rel_type
            == cast("overordnet", OrganisationEnhedRelationKode),
        ),
        viewonly=True,
        order_by=lambda: OrganisationEnhedRelation.virkning_period.asc(),
    )
    tidsregistrering: Mapped[list["OrganisationEnhedRelation"]] = relationship(
        primaryjoin=lambda: and_(
            OrganisationEnhedRegistrering.id
            == OrganisationEnhedRelation.organisationenhed_registrering_id,
            OrganisationEnhedRelation.rel_type
            == cast("opgaver", OrganisationEnhedRelationKode),
            OrganisationEnhedRelation.objekt_type == "tidsregistrering",
        ),
        viewonly=True,
        order_by=lambda: OrganisationEnhedRelation.virkning_period.asc(),
    )
    tilhoerer: Mapped[list["OrganisationEnhedRelation"]] = relationship(
        primaryjoin=lambda: and_(
            OrganisationEnhedRegistrering.id
            == OrganisationEnhedRelation.organisationenhed_registrering_id,
            OrganisationEnhedRelation.rel_type
            == cast("tilhoerer", OrganisationEnhedRelationKode),
        ),
        viewonly=True,
        order_by=lambda: OrganisationEnhedRelation.virkning_period.asc(),
    )


class OrganisationEnhedAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "organisationenhed_attr_egenskaber"

    enhedsnavn: Mapped[str | None] = mapped_column(Text, index=True)

    organisationenhed_registrering_id = Column(
        ForeignKey("organisationenhed_registrering.id"), index=True
    )
    registrering: Mapped["OrganisationEnhedRegistrering"] = relationship(
        back_populates="attr_egenskaber",
    )


OrganisationEnhedRelationKode = ENUM(
    "enhedstype",
    "niveau",
    "opgaver",
    "opmærkning",
    "overordnet",
    "tilhoerer",
    name="organisationenhedrelationkode",
)


class OrganisationEnhedRelation(_RelationMixin, Base):
    __tablename__ = "organisationenhed_relation"

    rel_type: Mapped[OrganisationEnhedRelationKode]

    organisationenhed_registrering_id = Column(
        ForeignKey("organisationenhed_registrering.id"), index=True
    )
    registrering: Mapped["OrganisationEnhedRegistrering"] = relationship(
        back_populates="relationer"
    )


class OrganisationEnhedTilsGyldighed(_TilsGyldighedMixin("organisationenhed"), Base):
    __tablename__ = "organisationenhed_tils_gyldighed"

    organisationenhed_registrering_id = Column(
        ForeignKey("organisationenhed_registrering.id"), index=True
    )
    registrering: Mapped["OrganisationEnhedRegistrering"] = relationship(
        back_populates="tils_gyldighed"
    )
