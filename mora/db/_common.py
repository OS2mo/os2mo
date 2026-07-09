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
from sqlalchemy import func
from sqlalchemy import literal_column
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
from sqlalchemy.sql.elements import Grouping
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.types import UserDefinedType

Base = declarative_base()
metadata = Base.metadata


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


class _CompositeType(UserDefinedType):
    """Opaque stand-in for a PostgreSQL composite-type column (``virkning`` /
    ``registrering``).

    The composite value is never round-tripped through the ORM; the column is
    mapped (deferred, so it is never loaded implicitly) only so that field
    access like ``(virkning).timeperiod`` renders with a proper table qualifier
    that adapts automatically when the table is aliased.
    """

    cache_ok = True

    def __init__(self, name: str) -> None:
        self.name = name

    def get_col_spec(self, **kw) -> str:  # pragma: no cover
        return self.name


def _composite_field(column: ColumnElement, field: str, type_: Any) -> ColumnElement:
    """Access ``field`` of a composite-type ``column`` as ``(column).field``.

    Built from the mapped column rather than a raw ``text("(virkning)...")``
    fragment, so the table qualifier is rendered correctly and is rewritten
    automatically when the table is aliased (e.g. in recursive ancestor /
    descendant org-unit queries). The ``Grouping`` is required because the
    composite-access syntax needs the parentheses in ``(column).field``.
    """
    return type_coerce(
        Grouping(column).op(".", precedence=15)(literal_column(field)), type_
    )


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

    registrering: Mapped[Any] = mapped_column(
        _CompositeType("registreringbase"), deferred=True
    )

    @hybrid_property
    def registrering_period(self) -> TimestamptzRange:  # pragma: no cover
        raise NotImplementedError("registrering_period is only available in queries")

    @registrering_period.inplace.expression
    @classmethod
    def _registrering_period(cls) -> ColumnElement[TimestamptzRange]:
        return _composite_field(cls.registrering, "timeperiod", TSTZRANGE)

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

    @hybrid_property
    def lifecycle(self) -> ENUM:  # pragma: no cover
        raise NotImplementedError("lifecycle is only available in queries")

    @lifecycle.inplace.expression
    @classmethod
    def _lifecycle(cls) -> ColumnElement[ENUM]:
        return _composite_field(cls.registrering, "livscykluskode", LivscyklusKode)

    def __repr__(self):  # pragma: no cover
        return f"{self.__class__.__name__}(id={self.id})"


class _VirkningMixin:
    __table_args__ = (
        CheckConstraint(
            "((virkning).timeperiod IS NOT NULL) AND (NOT isempty((virkning).timeperiod))"
        ),
    )

    virkning: Mapped[Any] = mapped_column(_CompositeType("virkning"), deferred=True)

    @hybrid_property
    def virkning_period(self) -> TimestamptzRange:  # pragma: no cover
        raise NotImplementedError("virkning_period is only available in queries")

    @virkning_period.inplace.expression
    @classmethod
    def _virkning_period(cls) -> ColumnElement[TimestamptzRange]:
        return _composite_field(cls.virkning, "timeperiod", TSTZRANGE)


HasValidity = NewType("HasValidity", _VirkningMixin)


class _AktivVirkningMixin:
    """Active-period overlap for a relation/attribute row, for the GraphQL list
    filters (see #70660).

    ``active_tils`` is the union of the registration's active validity periods
    (gyldighed=Aktiv / publiceret=Publiceret), copied onto each period row by a
    trigger; it depends only on the ``tils`` table (one-way data flow). Maintained
    so it is non-null (empty multirange ``{}`` when the registration is never
    active); NULL means only "not yet backfilled". Deferred so it is never loaded
    implicitly.

    ``aktiv_virkning`` is the query-only overlap of the row's own ``virkning``
    with ``active_tils``. It is not stored; an expression GiST index materialises
    it (fused with ``rel_type`` / ``rel_maal_uuid``), so the active-period filter
    is ``aktiv_virkning && window`` -- a single in-row multirange overlap instead
    of a correlated ``EXISTS`` into the multi-row ``*_tils_*`` table.
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


class _AttrEgenskaberMixin(_AktivVirkningMixin, _VirkningMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    brugervendtnoegle: Mapped[str] = mapped_column(Text, index=True)


class _RelationMixin(_AktivVirkningMixin, _VirkningMixin):
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

        @classmethod
        def is_active(cls) -> ColumnElement:
            return cls.gyldighed == "Aktiv"

        def __repr__(self):  # pragma: no cover
            return (
                f"{self.__class__.__name__}(id={self.id}, gyldighed={self.gyldighed!r})"
            )

    return _Mixin
