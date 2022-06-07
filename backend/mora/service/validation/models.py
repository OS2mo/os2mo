# SPDX-FileCopyrightText: 2022 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from collections import Counter
from itertools import chain
from operator import itemgetter
from typing import Iterable
from typing import Optional
from typing import TYPE_CHECKING

from ... import lora
from mora.exceptions import ErrorCodes

if TYPE_CHECKING:  # pragma: no cover
    from ...handler.reading import ReadingHandler


class GroupValidation:
    @classmethod
    def from_requests(cls, requests: Iterable[dict]) -> "GroupValidation":
        """Create a `GroupValidation` instance from an iterable of request details.
        This can be used to validate a group of requests as a whole.
        """
        return cls(cls._get_filtered_validation_items(requests))

    @classmethod
    async def from_mo_objects(cls, search_fields: dict[str]) -> "GroupValidation":
        """Create a `GroupValidation` instance based on the given `search_fields` and
        a `ReadingHandler` instance returned by `get_mo_object_reading_handler`. This
        can be used to validate a new item being added to an existing group of MO
        objects.
        """
        connector = lora.Connector()
        reading_handler = cls.get_mo_object_reading_handler()
        mo_objects = await reading_handler.get(connector, search_fields)
        return cls(cls._get_filtered_validation_items(mo_objects))

    @classmethod
    def get_validation_item_from_mo_object(cls, mo_object: dict) -> Optional[dict]:
        """Given a `MO object`, return a "validation item" (or None, if the `MO object`
        is not relevant for this particular validation class.)
        Must be implemented by subclasses of `GroupValidation`.
        """
        raise NotImplementedError()

    @classmethod
    def get_mo_object_reading_handler(cls) -> "ReadingHandler":
        """Return a suitable `ReadingHandler` instance for this validation class (see
        `from_mo_objects`.)
        Must be implemented by subclasses of `GroupValidation`.
        """
        raise NotImplementedError()

    @classmethod
    def _get_filtered_validation_items(cls, mo_objects: Iterable[dict]) -> list[dict]:
        """Convert `mo_objects` to "validation items", passing over any empty results
        from `get_validation_item_from_mo_object`.
        """
        return list(
            filter(None, map(cls.get_validation_item_from_mo_object, mo_objects))
        )

    def __init__(self, validation_items: list[dict]):
        self.validation_items = validation_items

    def validate(self, obj: Optional[dict] = None) -> None:
        """Validate this `GroupValidation` instance.

        `validate` should return None if there are no validation errors, or raise an
        appropriate exception using `mora.exceptions.ErrorCodes`.

        `validate` must be implemented by subclasses of `GroupValidation`.

        If `obj` is given, it is added to the list of "validation items" before the
        actual validation takes place.

        It is recommended to call `super().validate(obj=obj)` in subclass
        implementations.
        """
        if obj is not None:
            self.validation_items = list(chain(self.validation_items, [obj]))

    def validate_unique_constraint(
        self, field_names: list[str], error: ErrorCodes
    ) -> None:
        """Validate a "unique constraint" given by `field_names`,
        raising an `HTTPException` if the constraint is violated.

        This checks that only *one* validation item is present for each combination of
        fields given by `field_names`.

        If there are duplicates, a member of the `ErrorCodes` enum is called, raising an
        `HTTPException`.
        """
        counter = Counter(map(itemgetter(*field_names), self.validation_items))
        if any(count > 1 for count in counter.values()):
            error()
