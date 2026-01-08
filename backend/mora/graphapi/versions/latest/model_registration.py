# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any
import strawberry
from strawberry import Info
from .moobject import MOObject
from typing import Generic
from .registration import Registration

# The below concrete classes are instantiated using `resolve_type` on the Registration
# interface within `registration.py`. Once the type is found a sanity check is performed
# by strawberry which validates that the instance being constructed is of the expected
# subtype, this is however not the case, as the instance is a SQLAlchemy Row instance
# produced by the registration_resolver and the expected type is a FacetRegistration
# for instance, thus the sanity check done by strawberry fails, and the mapping done by
# `resolve_type` is rejected. We know however that the implementation of `resolve_type`
# is trustworthy and that we simply wish to construct our FacetRegistration or similar
# using the SQLAlchemy row in our constructor, so we can safely return `True` within
# the base-class' `is_type_of` method to disable the sanity check and simply trust the
# decision made by `resolve_type`.


@strawberry.type
class ModelRegistration(Registration, Generic[MOObject]):
    @classmethod
    def is_type_of(cls, model: Registration, info: Info) -> bool:
        # We trust resolve_type made the right choice
        return True

    @strawberry.field
    async def current(
        self,
        root: Any,
        info: Info,
    ) -> MOObject | None:
        return None
