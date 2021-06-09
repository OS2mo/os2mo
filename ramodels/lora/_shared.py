#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import datetime
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import List
from typing import Literal
from typing import Optional
from typing import Union
from uuid import UUID
from uuid import uuid4

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from ramodels.base import NEG_INF
from ramodels.base import POS_INF
from ramodels.base import RABase
from ramodels.base import tz_isodate

try:
    import zoneinfo
except ImportError:  # pragma: no cover
    from backports import zoneinfo  # type: ignore

UTC = zoneinfo.ZoneInfo("UTC")

# --------------------------------------------------------------------------------------
# LoRaBase
# --------------------------------------------------------------------------------------


class LoraBase(RABase):
    """Base model for LoRa data models.

    Attributes:
        uuid:
    """

    # TODO: This is duplicated to each class that cannot be instantiated.
    # We should probably find a better solution.
    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls is LoraBase:
            raise TypeError("LoraBase may not be instantiated")
        return super().__new__(cls)

    uuid: UUID = Field(None)

    # Autogenerate UUID if necessary
    # TODO: in pydantic v2, this can be replaced with Field(default_factory=uuid4)
    # However, the beta version of default_factory is still unstable and prone to
    # side-effects.
    @validator("uuid", pre=True, always=True)
    def set_uuid(cls, _uuid: Optional[UUID]) -> UUID:
        return _uuid or uuid4()


# --------------------------------------------------------------------------------------
# Infinite Datetime
# --------------------------------------------------------------------------------------


