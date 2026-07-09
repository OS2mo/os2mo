# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
from typing import Literal
from typing import NewType
from uuid import UUID

from psycopg.types.range import TimestamptzRange
from sqlalchemy import BigInteger
from sqlalchemy import CheckConstraint
from sqlalchemy import ColumnElement
from sqlalchemy import Enum
from sqlalchemy import Text
from sqlalchemy import cast
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import type_coerce
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import TSTZMULTIRANGE
from sqlalchemy.dialects.postgresql import TSTZRANGE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import column_property
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.types import UserDefinedType

Base = declarative_base()
metadata = Base.metadata


class PgSnapshot(UserDefinedType):
    """The PostgreSQL ``pg_snapshot`` type."""

    cache_ok = True

    def get_col_spec(self, **kw) -> str:
        return "pg_snapshot"

    def bind_expression(self, bindvalue) -> ColumnElement:
        return cast(bindvalue, self)


class make_interval(GenericFunction):
    """Register func.make_interval that can be used with the native PostgreSQL keyword arguments."""

    # https://docs.sqlalchemy.org/en/20/errors.html#error-cprf
    # https://docs.sqlalchemy.org/en/20/core/connections.html#sql-compilation-caching
    # https://docs.sqlalchemy.org/en/21/core/compiler.html#enabling-caching-support-for-custom-constructs
    inherit_cache = True

    def __init__(
        self, years=0, months=0, weeks=0, days=0, hours=0, mins=0, secs=0, **kw
    ):
        super().__init__(years, months, weeks, days, hours, mins, secs, **kw)


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

    @declared_attr
    @classmethod
    def _registrering_period_attr(cls) -> Mapped[TimestamptzRange]:
        return column_property(cls._registrering_period)

    @hybrid_property
    def registrering_period(self) -> TimestamptzRange:  # pragma: no cover
        return self._registrering_period_attr

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
    def lifecycle(self) -> ENUM:  # pragma: no cover
        return self._lifecycle_attr

    @lifecycle.inplace.expression
    @classmethod
    def _lifecycle(cls) -> ColumnElement[ENUM]:
        return type_coerce(text("(registrering).livscykluskode"), LivscyklusKode)

    def __repr__(self):  # pragma: no cover
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
    def virkning_period(self) -> TimestamptzRange:
        return self._virkning_period_attr

    @virkning_period.inplace.expression
    @classmethod
    def _virkning_period(cls) -> ColumnElement[TimestamptzRange]:
        return type_coerce(text("(virkning).timeperiod"), TSTZRANGE)


HasValidity = NewType("HasValidity", _VirkningMixin)


class _AktivVirkningMixin:
    """Lets the GraphQL list filters gate on validity without reading the
    multi-row ``*_tils_*`` table at all: ``active_tils`` holds the registration's
    active periods on the period row itself, and ``aktiv_virkning`` intersects
    them with the row's own ``virkning``. An expression GiST index materialises
    that intersection, so the filter is a single in-row overlap rather than a
    correlated ``EXISTS`` whose per-outer-row range Postgres cannot estimate.
    """

    active_tils: Mapped[Any] = mapped_column(
        TSTZMULTIRANGE, nullable=True, deferred=True
    )

    @hybrid_property
    def aktiv_virkning(self) -> Any:  # pragma: no cover
        raise NotImplementedError("aktiv_virkning is only available in queries")

    @aktiv_virkning.inplace.expression
    @classmethod
    def _aktiv_virkning(cls) -> ColumnElement:
        # Must render identically to the expression GiST index for the planner
        # to use it: tstzmultirange((virkning).timeperiod) * active_tils.
        return func.tstzmultirange(cls.virkning_period).op(
            "*", return_type=TSTZMULTIRANGE
        )(cls.active_tils)


HasAktivVirkning = NewType("HasAktivVirkning", _AktivVirkningMixin)


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
