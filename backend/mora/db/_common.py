# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import Enum
from sqlalchemy import select
from sqlalchemy import Text
from sqlalchemy import text
from sqlalchemy.orm import column_property
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


Base = declarative_base()
metadata = Base.metadata


class _OIOEntityMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True)


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
                    "greatest(lower((virkning).timeperiod), '1930-01-01'::timestamptz)"
                )
            ).scalar_subquery()
        )

    # SQLAlchemy does not support composite types
    @declared_attr
    def virkning_slut(cls) -> Mapped[datetime]:
        # We use `least` here as Python datetime don't support "infinity"
        return column_property(
            select(
                text("least(upper((virkning).timeperiod), '9999-12-31'::timestamptz)")
            ).scalar_subquery()
        )


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


Gyldighed = Literal["Aktiv", "Inaktiv", ""]

PubliceretStatus = Literal["Publiceret", "IkkePubliceret", ""]


def _TilsGyldighedMixin(oio_type):
    class _Mixin(_VirkningMixin):
        id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

        gyldighed: Mapped[Gyldighed] = mapped_column(
            Enum(*Gyldighed.__args__, name=f"{oio_type}gyldighedtils"),
            index=True,
        )

    return _Mixin
