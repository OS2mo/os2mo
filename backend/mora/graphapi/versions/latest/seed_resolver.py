# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Functions related to resolver seeding."""

import dataclasses
import typing
from collections.abc import Awaitable
from collections.abc import Callable
from functools import cache
from inspect import Parameter
from inspect import signature
from types import NoneType
from typing import Any
from typing import TypeVar

import strawberry

R = TypeVar("R")


@cache
def get_bound_filter(
    filter_class: type,
    seeds: frozenset[str],
) -> type:
    """Construct a bound Filter Strawberry input type with the seeded fields removed.

    The function's return is @cached since Strawberry exposes the type in the GraphQL
    schema, so each unique original filter and seeds combination has to refer to the
    same python object.

    Args:
        filter_class: The class of the original, unseeded filter.
        seeds: Seed keys. Passed as a frozenset to be hashable.

    Returns:
        A copy of the given filter class with the seeded fields removed.
    """
    # Examples: UuidBoundEmployeeFilter, FacetsBoundClassFilter
    cls_name = "{seeds}Bound{original_filter}".format(
        seeds="".join(s.title() for s in sorted(seeds)),
        original_filter=filter_class.__name__,
    )
    # Strawberry.input is incredibly badly typed; runtime check is better than nothing
    assert dataclasses.is_dataclass(filter_class)
    bound_filter_class = dataclasses.make_dataclass(
        cls_name=cls_name,
        fields=[
            (f.name, f.type, f)
            for f in dataclasses.fields(filter_class)
            if f.name not in seeds
        ],
    )
    return strawberry.input(bound_filter_class)


def seed_resolver(
    resolver_func: Callable[..., Awaitable[R]],
    seeds: dict[str, Callable[[Any], Any]] | None = None,
) -> Callable[..., Awaitable[R]]:
    """Seed the provided resolver function to be used in a field-level context.

    This function serves to create a new function which calls the provided resolver
    function with a seeded `filter` values from the field-context in which it is called.

    Example:
        A resolver exists to load organisation units, namely `organisation_unit_resolver`.
        This resolver accepts a `filter` parameter with a `parents` field, which, given
        a UUID of an existing organisation unit, loads all of its children.

        From our top-level `Query` object context, the caller can set this field
        explicitly, however on the OrganisationUnit field-level, we would like this
        field to be given by the context, i.e. when asking for `children` on an
        organisation unit, we expect the `parent` field on the filter to be set
        to the object we call `children` on.

        This can be achieved by setting `seeds` to a dictionary that sets `parents` to
        a callable that extracts the root object's `uuid` from the object itself:
        ```
        child_count: int = strawberry.field(
            description="Children count of the organisation unit.",
            resolver=seed_resolver(
                organisation_unit_resolver,
                {"parents": lambda root: [root.uuid]},
            ),
            ...
        )
        ```

    Args:
        resolver_func: The top-level resolver function to seed arguments to.
        seeds:
            A dictionary mapping from parameter name to callables resolving the argument
            values from the root object.

    Returns:
        A seeded resolver function that accepts the same parameters as `resolver_func`,
        except with a new `filter` object type with the `seeds` keys removed as fields,
        and a `root` parameter with the 'any' type added.
    """
    # If no seeds was provided, default to the empty dict
    seeds = seeds or {}

    # Extract the original `filter` class from the provided resolver
    sig = signature(resolver_func)
    parameters = sig.parameters.copy()
    original_filter_parameter = parameters.pop("filter")
    original_filter_type = typing.get_args(original_filter_parameter.annotation)
    original_filter_class, none = original_filter_type
    # For now, seeding is limited to resolvers which define their filter as
    # filter: SomeFilter | None
    # Assert that this is indeed what was passed.
    assert none is NoneType

    # Create a new filter class with the seeded fields removed. Strawberry exposes the
    # type in the GraphQL schema, so each one has to be named uniquely and refer to the
    # same python object instance. We use a function with @cache to achieve this.
    bound_filter_class = get_bound_filter(
        original_filter_class, frozenset(seeds.keys())
    )
    bound_filter_type = bound_filter_class | None

    # Wrap the original resolver to instead accept a bound filter with the seeded
    # field(s) removed. At call-time, we construct an instance of the original filter
    # class with the user-provided and seeded values combined and pass it to the
    # resolver.
    async def seeded_resolver(
        *args: Any,
        root: Any,
        filter: bound_filter_type = None,  # type: ignore[valid-type]
        **kwargs: Any,
    ) -> R:
        assert seeds is not None
        filter_args = {}
        # Pass user-provided filters from the bound filter
        if filter is not None:
            # We iterate the fields explicitly, rather than use dataclasses.asdict(),
            # to create a shallow copy. This ensures nested Filter objects, which we do
            # not seed anyway, are not converted to dicts.
            filter_args.update(
                (field.name, getattr(filter, field.name))
                for field in dataclasses.fields(filter)
            )
        # Resolve arguments from the root object
        for key, argument_callable in seeds.items():
            filter_args[key] = argument_callable(root)
        # Create an instance of the original filter, as expected by the resolver
        filter = original_filter_class(**filter_args)
        assert "filter" not in kwargs
        return await resolver_func(*args, filter=filter, **kwargs)  # type: ignore[misc]

    # Generate and apply our new signature to the seeded_resolver function. The `root`
    # parameter is required for all the `seeds` resolvers to determine call-time
    # parameters.
    parameter_list = list(parameters.values())
    parameter_list = [
        Parameter("root", Parameter.POSITIONAL_OR_KEYWORD, annotation=Any),
        Parameter(
            "filter", Parameter.POSITIONAL_OR_KEYWORD, annotation=bound_filter_type
        ),
    ] + parameter_list
    new_sig = sig.replace(parameters=parameter_list)
    seeded_resolver.__signature__ = new_sig  # type: ignore[attr-defined]

    return seeded_resolver
