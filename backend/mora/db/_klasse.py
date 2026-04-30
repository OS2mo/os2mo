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


class Klasse(_OIOEntityMixin, Base):
    __tablename__ = "klasse"


class KlasseRegistrering(_RegistreringMixin, Base):
    __tablename__ = "klasse_registrering"
    klasse_id: Mapped[int] = mapped_column(ForeignKey("klasse.id"), index=True)
    uuid = synonym("klasse_id")


class KlasseAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "klasse_attr_egenskaber"

    titel: Mapped[str] = mapped_column(Text, index=True)

    beskrivelse: Mapped[str | None] = mapped_column(Text, index=True)
    eksempel: Mapped[str | None] = mapped_column(Text, index=True)
    omfang: Mapped[str | None] = mapped_column(Text, index=True)
    retskilde: Mapped[str | None] = mapped_column(Text, index=True)
    aendringsnotat: Mapped[str | None] = mapped_column(Text, index=True)

    klasse_registrering_id: Mapped[int] = mapped_column(
        ForeignKey("klasse_registrering.id"), index=True
    )


class KlasseAttrEgenskaberSoegeord(Base):
    __tablename__ = "klasse_attr_egenskaber_soegeord"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    soegeordidentifikator: Mapped[str | None] = mapped_column(Text, index=True)
    beskrivelse: Mapped[str | None] = mapped_column(Text, index=True)
    soegeordskategori: Mapped[str | None] = mapped_column(Text, index=True)

    klasse_attr_egenskaber_id: Mapped[int] = mapped_column(
        ForeignKey("klasse_attr_egenskaber.id"), index=True
    )


KlasseRelationKode = Literal[
    "ansvarlig",
    "ejer",
    "facet",
    "overordnetklasse",
]


class KlasseRelation(_RelationMixin, Base):
    __tablename__ = "klasse_relation"

    rel_type: Mapped[KlasseRelationKode]  # type: ignore[assignment]

    klasse_registrering_id: Mapped[int] = mapped_column(
        ForeignKey("klasse_registrering.id"), index=True
    )


class KlasseTilsPubliceret(_VirkningMixin, Base):
    __tablename__ = "klasse_tils_publiceret"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    publiceret: Mapped[PubliceretStatus] = mapped_column(
        Enum(*PubliceretStatus.__args__, name="klassepublicerettils"),  # type: ignore[attr-defined]
        index=True,
    )

    klasse_registrering_id: Mapped[int] = mapped_column(
        ForeignKey("klasse_registrering.id"), index=True
    )
