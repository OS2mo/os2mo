# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Literal
from typing import NewType
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Enum
from sqlalchemy import Text
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import column_property
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column

Base = declarative_base()
metadata = Base.metadata


class _OIOEntityMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True)

    def __repr__(self):  # pragma: no cover
        return f"{self.__class__.__name__}(id={self.id})"


LivscyklusKode = ENUM(
    "Opstaaet",
    "Importeret",
    "Passiveret",
    "Slettet",
    "Rettet",
    name="livscykluskode",
    metadata=metadata,
)


class _RegistreringMixin:
    __table_args__ = (
        CheckConstraint(
            "((registrering).timeperiod IS NOT NULL) AND (NOT isempty((registrering).timeperiod))"
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # SQLAlchemy does not support composite types
    @declared_attr
    def registreringstid_start(cls) -> Mapped[datetime]:
        # We use `greatest` here as Python datetime don't support "-infinity"
        return column_property(
            select(
                text(
                    "greatest(lower((registrering).timeperiod), '1930-01-01'::timestamptz)"
                )
            ).scalar_subquery()
        )

    # SQLAlchemy does not support composite types
    @declared_attr
    def registreringstid_slut(cls) -> Mapped[datetime]:
        # We use `least` here as Python datetime don't support "infinity"
        return column_property(
            select(
                text(
                    "least(upper((registrering).timeperiod), '9999-12-31'::timestamptz)"
                )
            ).scalar_subquery()
        )

    # SQLAlchemy does not support composite types
    @declared_attr
    def actor(cls) -> Mapped[UUID]:
        return column_property(
            select(text("(registrering).brugerref")).scalar_subquery()
        )

    # SQLAlchemy does not support composite types
    @declared_attr
    def note(cls) -> Mapped[UUID]:
        return column_property(select(text("(registrering).note")).scalar_subquery())

    # SQLAlchemy does not support composite types
    @declared_attr
    def lifecycle(cls) -> Mapped[LivscyklusKode]:
        return column_property(
            select(text("(registrering).livscykluskode")).scalar_subquery()
        )

    def __repr__(self):  # pragma: no cover
        return f"{self.__class__.__name__}(id={self.id}, registreringstid_start={self.registreringstid_start!r}, registreringstid_slut={self.registreringstid_slut!r})"


class _VirkningMixin:
    __table_args__ = (
        CheckConstraint(
            "((virkning).timeperiod IS NOT NULL) AND (NOT isempty((virkning).timeperiod))"
        ),
    )

    # SQLAlchemy does not support composite types
    @declared_attr
    def virkning_start(cls) -> Mapped[datetime]:
        # We use `greatest` here as Python datetime don't support "-infinity"
        return column_property(
            select(
                text(
                    f"greatest(lower(({cls.__tablename__}.virkning).timeperiod), '1930-01-01'::timestamptz)"
                )
            ).scalar_subquery()
        )

    # SQLAlchemy does not support composite types
    @declared_attr
    def virkning_slut(cls) -> Mapped[datetime]:
        # We use `least` here as Python datetime don't support "infinity"
        return column_property(
            select(
                text(
                    f"least(upper(({cls.__tablename__}.virkning).timeperiod), '9999-12-31'::timestamptz)"
                )
            ).scalar_subquery()
        )


HasValidity = NewType("HasValidity", _VirkningMixin)


class _AttrEgenskaberMixin(_VirkningMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    brugervendtnoegle: Mapped[str] = mapped_column(Text, index=True)


class _RelationMixin(_VirkningMixin):
    @declared_attr
    def __table_args__(cls):
        return (
            *_VirkningMixin.__table_args__,
            CheckConstraint(
                "NOT ((rel_maal_uuid IS NOT NULL) AND ((rel_maal_urn IS NOT NULL) AND (rel_maal_urn <> ''::text)))"  # noqa
            ),
        )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    rel_maal_uuid: Mapped[UUID | None]
    rel_maal_urn: Mapped[str | None]
    objekt_type: Mapped[str | None]
    rel_type: Mapped[str]

    def __repr__(self):  # pragma: no cover
        return f"{self.__class__.__name__}(id={self.id}, rel_maal_uuid={self.rel_maal_uuid!r}, rel_maal_urn={self.rel_maal_urn!r}, objekt_type={self.objekt_type!r}, rel_type={self.rel_type!r})"


Gyldighed = Literal["Aktiv", "Inaktiv", ""]

PubliceretStatus = Literal["Publiceret", "IkkePubliceret", ""]


def _TilsGyldighedMixin(oio_type):
    class _Mixin(_VirkningMixin):
        id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

        gyldighed: Mapped[Gyldighed] = mapped_column(
            Enum(*Gyldighed.__args__, name=f"{oio_type}gyldighedtils"),
            index=True,
        )

        def __repr__(self):  # pragma: no cover
            return (
                f"{self.__class__.__name__}(id={self.id}, gyldighed={self.gyldighed!r})"
            )

    return _Mixin
