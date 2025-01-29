# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
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
from ._common import _VirkningMixin


class OrganisationFunktion(_OIOEntityMixin, Base):
    __tablename__ = "organisationfunktion"


class OrganisationFunktionRegistrering(_RegistreringMixin, Base):
    __tablename__ = "organisationfunktion_registrering"
    organisationfunktion_id = Column(ForeignKey("organisationfunktion.id"), index=True)
    uuid = synonym("organisationfunktion_id")


FunktionsNavn = Literal[
    "Adresse",
    "Engagement",
    "IT-system",
    "KLE",
    "Leder",
    "Orlov",
    "Relateret Enhed",
    "Rollebinding",
    "Tilknytning",
    "owner",
]


class OrganisationFunktionAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "organisationfunktion_attr_egenskaber"

    funktionsnavn: Mapped[FunktionsNavn]

    organisationfunktion_registrering_id = Column(
        ForeignKey("organisationfunktion_registrering.id"), index=True
    )


class OrganisationFunktionRelationKode(Enum):
    adresser = "adresser"
    opgaver = "opgaver"
    organisatoriskfunktionstype = "organisatoriskfunktionstype"
    primaer = "primær"
    tilknyttedebrugere = "tilknyttedebrugere"
    tilknyttedeenheder = "tilknyttedeenheder"
    tilknyttedefunktioner = "tilknyttedefunktioner"
    tilknyttedeinteressefaellesskaber = "tilknyttedeinteressefaellesskaber"
    tilknyttedeitsystemer = "tilknyttedeitsystemer"
    tilknyttedeklasser = "tilknyttedeklasser"
    tilknyttedeorganisationer = "tilknyttedeorganisationer"
    tilknyttedepersoner = "tilknyttedepersoner"


class OrganisationFunktionRelation(_RelationMixin, Base):
    __tablename__ = "organisationfunktion_relation"

    rel_type: Mapped[OrganisationFunktionRelationKode]

    organisationfunktion_registrering_id = Column(
        ForeignKey("organisationfunktion_registrering.id"), index=True
    )


class OrganisationFunktionTilsGyldighed(
    _TilsGyldighedMixin("organisationfunktion"), Base
):
    __tablename__ = "organisationfunktion_tils_gyldighed"

    organisationfunktion_registrering_id = Column(
        ForeignKey("organisationfunktion_registrering.id"), index=True
    )


class OrganisationFunktionAttrUdvidelser(_VirkningMixin, Base):
    __tablename__ = "organisationfunktion_attr_udvidelser"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    primær: Mapped[bool | None] = mapped_column(Boolean, index=True)
    fraktion: Mapped[int | None] = mapped_column(Integer, index=True)

    udvidelse_1: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_2: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_3: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_4: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_5: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_6: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_7: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_8: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_9: Mapped[str | None] = mapped_column(Text, index=True)
    udvidelse_10: Mapped[str | None] = mapped_column(Text, index=True)

    organisationfunktion_registrering_id = Column(
        ForeignKey("organisationfunktion_registrering.id"), nullable=False, index=True
    )
