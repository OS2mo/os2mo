# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from collections.abc import Callable
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from textwrap import dedent
from typing import Annotated
from typing import Any
from uuid import UUID

import strawberry
from pydantic import PositiveInt
from pydantic import ValidationError
from strawberry import UNSET
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from ...middleware import set_graphql_dates
from .resolver_map import resolver_map
from .types import Cursor
from .validity import OpenValidityModel
from mora.util import CPR
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import EngagementAssociationRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import ITSystemRead
from ramodels.mo.details import ITUserRead
from ramodels.mo.details import KLERead
from ramodels.mo.details import LeaveRead
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import RelatedUnitRead
from ramodels.mo.details import RoleRead


LimitType = Annotated[
    PositiveInt | None,
    strawberry.argument(
        description=dedent(
            r"""
    Limit the maximum number of elements to fetch.

    | `limit`      | \# elements fetched |
    |--------------|---------------------|
    | not provided | All                 |
    | `null`       | All                 |
    | `0`          | `0` (`*`)           |
    | `x`          | Between `0` and `x` |

    `*`: This behavior is equivalent to SQL's `LIMIT 0` behavior.

    Note:

    Sometimes the caller may receieve a shorter list (or even an empty list) of results compared to the expected per the limit argument.

    This may seem confusing, but it is the expected behavior given the way that limiting is implemented in the bitemporal database layer, combined with how filtering and object change consolidation is handled.

    Not to worry; all the expected elements will eventually be returned, as long as the iteration is continued until the `next_cursor` is `null`.
    """
        )
    ),
]
# Cursor's input is a Base64 encoded string eg. `Mw==`, but is parsed as an int
# and returned again as a Base64 encoded string.
# This way we can use it for indexing and calculations
CursorType = Annotated[
    Cursor | None,
    strawberry.argument(
        description=dedent(
            """
    Cursor defining the next elements to fetch.

    | `cursor`       | Next element is    |
    |----------------|--------------------|
    | not provided   | First              |
    | `null`         | First              |
    | `"MA=="` (`*`) | First after Cursor |

    `*`: Placeholder for the cursor returned by the previous iteration.
    """
        )
    ),
]


def gen_filter_string(title: str, key: str) -> str:
    return (
        dedent(
            f"""
        {title} filter limiting which entries are returned.
        """
        )
        + gen_filter_table(key)
    )


def gen_filter_table(key: str) -> str:
    return dedent(
        f"""

        | `{key}`      | Elements returned                            |
        |--------------|----------------------------------------------|
        | not provided | All                                          |
        | `null`       | All                                          |
        | `[]`         | None                                         |
        | `"x"`        | `["x"]` or `[]` (`*`)                        |
        | `["x", "y"]` | `["x", "y"]`, `["x"]`, `["y"]` or `[]` (`*`) |

        `*`: Elements returned depends on which elements were found.
        """
    )


UUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("UUID", "uuids")),
]
UserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(description=gen_filter_string("User-key", "user_keys")),
]

FromDateFilterType = Annotated[
    datetime | None,
    strawberry.argument(
        description=dedent(
            """
    Limit the elements returned by their starting validity.
    """
        )
    ),
]
ToDateFilterType = Annotated[
    datetime | None,
    strawberry.argument(
        description=dedent(
            """
    Limit the elements returned by their ending validity.
    """
        )
    ),
]

FacetUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("Facet UUID", "facets")),
]
FacetUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string("Facet user-key", "facet_user_keys")
    ),
]

ParentUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("Parent UUID", "parents")),
]
ParentUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string("Parent user-key", "parent_user_keys")
    ),
]

AddressTypeUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Address type UUID", "address_types")
    ),
]
AddressTypeUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string("Address type user-key", "address_type_user_keys")
    ),
]
EmployeeUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(description=gen_filter_string("Employee UUID", "employees")),
]
EngagementUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Engagement UUID", "engagements")
    ),
]
OrgUnitUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Organisational Unit UUID", "org_units")
    ),
]

AssociationTypeUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=gen_filter_string("Association type UUID", "association_types")
    ),
]
AssociationTypeUserKeysFilterType = Annotated[
    list[str] | None,
    strawberry.argument(
        description=gen_filter_string(
            "Association type user-key", "association_type_user_keys"
        )
    ),
]

CPRNumberFilterType = Annotated[
    list[CPR] | None,
    strawberry.argument(description=gen_filter_string("CPR number", "cpr_numbers")),
]

HierarchiesUUIDsFilterType = Annotated[
    list[UUID] | None,
    strawberry.argument(
        description=dedent(
            """
        Filter organisation units by their organisational hierarchy labels.

        Can be used to extract a subset of the organisational structure.

        Examples of user-keys:
        * `"Line-management"`
        * `"Self-owned institution"`
        * `"Outside organisation"`
        * `"Hidden"`

        Note:
        The organisation-gatekeeper integration is one option to keep hierarchy labels up-to-date.
        """
        )
        + gen_filter_table("hierarchies")
    ),
]


class PagedResolver:
    async def resolve(
        self,
        *args: Any,
        limit: LimitType = None,
        cursor: CursorType = None,
        **kwargs: Any,
    ) -> Any:
        raise NotImplementedError