class InfiniteDatetime(str):
    # Inspired by
    # https://pydantic-docs.helpmanual.io/usage/types/#classes-with-__get_validators__

    """Class handling InfiniteDatetimes for LoRa.

    Please note: This class is *not* meant to be instantiated directly.
    If a new object is desired, please use the from_value class method."""

    @classmethod
    def from_value(cls, value: Union[str, datetime]) -> "InfiniteDatetime":
        return cls.validate(value)

    @classmethod
    def __get_validators__(cls) -> Iterator[Callable]:
        """Magic method used by pydantic to collect validators.

        Yields:
            Iterator[Callable]: One (or more) validation functions,
            which are evaluated in order.
        """
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "InfiniteDatetime":
        """Validate an incoming value against InfiniteDatetime logic.

        Args:
            value (Any): The value to validate

        Raises:
            TypeError: If the value is not a 'str' or 'datetime' object.
            ISOParseError: If the value cannot be parsed as either the strings
                "-infinity", "infinity", or an ISO-8601 datetime string.

        Returns:
            str: Either "-infinity", "infinity", or an ISO-8601 datetime string.
        """

        if not isinstance(value, (str, datetime)):
            raise TypeError("string or datetime required")

        if value in {POS_INF, NEG_INF}:
            return cls(value)

        dt = tz_isodate(value)
        return cls(dt.isoformat())

    def __repr__(self) -> str:
        return f"InfiniteDatetime({super().__repr__()})"

    def __lt__(self, other: Any) -> bool:
        # other is not explictly typed because mypy complains about LSP violations.
        """Implements the less than magic method for InfiniteDatetime.

        Args:
            other (Any): value to compare against.
        Raises:
            TypeError: If other turns out to not be an instance of InfiniteDatetime.

        Returns:
            bool: True if dt(self) < dt(other), otherwise False.
        """
        if not isinstance(other, InfiniteDatetime):
            raise TypeError(
                f"Comparison between {type(self)} and {type(other)} not defined"
            )

        def _cast_dt(inf_dt: "InfiniteDatetime") -> datetime:
            if inf_dt == POS_INF:
                return datetime.max.replace(tzinfo=UTC)
            if inf_dt == NEG_INF:
                return datetime.min.replace(tzinfo=UTC)
            return datetime.fromisoformat(inf_dt)

        return _cast_dt(self) < _cast_dt(other)

    def __le__(self, other: Any) -> bool:
        """Implements the less than or equal to magic method for InfiniteDatetime.

        This method is defined using __lt__ and __eq__.
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other: Any) -> bool:
        """Implements the greater than magic method for InfiniteDatetime.

        This method is defined by negating __le__.
        """
        return not self.__le__(other)

    def __ge__(self, other: Any) -> bool:
        """Implements the less than or equal to magic method for InfiniteDatetime.

        This method is defined using __gt__ and __eq__.
        """
        return self.__gt__(other) or self.__eq__(other)


# --------------------------------------------------------------------------------------
# Shared models
# --------------------------------------------------------------------------------------


class EffectiveTime(RABase):
    """
    Attributes:
        from_date:
        to_date:
    """

    from_date: InfiniteDatetime = Field(alias="from")
    to_date: InfiniteDatetime = Field(alias="to")

    @root_validator
    def check_from_lt_to(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        from_date, to_date = values.get("from_date"), values.get("to_date")
        # Mypy complains here about unsupported use of operators due to Nones,
        # but we catch those with if all...
        if all([from_date, to_date]) and from_date >= to_date:  # type: ignore
            raise ValueError("from_date must be strictly less than to_date")
        return values


class Authority(RABase):
    """
    Attributes:
        urn:
        effective_time:
    """

    urn: str = Field(
        regex=r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$"
    )
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetProperties(RABase):
    """
    Attributes:
        user_key:
        effective_time:
    """

    user_key: str = Field(alias="brugervendtnoegle")
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetAttributes(RABase):
    """
    Attributes:
        properties:
    """

    properties: List[FacetProperties] = Field(
        alias="facetegenskaber", min_items=1, max_items=1
    )


class Published(RABase):
    """
    Attributes:
        published:
        effective_time:
    """

    # TODO: published are actually Enums in LoRa, but it's currently not possible
    # to lift them from LoRa systematically. We should definitely fix this!

    published: str = Field("Publiceret", alias="publiceret")
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetStates(RABase):
    """
    Attributes:
        published_state:
    """

    published_state: List[Published] = Field(
        alias="facetpubliceret", min_items=1, max_items=1
    )


class Responsible(RABase):
    """
    Attributes:
        object_type:
        uuid:
        effective_time:
    """

    object_type: Literal["organisation"] = Field("organisation", alias="objekttype")
    uuid: UUID
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetRef(RABase):
    """
    Attributes:
        object_type:
        uuid:
        effective_time:
    """

    object_type: Literal["facet"] = Field("facet", alias="objekttype")
    uuid: UUID
    effective_time: EffectiveTime = Field(alias="virkning")


class FacetRelations(RABase):
    """
    Attributes:
        responsible:
    """

    responsible: List[Responsible] = Field(alias="ansvarlig", min_items=1, max_items=1)


class KlasseProperties(RABase):
    """
    Attributes:
        user_key:
        title:
        scope:
        effective_time:
    """

    user_key: str = Field(alias="brugervendtnoegle")
    title: str = Field(alias="titel")
    scope: Optional[str] = Field(alias="omfang")
    effective_time: EffectiveTime = Field(alias="virkning")


class KlasseRelations(RABase):
    """
    Attributes:
        responsible:
        facet:
    """

    responsible: List[Responsible] = Field(alias="ansvarlig", min_items=1, max_items=1)
    facet: List[FacetRef] = Field(min_items=1, max_items=1)


class KlasseAttributes(RABase):
    """
    Attributes:
        properties:
    """

    properties: List[KlasseProperties] = Field(
        alias="klasseegenskaber", min_items=1, max_items=1
    )


class KlasseStates(RABase):
    """
    Attributes:
        published_state:
    """

    published_state: List[Published] = Field(
        alias="klassepubliceret", min_items=1, max_items=1
    )


class OrganisationProperties(RABase):
    """
    Attributes:
        user_key:
        name:
        effective_time:
    """

    user_key: str = Field(alias="brugervendtnoegle")
    name: str = Field(alias="organisationsnavn")
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationAttributes(RABase):
    """
    Attributes:
        properties:
    """

    properties: List[OrganisationProperties] = Field(
        alias="organisationegenskaber", min_items=1, max_items=1
    )


class OrganisationValidState(RABase):
    """
    Attributes:
        state:
        effective_time:
    """

    state: str = Field("Aktiv", alias="gyldighed")
    effective_time: EffectiveTime = Field(alias="virkning")


class OrganisationStates(RABase):
    """
    Attributes:
        valid_state:
    """

    valid_state: List[OrganisationValidState] = Field(
        alias="organisationgyldighed", min_items=1, max_items=1
    )


class OrganisationRelations(RABase):
    """
    Attributes:
        authority:
    """

    authority: List[Authority] = Field(alias="myndighed", min_items=1, max_items=1)
