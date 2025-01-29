# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
import copy
from collections import Counter
from collections.abc import Callable
from collections.abc import Iterable
from itertools import chain
from operator import itemgetter
from typing import TYPE_CHECKING

from more_itertools import flatten

from mora.exceptions import ErrorCodes

from ... import lora

if TYPE_CHECKING:  # pragma: no cover
    from ...handler.reading import ReadingHandler


class GroupValidation:
    @classmethod
    async def from_requests(cls, requests: Iterable[dict]) -> "GroupValidation":
        """Create a `GroupValidation` instance from an iterable of request details.
        This can be used to validate a group of requests as a whole.
        """
        return cls(await cls._get_filtered_validation_items(requests))

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
        return cls(await cls._get_filtered_validation_items(mo_objects))

    @classmethod
    async def get_validation_items_from_mo_object(cls, mo_object: dict) -> list[dict]:
        """Given a `MO object`, return a list of zero or more "validation items" that
        are relevant to this group validation.
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
    async def _get_filtered_validation_items(
        cls, mo_objects: Iterable[dict]
    ) -> list[dict]:
        """Convert one or more `mo_objects` to zero or more "validation items"."""
        # Each task returns a list of zero or more validation items
        tasks = map(cls.get_validation_items_from_mo_object, mo_objects)
        # Flatten the lists from each task into a single list of all validation items
        return list(flatten(await asyncio.gather(*tasks)))

    def __init__(self, validation_items: list[dict]):
        self.validation_items = validation_items

    def validate(self) -> None:
        """Validate this `GroupValidation` instance.

        `validate` should return None if there are no validation errors, or raise an
        appropriate exception using `mora.exceptions.ErrorCodes`.

        `validate` must be implemented by subclasses of `GroupValidation`.
        """
        raise NotImplementedError()

    def add_validation_item(self, validation_item: dict) -> "GroupValidation":
        """Add another validation item to this group validation.

        This is used for validating the addition of a new item to a group, e.g. in
        `prepare_create` methods.

        Creates a copy of this `GroupValidation` instance containing the original
        validation items, plus the new validation item.

        The caller code can then call `validate` on the new instance returned, which
        will validate the new validation item together with the original validation
        items.
        """
        return self.__class__(list(chain(self.validation_items, [validation_item])))

    def update_validation_item(
        self, item_uuid: str, validation_item: dict
    ) -> "GroupValidation":
        """Update a validation item in this group validation.

        This is used for validating the modification of an existing item in a group,
        e.g. in  `prepare_edit` methods.

        Creates a copy of this `GroupValidation` instance containing an updated list of
        validation items.

        The caller code can then call `validate` on the new instance returned, which
        will validate the updated list of validation items.
        """
        validation_items = copy.deepcopy(self.validation_items)
        for item in validation_items:
            if item["uuid"] == item_uuid:
                item.update(**validation_item)
        return self.__class__(validation_items)

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

    def validate_at_most_one(
        self, field: Callable, predicate: Callable, error: ErrorCodes
    ) -> None:
        """Validate an "at most one" constraint given by `field` and `predicate`,
        raising an `HTTPException` if the constraint is violated.

        This checks that at most one validation item in a group satisfies the given
        predicate when looking at the value returned by the `field` callable.

        If more than one validation item satisfies the predicate, a member of the `
        ErrorCodes` enum is called, raising an `HTTPException`.
        """
        counter = Counter(
            field(item) for item in self.validation_items if predicate(item)
        )
        if any(count > 1 for count in counter.values()):
            error()
