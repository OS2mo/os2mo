# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import enum
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
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
    organisationenhed_id: Mapped[UUID] = mapped_column(
        ForeignKey("organisationenhed.id"), index=True
    )
    uuid = synonym("organisationenhed_id")


class OrganisationEnhedAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "organisationenhed_attr_egenskaber"

    enhedsnavn: Mapped[str | None] = mapped_column(Text, index=True)

    organisationenhed_registrering_id = Column(
        ForeignKey("organisationenhed_registrering.id"), index=True
    )


class OrganisationEnhedRelationKode(enum.StrEnum):
    enhedstype = enum.auto()
    niveau = enum.auto()
    opgaver = enum.auto()
    opmærkning = enum.auto()
    overordnet = enum.auto()
    tilhoerer = enum.auto()


class OrganisationEnhedRelation(_RelationMixin, Base):
    __tablename__ = "organisationenhed_relation"

    rel_type: Mapped[OrganisationEnhedRelationKode] = mapped_column(
        Enum(OrganisationEnhedRelationKode, name="organisationenhedrelationkode")
    )

    organisationenhed_registrering_id = Column(
        ForeignKey("organisationenhed_registrering.id"), index=True
    )


class OrganisationEnhedTilsGyldighed(_TilsGyldighedMixin("organisationenhed"), Base):
    __tablename__ = "organisationenhed_tils_gyldighed"

    organisationenhed_registrering_id = Column(
        ForeignKey("organisationenhed_registrering.id"), index=True
    )
