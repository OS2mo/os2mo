# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Literal
from typing import NewType
from uuid import UUID

from psycopg.types.range import TimestamptzRange
from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import ColumnElement
from sqlalchemy import Enum
from sqlalchemy import Text
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import type_coerce
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import column_property
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import GenericFunction

Base = declarative_base()
metadata = Base.metadata


class make_interval(GenericFunction):
    """Register func.make_interval that can be used with the native PostgreSQL keyword arguments."""

    # https://docs.sqlalchemy.org/en/20/errors.html#error-cprf
    # https://docs.sqlalchemy.org/en/20/core/connections.html#sql-compilation-caching
    # https://docs.sqlalchemy.org/en/21/core/compiler.html#enabling-caching-support-for-custom-constructs
    inherit_cache = True

    def __init__(
        self, years: int=0, months: int=0, weeks: int=0, days: int=0, hours: int=0, mins: int=0, secs: int=0, **kw
    ) -> None:
        super().__init__(years, months, weeks, days, hours, mins, secs, **kw)


class _OIOEntityMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True)

    def __repr__(self) -> str:  # pragma: no cover
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

    @declared_attr
    @classmethod
    def _registrering_period_attr(cls) -> Mapped[TimestamptzRange]:
        return column_property(cls._registrering_period)

    @hybrid_property
    def registrering_period(self) -> TimestamptzRange:
        return self._registrering_period_attr  # pragma: no cover

    @registrering_period.inplace.expression
    @classmethod
    def _registrering_period(cls) -> ColumnElement[TimestamptzRange]:
        return type_coerce(text("(registrering).timeperiod"), TSTZRANGE)

    # TODO: hybrid_property
    @declared_attr
    def actor(cls) -> Mapped[UUID]:
        return column_property(
            select(text("(registrering).brugerref")).scalar_subquery()
        )

    # TODO: hybrid_property
    @declared_attr
    def note(cls) -> Mapped[UUID]:
        return column_property(select(text("(registrering).note")).scalar_subquery())

    @declared_attr
    @classmethod
    def _lifecycle_attr(cls) -> Mapped[ENUM]:
        return column_property(cls._lifecycle)

    @hybrid_property
    def lifecycle(self) -> ENUM:
        return self._lifecycle_attr  # pragma: no cover

    @lifecycle.inplace.expression
    @classmethod
    def _lifecycle(cls) -> ColumnElement[ENUM]:
        return type_coerce(text("(registrering).livscykluskode"), LivscyklusKode)

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(id={self.id}, registrering_period={self.registrering_period!r})"


class _VirkningMixin:
    __table_args__ = (
        CheckConstraint(
            "((virkning).timeperiod IS NOT NULL) AND (NOT isempty((virkning).timeperiod))"
        ),
    )

    @declared_attr
    @classmethod
    def _virkning_period_attr(cls) -> Mapped[TimestamptzRange]:
        return column_property(cls._virkning_period)

    @hybrid_property
    def virkning_period(self) -> TimestamptzRange:  # pragma: no cover
        return self._virkning_period_attr

    @virkning_period.inplace.expression
    @classmethod
    def _virkning_period(cls) -> ColumnElement[TimestamptzRange]:
        return type_coerce(text("(virkning).timeperiod"), TSTZRANGE)


HasValidity = NewType("HasValidity", _VirkningMixin)


class _AttrEgenskaberMixin(_VirkningMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    brugervendtnoegle: Mapped[str] = mapped_column(Text, index=True)


class _RelationMixin(_VirkningMixin):
    @declared_attr
    def __table_args__(cls) -> tuple[CheckConstraint, CheckConstraint]:
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

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.__class__.__name__}(id={self.id}, rel_maal_uuid={self.rel_maal_uuid!r}, rel_maal_urn={self.rel_maal_urn!r}, objekt_type={self.objekt_type!r}, rel_type={self.rel_type!r})"


Gyldighed = Literal["Aktiv", "Inaktiv", ""]

PubliceretStatus = Literal["Publiceret", "IkkePubliceret", ""]


def _TilsGyldighedMixin(oio_type) -> type[_Mixin]:
    class _Mixin(_VirkningMixin):
        id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

        gyldighed: Mapped[Gyldighed] = mapped_column(
            Enum(*Gyldighed.__args__, name=f"{oio_type}gyldighedtils"),
            index=True,
        )

        def __repr__(self) -> str:  # pragma: no cover
            return (
                f"{self.__class__.__name__}(id={self.id}, gyldighed={self.gyldighed!r})"
            )

    return _Mixin
