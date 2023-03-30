# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from operator import attrgetter
from typing import Any
from uuid import UUID

from pydantic import PositiveInt
from pydantic import ValidationError
from strawberry import UNSET
from strawberry.dataloader import DataLoader
from strawberry.types import Info

from ...middleware import set_graphql_dates
from .dataloaders import MOModel
from .resolver_map import resolver_map
from .schema import OpenValidityModel
from .schema import Response
from mora.util import CPR
from ramodels.mo import ClassRead
from ramodels.mo import EmployeeRead
from ramodels.mo import FacetRead
from ramodels.mo import OrganisationRead
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


class StaticResolver:
    def __init__(self, model: MOModel) -> None:
        """Create a field resolver by specifying a model.

        Args:
            model: The MOModel.
        """
        self.model = model

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
    ):
        """Resolve queries with no validity, i.e. class/facet/itsystem.

        Uses getters/loaders from the context.
        """
        return await self._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            offset=offset,
            from_date=None,  # from -inf
            to_date=None,  # to inf
        )

    async def _resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
        **kwargs: Any,
    ):
        """The internal resolve interface, allowing for kwargs."""
        # Dates
        dates = get_date_interval(from_date, to_date)
        set_graphql_dates(dates)

        # UUIDs
        if uuids is not None:
            if limit is not None or offset is not None:
                raise ValueError("Cannot filter 'uuid' with 'limit' or 'offset'")
            return [Response(model=self.model, uuid=uuid) for uuid in uuids]

        # User keys
        if user_keys is not None:
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
        if offset is not None:
            kwargs["foersteresultat"] = offset

        resolver_name = resolver_map[self.model]["getter"]
        return await info.context[resolver_name](**kwargs)

    @staticmethod
    # type: ignore[no-untyped-def]
    async def get_by_uuid(dataloader: DataLoader, uuids: list[UUID]):
        """Get data from a list of UUIDs. Only unique UUIDs are loaded.

        Args:
            dataloader: Strawberry dataloader to use.
            uuids: List of UUIDs to load.

        Returns:
            List of objects found.
            Type: Union[list[ClassRead], list[FacetRead], list[ITSystemRead]]
        """
        responses = await dataloader.load_many(list(set(uuids)))
        if not responses:
            return responses
        # These loaders can return None, which we need to filter here.
        return [response for response in responses if response is not None]


class Resolver(StaticResolver):
    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
    ):
        """Resolve a query using the specified arguments.

        Args:
            uuids: Only retrieve these UUIDs. Defaults to None.
            user_keys: Only retrieve these user_keys. Defaults to None.
            limit: The maximum number of elements to return. Fewer elements may be
                returned if the query itself yields fewer elements.
            offset: Skips this many elements before beginning to return elements. An
                offset of 0 is the same as omitting offset, as is null.
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
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
        )

    @staticmethod
    async def get_by_uuid(
        dataloader: DataLoader, uuids: list[UUID]
    ) -> list[Response[MOModel]]:
        responses = await dataloader.load_many(list(set(uuids)))
        # Filter empty objects, see: https://redmine.magenta-aps.dk/issues/51523.
        return [response for response in responses if response.objects != []]


class FacetResolver(StaticResolver):
    def __init__(self) -> None:
        super().__init__(FacetRead)


class ClassResolver(StaticResolver):
    def __init__(self) -> None:
        super().__init__(ClassRead)

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        facets: list[UUID] | None = None,
        facet_user_keys: list[str] | None = None,
    ):
        """Resolve classes."""
        if facet_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            facet_objects = await FacetResolver().resolve(
                info, user_keys=facet_user_keys
            )
            facet_uuids = list(map(attrgetter("uuid"), facet_objects))
            if facets is None:
                facets = []
            facets.extend(facet_uuids)

        kwargs = {}
        if facets is not None:
            kwargs["facet"] = facets

        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            offset=offset,
            from_date=None,  # from -inf
            to_date=None,  # to inf
            **kwargs,
        )


class AddressResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AddressRead)

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
        address_types: list[UUID] | None = None,
        address_type_user_keys: list[str] | None = None,
        employees: list[UUID] | None = None,
        engagements: list[UUID] | None = None,
    ):
        """Resolve addresses."""
        if address_type_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            address_type_objects = await ClassResolver().resolve(
                info, user_keys=address_type_user_keys
            )
            address_type_uuids = list(map(attrgetter("uuid"), address_type_objects))
            if address_types is None:
                address_types = []
            address_types.extend(address_type_uuids)

        kwargs = {}
        if address_types is not None:
            kwargs["organisatoriskfunktionstype"] = address_types
        if employees is not None:
            kwargs["tilknyttedebrugere"] = employees
        if engagements is not None:
            kwargs["tilknyttedefunktioner"] = engagements
        return await super()._resolve(
            info=info,
            uuids=uuids,
            user_keys=user_keys,
            limit=limit,
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class AssociationResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(AssociationRead)

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
        employees: list[UUID] | None = None,
        org_units: list[UUID] | None = None,
        association_types: list[UUID] | None = None,
        association_type_user_keys: list[str] | None = None,
    ):
        """Resolve associations."""
        if association_type_user_keys is not None:
            # Convert user-keys to UUIDs for the UUID filtering
            association_type_objects = await ClassResolver().resolve(
                info, user_keys=association_type_user_keys
            )
            association_type_uuids = list(
                map(attrgetter("uuid"), association_type_objects)
            )
            if association_types is None:
                association_types = []
            association_types.extend(association_type_uuids)

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
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class EmployeeResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EmployeeRead)

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
        cpr_numbers: list[CPR] | None = None,
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
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class EngagementResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EngagementRead)

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
        employees: list[UUID] | None = None,
        org_units: list[UUID] | None = None,
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
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class ManagerResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ManagerRead)

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
        employees: list[UUID] | None = None,
        org_units: list[UUID] | None = None,
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
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class OrganisationUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(OrganisationUnitRead)

    async def resolve(  # type: ignore[no-untyped-def]
        self,
        info: Info,
        uuids: list[UUID] | None = None,
        user_keys: list[str] | None = None,
        limit: PositiveInt | None = None,
        offset: PositiveInt | None = None,
        from_date: datetime | None = UNSET,
        to_date: datetime | None = UNSET,
        parents: list[UUID] | None = UNSET,
        hierarchies: list[UUID] | None = None,
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
            offset=offset,
            from_date=from_date,
            to_date=to_date,
            **kwargs,
        )


class EngagementAssociationResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(EngagementAssociationRead)


class ITSystemResolver(StaticResolver):
    def __init__(self) -> None:
        super().__init__(ITSystemRead)


class ITUserResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(ITUserRead)


class KLEResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(KLERead)


class LeaveResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(LeaveRead)


class RelatedUnitResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RelatedUnitRead)


class RoleResolver(Resolver):
    def __init__(self) -> None:
        super().__init__(RoleRead)


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
