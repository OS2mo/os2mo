# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import Column
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
from ._common import _VirkningMixin


class Bruger(_OIOEntityMixin, Base):
    __tablename__ = "bruger"


class BrugerRegistrering(_RegistreringMixin, Base):
    __tablename__ = "bruger_registrering"
    bruger_id: Mapped[UUID] = mapped_column(ForeignKey("bruger.id"), index=True)
    uuid = synonym("bruger_id")


class BrugerAttrEgenskaber(_AttrEgenskaberMixin, Base):
    __tablename__ = "bruger_attr_egenskaber"

    brugernavn: Mapped[str | None] = mapped_column(Text, index=True)
    brugertype: Mapped[str | None] = mapped_column(Text, index=True)

    bruger_registrering_id = Column(ForeignKey("bruger_registrering.id"), index=True)


class BrugerAttrUdvidelser(_VirkningMixin, Base):
    __tablename__ = "bruger_attr_udvidelser"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fornavn: Mapped[str | None] = mapped_column(Text, index=True)
    efternavn: Mapped[str | None] = mapped_column(Text, index=True)
    kaldenavn_fornavn: Mapped[str | None] = mapped_column(Text, index=True)
    kaldenavn_efternavn: Mapped[str | None] = mapped_column(Text, index=True)
    seniority: Mapped[str | None] = mapped_column(Text, index=True)

    bruger_registrering_id = Column(ForeignKey("bruger_registrering.id"), index=True)


BrugerRelationKode = Literal[
    "tilhoerer",
    "tilknyttedepersoner",
]


class BrugerRelation(_RelationMixin, Base):
    __tablename__ = "bruger_relation"

    rel_type: Mapped[BrugerRelationKode]

    bruger_registrering_id = Column(ForeignKey("bruger_registrering.id"), index=True)


class BrugerTilsGyldighed(_TilsGyldighedMixin("bruger"), Base):
    __tablename__ = "bruger_tils_gyldighed"

    bruger_registrering_id = Column(ForeignKey("bruger_registrering.id"), index=True)