class Resolver(PagedResolver):
    neutral_element_constructor: Callable[[], Any] = dict

    def __init__(self, model: type) -> None:
        """Create a field resolver by specifying a model.

        Args:
            model: The MOModel.
        """
        self.model: type = model

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
    ):
        """Resolve a query using the specified arguments.

        Args:
            uuids: Only retrieve these UUIDs. Defaults to None.
            user_keys: Only retrieve these user_keys. Defaults to None.
            limit: The maximum number of elements to return. Fewer elements may be
                returned if the query itself yields fewer elements.
            from_date: Lower bound of the object validity (bitemporal lookup).
                Defaults to UNSET, in which case from_date is today.
            to_date: Upper bound of the object validity (bitemporal lookup).
                Defaults to UNSET, in which case to_date is from_date + 1 ms.

        Note:
            While OFFSET and LIMITing is done in LoRa/SQL, further filtering is
            sometimes applied in MO. Confusingly, this means that receiving a list
            shorter than the requested limit does not imply that we are at the end.

        Returns:
            List of response objects based on getters/loaders.

        Note:
            The default behaviour of from_date and to_date, i.e. both being
            UNSET, is equivalent to validity=present in the service API.
        """
        return await self._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
        )

    async def _resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        **kwargs: Any,
    ):
        """The internal resolve interface, allowing for kwargs."""
        # Dates
        dates = get_date_interval(from_date, to_date)
        set_graphql_dates(dates)

        # UUIDs
        if uuids is not None:
            if limit is not None or cursor is not None:
                raise ValueError("Cannot filter 'uuid' with 'limit' or 'cursor'")
            # Early return on empty UUID list
            if not uuids:
                return self.neutral_element_constructor()
            resolver_name = resolver_map[self.model]["loader"]
            return await self.get_by_uuid(info.context[resolver_name], uuids)

        # User keys
        if user_keys is not None:
            # Early return on empty user-key list
            if not user_keys:
                return self.neutral_element_constructor()
            # We need to explicitly use a 'SIMILAR TO' search in LoRa, as the default is
            # to 'AND' filters of the same name, i.e. 'http://lora?bvn=x&bvn=y' means
            # "bvn is x AND Y", which is never true. Ideally, we'd use a different query
            # parameter key for these queries - such as '&bvn~=foo' - but unfortunately
            # such keys are hard-coded in a LOT of different places throughout LoRa.
            # For this reason, it is easier to pass the sentinel in the VALUE at this
            # point in time.
            # Additionally, the values are regex-escaped since the joined string will be
            # interpreted as one big regular expression in LoRa's SQL.
            use_is_similar_sentinel = "|LORA-PLEASE-USE-IS-SIMILAR|"
            escaped_user_keys = (re.escape(k) for k in user_keys)
            kwargs["bvn"] = use_is_similar_sentinel + "|".join(escaped_user_keys)

        # Pagination
        if limit is not None:
            kwargs["maximalantalresultater"] = limit
        if cursor is not None:
            kwargs["foersteresultat"] = cursor

        resolver_name = resolver_map[self.model]["getter"]
        return await info.context[resolver_name](**kwargs)

    @staticmethod
    # type: ignore[no-untyped-def,override]
    async def get_by_uuid(dataloader: DataLoader, uuids: list[UUID]):
        deduplicated_uuids = list(set(uuids))
        responses = await dataloader.load_many(deduplicated_uuids)
        # Filter empty objects, see: https://redmine.magenta-aps.dk/issues/51523.
        return {
            uuid: objects
            for uuid, objects in zip(deduplicated_uuids, responses)
            if objects != []
        }


async def user_keys2uuids(
    resolver: Resolver, info: Info, user_keys: list[str]
) -> list[UUID]:
    """Translate a list of user-keys into a list of UUIDs.

    Args:
        resolver: The resolver used to resolve user-keys to UUIDs.
        info: The strawberry execution context.
        user_keys: The user-keys to resolve.

    Returns:
        A list of UUIDs resolved from the user-keys.
    """
    objects = await resolver.resolve(info, user_keys=user_keys)
    uuids = list(objects.keys())
    if uuids:
        return uuids

    # If the user key(s) were not in found in LoRa, we would return an empty list here.
    # Unfortunately, filtering a key on an empty list in LoRa is equivalent to _not
    # filtering on that key at all_. This is obviously very confusing to anyone who has
    # ever used SQL, but we are too scared to change the behaviour. Instead, to
    # circumvent this issue, we send a UUID which we know (hope) is never present.
    return [UUID("00000000-baad-1dea-ca11-fa11fa11c0de")]


class FacetResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(FacetRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        parents: ParentUUIDsFilterType = None,
        parent_user_keys: ParentUserKeysFilterType = None,
    ):
        """Resolve facets."""
        if parent_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            parents = parents or []
            parents.extend(
                await user_keys2uuids(FacetResolver(), info, parent_user_keys)
            )

        kwargs = {}
        if parents is not None:
            kwargs["facettilhoerer"] = parents

        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=None,  # from -inf
            to_date=None,  # to inf
            **kwargs,
        )


class ClassResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ClassRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        facets: FacetUUIDsFilterType = None,
        facet_user_keys: FacetUserKeysFilterType = None,
        parents: ParentUUIDsFilterType = None,
        parent_user_keys: ParentUserKeysFilterType = None,
    ):
        """Resolve classes."""
        if facet_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            facets = facets or []
            facets.extend(await user_keys2uuids(FacetResolver(), info, facet_user_keys))

        if parent_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            parents = parents or []
            parents.extend(
                await user_keys2uuids(ClassResolver(), info, parent_user_keys)
            )

        kwargs = {}
        if facets is not None:
            kwargs["facet"] = facets
        if parents is not None:
            kwargs["overordnetklasse"] = parents

        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=None,  # from -inf
            to_date=None,  # to inf
            **kwargs,
        )


class AddressResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AddressRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        address_types: AddressTypeUUIDsFilterType = None,
        address_type_user_keys: AddressTypeUserKeysFilterType = None,
        employees: EmployeeUUIDsFilterType = None,
        engagements: EngagementUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve addresses."""
        if address_type_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            address_types = address_types or []
            address_types.extend(
                await user_keys2uuids(ClassResolver(), info, address_type_user_keys)
            )

        kwargs = {}
        if address_types is not None:
            kwargs["organisatoriskfunktionstype"] = address_types
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if engagements is not None:
            kwargs["tilknyttedefunktioner"] = engagements
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units

        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class AssociationResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AssociationRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
        association_types: AssociationTypeUUIDsFilterType = None,
        association_type_user_keys: AssociationTypeUserKeysFilterType = None,
    ):
        """Resolve associations."""
        if association_type_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            association_types = association_types or []
            association_types.extend(
                await user_keys2uuids(ClassResolver(), info, association_type_user_keys)
            )

        kwargs = {}
        if association_types is not None:
            kwargs["organisatoriskfunktionstype"] = association_types
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class EmployeeResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EmployeeRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        cpr_numbers: CPRNumberFilterType = None,
    ):
        """Resolve employees."""
        kwargs = {}
        if cpr_numbers is not None:
            kwargs["tilknyttedepersoner"] = [
                f"urn:dk:cpr:person:{c}" for c in cpr_numbers
            ]
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class EngagementResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EngagementRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve engagements."""
        kwargs = {}
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class ManagerResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ManagerRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve managers."""
        kwargs = {}
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class OrganisationUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(OrganisationUnitRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        parents: ParentUUIDsFilterType = UNSET,
        hierarchies: HierarchiesUUIDsFilterType = None,
    ):
        """Resolve organisation units."""
        kwargs = {}
        # Parents
        if parents is None:
            org = await info.context["org_loader"].load(0)
            kwargs["overordnet"] = org.uuid
        elif parents is not UNSET:
            kwargs["overordnet"] = parents
        # Hierarchy
        if hierarchies is not None:
            kwargs["opmærkning"] = hierarchies

        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class EngagementAssociationResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EngagementAssociationRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        engagements: EngagementUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve engagement-associations."""
        kwargs = {}
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if engagements is not None:
            kwargs["tilknyttedefunktioner"] = engagements
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class ITSystemResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITSystemRead)


class ITUserResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITUserRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve it-users."""
        kwargs = {}
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class KLEResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(KLERead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve kle."""
        kwargs = {}
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class LeaveResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(LeaveRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve leaves."""
        kwargs = {}
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class RelatedUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RelatedUnitRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve leaves."""
        kwargs = {}
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class RoleResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RoleRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        uuids: UUIDsFilterType = None,
        user_keys: UserKeysFilterType = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        from_date: FromDateFilterType = UNSET,
        to_date: ToDateFilterType = UNSET,
        employees: EmployeeUUIDsFilterType = None,
        org_units: OrgUnitUUIDsFilterType = None,
    ):
        """Resolve roles."""
        kwargs = {}
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if org_units is not None:
            kwargs["tilknyttedeenheder"] = org_units
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            cursor=cursor,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


def get_date_interval(
    from_date: FromDateFilterType = UNSET, to_date: ToDateFilterType = UNSET
) -> OpenValidityModel:
    """Get the date interval for GraphQL queries to support bitemporal lookups.

    Args:
        from_date: The lower bound of the request interval
        to_date: The upper bound of the request interval

    Raises:
        ValueError: If lower bound is none and upper bound is unset
        ValueError: If the interval is invalid, e.g. lower > upper
    """
    if from_date is UNSET:
        from_date = datetime.now(tz=timezone.utc)
    if to_date is UNSET:
        if from_date is None:
            raise ValueError(
                "Cannot infer UNSET to_date from interval starting at -infinity"
            )
        to_date = from_date + timedelta(milliseconds=1)
    try:
        interval = OpenValidityModel(from_date=from_date, to_date=to_date)
    except ValidationError as v_error:
        # Pydantic errors are ugly in GraphQL so we get the msg part only
        message = ", ".join([err["msg"] for err in v_error.errors()])
        raise ValueError(message)
    return interval
