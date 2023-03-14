# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal

from sqlalchemy import ARRAY
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ._common import _AttrEgenskaberMixin
from ._common import _OIOEntityMixin
from ._common import _RegistreringMixin
from ._common import _RelationMixin
from ._common import _TilsGyldighedMixin
from ._common import Base


class ITSystem(_OIOEntityMixin, Base):
    __tablename__ = "itsystem"


class ITSystemRegistrering(_RegistreringMixin, Base):
    __tablename__ = "itsystem_registrering"
    itsystem_id = Column(ForeignKey("itsystem.id"), index=True)


class ITSystemAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "itsystem_attr_egenskaber"

    itsystemnavn: Mapped[str | None] = mapped_column(Text, index=True)
    itsystemtype: Mapped[str | None] = mapped_column(Text, index=True)
    konfigurationreference = Column(ARRAY(Text()))

    itsystem_registrering_id = Column(
        ForeignKey("itsystem_registrering.id"), index=True
    )


ITSystemRelationKode = Literal[
    "tilhoerer",
    "tilknyttedeorganisationer",
    "tilknyttedeenheder",
    "tilknyttedefunktioner",
    "tilknyttedebrugere",
    "tilknyttedeinteressefaellesskaber",
    "tilknyttedeitsystemer",
    "tilknyttedepersoner",
    "systemtyper",
    "opgaver",
    "adresser",
]


class ITSystemRelation(_RelationMixin, Base):
    __tablename__ = "itsystem_relation"

    rel_type: Mapped[ITSystemRelationKode]

    itsystem_registrering_id = Column(
        ForeignKey("itsystem_registrering.id"), index=True
    )


class ITSystemTilsGyldighed(_TilsGyldighedMixin("itsystem"), Base):
    __tablename__ = "itsystem_tils_gyldighed"

    itsystem_registrering_id = Column(
        ForeignKey("itsystem_registrering.id"), index=True
    )
