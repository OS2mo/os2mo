# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import zoneinfo
from collections.abc import Callable
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from uuid import UUID
from uuid import uuid4

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from mora.graphapi.gmodels.base import NEG_INF
from mora.graphapi.gmodels.base import POS_INF
from mora.graphapi.gmodels.base import RABase
from mora.graphapi.gmodels.base import tz_isodate

UTC = zoneinfo.ZoneInfo("UTC")


class LoraBase(RABase):
    """Base model for LoRa data models.

    Attributes:
        uuid:
    """

    # TODO: This is duplicated to each class that cannot be instantiated.
    # We should probably find a better solution.
    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls is LoraBase:  # pragma: no cover
            raise TypeError("LoraBase may not be instantiated")
        return super().__new__(cls)

    uuid: UUID = Field(None)  # type: ignore

    # Autogenerate UUID if necessary
    # TODO: in pydantic v2, this can be replaced with Field(default_factory=uuid4)
    # However, the beta version of default_factory is still unstable and prone to
    # side-effects.
    @validator("uuid", pre=True, always=True)
    def set_uuid(cls, _uuid: UUID | None) -> UUID:
        return _uuid or uuid4()

    @validator("object_type", pre=True, check_fields=False)
    def lower_object_type(cls, object_type: Any | None) -> Any:  # pragma: no cover
        """
        Lower the object_type before validating equality with the literal, as some LoRa
        databases define the capitalised value, while others do not.
        """
        if isinstance(object_type, str):
            return object_type.lower()
        return object_type


class InfiniteDatetime(str):
    # Inspired by
    # https://pydantic-docs.helpmanual.io/usage/types/#classes-with-__get_validators__

    """Class handling InfiniteDatetimes for LoRa.

    Please note: This class is *not* meant to be instantiated directly.
    If a new object is desired, please use the from_value class method."""

    @classmethod
    def from_value(
        cls, value: str | datetime
    ) -> "InfiniteDatetime":  # pragma: no cover
        return cls.validate(value)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        """Magic method used by pydantic to collect validators.

        Yields:
            One (or more) validation functions, which are evaluated in order.
        """
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "InfiniteDatetime":
        """Validate an incoming value against InfiniteDatetime logic.

        Args:
            value: The value to validate

        Raises:
            TypeError: If the value is not a `str` or `datetime` object.
            ISOParseError: If the value cannot be parsed as either the strings
                `-infinity`, `infinity`, or an ISO-8601 datetime string.

        Returns:
            Either `-infinity`, `infinity`, or an ISO-8601 datetime string.
        """

        if not isinstance(value, (str, datetime)):  # pragma: no cover
            raise TypeError("string or datetime required")

        if value in {POS_INF, NEG_INF}:
            return cls(value)

        # coverage: pause
        dt = tz_isodate(value)
        return cls(dt.isoformat())
        # coverage: unpause

    def __repr__(self) -> str:  # pragma: no cover
        return f"InfiniteDatetime({super().__repr__()})"

    def __lt__(self, other: Any) -> bool:
        # other is not explictly typed because mypy complains about LSP violations.
        """Implements the less than magic method for InfiniteDatetime.

        Args:
            other: value to compare against.
        Raises:
            TypeError: If other turns out to not be an instance of InfiniteDatetime.

        Returns:
            True if `dt(self) < dt(other)`, otherwise False.
        """
        if not isinstance(other, InfiniteDatetime):  # pragma: no cover
            raise TypeError(
                f"Comparison between {type(self)} and {type(other)} not defined"
            )

        def _cast_dt(inf_dt: "InfiniteDatetime") -> datetime:
            if inf_dt == POS_INF:
                return datetime.max.replace(tzinfo=UTC)
            if inf_dt == NEG_INF:
                return datetime.min.replace(tzinfo=UTC)
            # coverage: pause
            return datetime.fromisoformat(inf_dt)
            # coverage: unpause

        return _cast_dt(self) < _cast_dt(other)

    def __le__(self, other: Any) -> bool:
        """Implements the less than or equal to magic method for InfiniteDatetime.

        This method is defined using `__lt__` and `__eq__`.
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: Any) -> bool:
        """Implements the greater than magic method for InfiniteDatetime.

        This method is defined by negating `__le__`.
        """
        return not self.__le__(other)

    def __ge__(self, other: Any) -> bool:
        """Implements the less than or equal to magic method for InfiniteDatetime.

        This method is defined using `__gt__` and `__eq__`.
        """
        return self.__gt__(other) or self.__eq__(other)


class EffectiveTime(RABase):
    """
    The effective time of a given object in LoRa.
    """

    from_date: InfiniteDatetime = Field(
        alias="from", description="Start of the effective time interval."
    )
    from_included: bool | None = Field(
        description="Whether from_date is included in the interval."
    )
    to_date: InfiniteDatetime = Field(
        alias="to", description="End of the effective time interval."
    )
    to_included: bool | None = Field(
        description="Whether to_date is included in the interval."
    )
    actor_type: str | None = Field(
        alias="aktoertypekode", description="Actor type indicator, e.g. Bruger"
    )
    actor_ref: UUID | None = Field(
        alias="aktoerref", description="Actor UUID reference."
    )

    @root_validator
    def check_from_lt_to(cls, values: dict[str, Any]) -> dict[str, Any]:
        from_date, to_date = values.get("from_date"), values.get("to_date")
        # Mypy complains here about unsupported use of operators due to Nones,
        # but we catch those with if all...
        if all([from_date, to_date]) and from_date >= to_date:  # type: ignore  # pragma: no cover
            raise ValueError("from_date must be strictly less than to_date")
        return values


class Authority(RABase):
    """Authority as given by URN."""

    urn: str = Field(
        regex=r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$",
        description="URN of the authority.",
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the authority."
    )


class OrganisationProperties(RABase):
    """
    LoRa organisation properties.
    """

    user_key: str = Field(alias="brugervendtnoegle", description="Short, unique key.")
    name: str = Field(
        alias="organisationsnavn", description="Name of the organisation."
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the properties."
    )


class OrganisationAttributes(RABase):
    """
    LoRa organisation attributes.
    """

    properties: list[OrganisationProperties] = Field(
        alias="organisationegenskaber",
        min_items=1,
        max_items=1,
        description="Properties denoting the attributes.",
    )


class OrganisationValidState(RABase):
    """
    State of an organisation in LoRa.
    """

    state: str = Field(
        "Aktiv",
        alias="gyldighed",
        description="String describing the validity of an organisation.",
    )
    effective_time: EffectiveTime = Field(
        alias="virkning", description="Effective time of the valid states."
    )


class OrganisationStates(RABase):
    """
    Organisation validity as given by OrganisationValidState.
    """

    valid_state: list[OrganisationValidState] = Field(
        alias="organisationgyldighed",
        min_items=1,
        max_items=1,
        description="Valid states denoting the overall state.",
    )


class OrganisationRelations(RABase):
    """
    Organisation relations given by an authority object.
    """

    authority: list[Authority] = Field(
        alias="myndighed",
        min_items=1,
        max_items=1,
        description="Authority object denoting the relations.",
    )
