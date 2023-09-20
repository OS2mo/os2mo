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
from .filters import AddressFilter
from .filters import AssociationFilter
from .filters import BaseFilter
from .filters import ClassFilter
from .filters import EmployeeFilter
from .filters import EngagementFilter
from .filters import FacetFilter
from .filters import ITSystemFilter
from .filters import ITUserFilter
from .filters import KLEFilter
from .filters import LeaveFilter
from .filters import ManagerFilter
from .filters import OrganisationUnitFilter
from .filters import OwnerFilter
from .filters import RelatedUnitFilter
from .filters import RoleFilter
from .resolver_map import resolver_map
from .types import Cursor
from .validity import OpenValidityModel
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationUnitRead
from ramodels.mo.details import AddressRead
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import EngagementRead
from ramodels.mo.details import ITSystemRead
from ramodels.mo.details import ITUserRead
from ramodels.mo.details import KLERead
from ramodels.mo.details import LeaveRead
from ramodels.mo.details import ManagerRead
from ramodels.mo.details import OwnerRead
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

CursorType = Annotated[
    Cursor | None,
    strawberry.argument(
        description=dedent(
            """\
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
        filter: BaseFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
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
            filter=filter,
            limit=limit,
            cursor=cursor,
        )

    async def _resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: BaseFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
        **kwargs: Any,
    ):
        """The internal resolve interface, allowing for kwargs."""
        # Filter
        if filter is None:
            filter = BaseFilter()

        # Dates
        dates = get_date_interval(filter.from_date, filter.to_date)
        set_graphql_dates(dates)

        # UUIDs
        if filter.uuids is not None:
            if limit is not None or cursor is not None:
                raise ValueError("Cannot filter 'uuid' with 'limit' or 'cursor'")
            # Early return on empty UUID list
            if not filter.uuids:
                return self.neutral_element_constructor()
            resolver_name = resolver_map[self.model]["loader"]
            return await self.get_by_uuid(info.context[resolver_name], filter.uuids)

        # User keys
        if filter.user_keys is not None:
            # Early return on empty user-key list
            if not filter.user_keys:
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
            escaped_user_keys = (re.escape(k) for k in filter.user_keys)
            kwargs["bvn"] = use_is_similar_sentinel + "|".join(escaped_user_keys)

        # Pagination
        if limit is not None:
            kwargs["maximalantalresultater"] = limit
        if cursor is not None:
            kwargs["foersteresultat"] = cursor.offset
            kwargs["registreringstid"] = str(cursor.registration_time)

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


async def filter2uuids(
    resolver: Resolver,
    info: Info,
    filter: BaseFilter,
) -> list[UUID]:
    """Resolve into a list of UUIDs with the given filter.

    Args:
        resolver: The resolver used to resolve user-keys to UUIDs.
        info: The strawberry execution context.
        filter: Filter instance passed to the resolver.

    Returns:
        A list of UUIDs.
    """
    objects = await resolver.resolve(info, filter=filter)
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
        filter: FacetFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve facets."""
        if filter is None:
            filter = FacetFilter()

        parents = filter.parents
        if filter.parent_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            parents = filter.parents or []
            parents.extend(
                await filter2uuids(
                    FacetResolver(),
                    info,
                    FacetFilter(user_keys=filter.parent_user_keys),  # type: ignore[arg-type]
                )
            )

        kwargs = {}
        if parents is not None:
            kwargs["facettilhoerer"] = parents

        return await super()._resolve(
            info=info,
            # TODO: pass filter=filter directly when the object is non-static
            filter=BaseFilter(
                uuids=filter.uuids,
                user_keys=filter.user_keys,
                from_date=None,  # from -inf
                to_date=None,  # to inf
            ),
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class ClassResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ClassRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: ClassFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve classes."""
        if filter is None:
            filter = ClassFilter()

        facets = filter.facets
        if filter.facet_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            facets = facets or []
            facets.extend(
                await filter2uuids(
                    FacetResolver(),
                    info,
                    FacetFilter(user_keys=filter.facet_user_keys),  # type: ignore[arg-type]
                )
            )

        parents = filter.parents
        if filter.parent_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            parents = parents or []
            parents.extend(
                await filter2uuids(
                    ClassResolver(),
                    info,
                    ClassFilter(user_keys=filter.parent_user_keys),  # type: ignore[arg-type]
                )
            )

        kwargs = {}
        if facets is not None:
            kwargs["facet"] = facets
        if parents is not None:
            kwargs["overordnetklasse"] = parents

        return await super()._resolve(
            info=info,
            filter=BaseFilter(
                uuids=filter.uuids,
                user_keys=filter.user_keys,
                from_date=None,  # from -inf
                to_date=None,  # to inf
            ),
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class AddressResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AddressRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: AddressFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve addresses."""
        if filter is None:
            filter = AddressFilter()

        address_types = filter.address_types or []
        if filter.address_type_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            address_types.extend(
                await filter2uuids(
                    ClassResolver(),
                    info,
                    ClassFilter(user_keys=filter.address_type_user_keys),  # type: ignore[arg-type]
                )
            )

        kwargs = {}
        if address_types is not None:
            kwargs["organisatoriskfunktionstype"] = address_types
        if filter.employees is not None:
            kwargs["tilknyttedebrugere"] = filter.employees
        if filter.engagements is not None:
            kwargs["tilknyttedefunktioner"] = filter.engagements
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units

        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class AssociationResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AssociationRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: AssociationFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve associations."""
        if filter is None:
            filter = AssociationFilter()

        association_types = filter.association_types or []
        if filter.association_type_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            association_types.extend(
                await filter2uuids(
                    ClassResolver(),
                    info,
                    ClassFilter(user_keys=filter.association_type_user_keys),  # type: ignore[arg-type]
                )
            )

        kwargs = {}
        if association_types is not None:
            kwargs["organisatoriskfunktionstype"] = association_types
        if filter.employees is not None:
            kwargs["tilknyttedebrugere"] = filter.employees
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        associations = await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )

        if filter.it_association is not None:
            filtered_data = {}
            for uuid, association_fields in associations.items():
                if filter.it_association:
                    filtered_associations = [
                        association
                        for association in association_fields
                        if association.it_user_uuid is not None
                    ]
                else:
                    filtered_associations = [
                        association
                        for association in association_fields
                        if association.it_user_uuid is None
                    ]
                if filtered_associations:
                    filtered_data[uuid] = filtered_associations
            associations = filtered_data

        return associations


class EmployeeResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EmployeeRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: EmployeeFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve employees."""
        if filter is None:
            filter = EmployeeFilter()

        kwargs = {}
        if filter.cpr_numbers is not None:
            kwargs["tilknyttedepersoner"] = [
                f"urn:dk:cpr:person:{c}" for c in filter.cpr_numbers
            ]
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class EngagementResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EngagementRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: EngagementFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve engagements."""
        if filter is None:
            filter = EngagementFilter()

        kwargs = {}
        if filter.employees is not None:
            kwargs["tilknyttedebrugere"] = filter.employees
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class ManagerResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ManagerRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: ManagerFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve managers."""
        if filter is None:
            filter = ManagerFilter()

        kwargs = {}
        if filter.employees is not None:
            kwargs["tilknyttedebrugere"] = filter.employees
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class OwnerResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(OwnerRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: OwnerFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve owners."""
        if filter is None:
            filter = OwnerFilter()

        kwargs = {}
        if filter.employees is not None:
            # TODO: Figure out why this uses personer instead of brugere
            kwargs["tilknyttedepersoner"] = filter.employees
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class OrganisationUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(OrganisationUnitRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: OrganisationUnitFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve organisation units."""
        if filter is None:
            filter = OrganisationUnitFilter()

        kwargs = {}
        # Parents
        if filter.parents is None:
            org = await info.context["org_loader"].load(0)
            kwargs["overordnet"] = org.uuid
        elif filter.parents is not UNSET:
            kwargs["overordnet"] = filter.parents
        # Hierarchy
        if filter.hierarchies is not None:
            kwargs["opmærkning"] = filter.hierarchies

        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class ITSystemResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITSystemRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        # TODO: change BaseFilter to ITSystemFilter in a breaking change or new version
        filter: BaseFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve it-systems."""
        if filter is None:
            filter = ITSystemFilter()

        return await super().resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
        )


class ITUserResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITUserRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: ITUserFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve it-users."""
        if filter is None:
            filter = ITUserFilter()

        kwargs = {}
        if filter.employees is not None:
            kwargs["tilknyttedebrugere"] = filter.employees
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        if filter.itsystem_uuids is not None:
            kwargs["tilknyttedeitsystemer"] = filter.itsystem_uuids

        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class KLEResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(KLERead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: KLEFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve kle."""
        if filter is None:
            filter = KLEFilter()

        kwargs = {}
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class LeaveResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(LeaveRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: LeaveFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve leaves."""
        if filter is None:
            filter = LeaveFilter()

        kwargs = {}
        if filter.employees is not None:
            kwargs["tilknyttedebrugere"] = filter.employees
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class RelatedUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RelatedUnitRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: RelatedUnitFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve related units."""
        if filter is None:
            filter = RelatedUnitFilter()

        kwargs = {}
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


class RoleResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RoleRead)

    async def resolve(  # type: ignore[no-untyped-def,override]
        self,
        info: Info,
        filter: RoleFilter | None = None,
        limit: LimitType = None,
        cursor: CursorType = None,
    ):
        """Resolve roles."""
        if filter is None:
            filter = RoleFilter()

        kwargs = {}
        if filter.employees is not None:
            kwargs["tilknyttedebrugere"] = filter.employees
        if filter.org_units is not None:
            kwargs["tilknyttedeenheder"] = filter.org_units
        return await super()._resolve(
            info=info,
            filter=filter,
            limit=limit,
            cursor=cursor,
            **kwargs,
        )


def get_date_interval(
    from_date: datetime | None = UNSET, to_date: datetime | None = UNSET
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
