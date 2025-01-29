# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import synonym

from ._common import Base
from ._common import PubliceretStatus
from ._common import _AttrEgenskaberMixin
from ._common import _OIOEntityMixin
from ._common import _RegistreringMixin
from ._common import _RelationMixin
from ._common import _VirkningMixin


class Facet(_OIOEntityMixin, Base):
    __tablename__ = "facet"


class FacetRegistrering(_RegistreringMixin, Base):
    __tablename__ = "facet_registrering"
    facet_id = Column(ForeignKey("facet.id"), index=True)
    uuid = synonym("facet_id")


class FacetAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "facet_attr_egenskaber"

    beskrivelse: Mapped[str | None] = mapped_column(Text, index=True)
    opbygning: Mapped[str | None] = mapped_column(Text, index=True)
    ophavsret: Mapped[str | None] = mapped_column(Text, index=True)
    plan: Mapped[str | None] = mapped_column(Text, index=True)
    supplement: Mapped[str | None] = mapped_column(Text, index=True)
    retskilde: Mapped[str | None] = mapped_column(Text, index=True)

    facet_registrering_id = Column(ForeignKey("facet_registrering.id"), index=True)


FacetRelationKode = Literal[
    "ansvarlig",
    "facettilhoerer",
]


class FacetRelation(_RelationMixin, Base):
    __tablename__ = "facet_relation"

    rel_type: Mapped[FacetRelationKode]

    facet_registrering_id = Column(ForeignKey("facet_registrering.id"), index=True)


class FacetTilsPubliceret(_VirkningMixin, Base):
    __tablename__ = "facet_tils_publiceret"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    publiceret: Mapped[PubliceretStatus] = mapped_column(
        Enum(*PubliceretStatus.__args__, name="facetpublicerettils"),
        index=True,
    )

    facet_registrering_id = Column(ForeignKey("facet_registrering.id"), index=True)
