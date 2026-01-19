# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph - Address."""

from functools import partial
from textwrap import dedent
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

import strawberry
from more_itertools import one
from starlette_context import context
from strawberry.types import Info

from mora.service.address_handler import dar
from mora.service.address_handler import multifield_text
from mora.service.address_handler.base import AddressHandler
from mora.service.address_handler.base import get_handler_for_scope

from ..graphql_utils import LoadKey
from ..lazy import LazyClass
from ..lazy import LazyEmployee
from ..lazy import LazyEngagement
from ..lazy import LazyITUser
from ..lazy import LazyOrganisationUnit
from ..models import AddressRead
from ..models import ClassRead
from ..permissions import IsAuthenticatedPermission
from ..permissions import gen_read_permission
from ..resolvers import class_resolver
from ..resolvers import employee_resolver
from ..resolvers import engagement_resolver
from ..resolvers import it_user_resolver
from ..resolvers import organisation_unit_resolver
from ..response import Response
from ..seed_resolver import seed_resolver
from ..utils import uuid2list
from ..validity import Validity
from .utils import force_none_return_wrapper
from .utils import gen_uuid_field_deprecation
from .utils import list_to_optional_field_warning
from .utils import raise_force_none_return_if_uuid_none
from .utils import to_list
from .utils import to_one
from .utils import to_only


@strawberry.interface
class ResolvedAddress:
    value: str


@strawberry.type
class DefaultAddress(ResolvedAddress):
    pass


@strawberry.type
class MultifieldAddress(ResolvedAddress):
    value2: str

    @strawberry.field
    async def name(self, root: "MultifieldAddress") -> str:  # pragma: no cover
        return multifield_text.name(root.value, root.value2)


def extract_field(field: str) -> Any:
    @strawberry.field
    async def extractor(self: Any, root: "DARAddress") -> Any:
        dar_response = await root.resolve_dar(root)
        # The AsyncDARClient underpinning the resolve_dar function and its dar_loader
        # attempts to load the provided UUID using 4 different types of addresses in
        # DAR (by default) using a prioritized order defined by the `AddressType` enum
        # in dar_client.py within FastRAMQPI, the order is:
        # * "adresser"
        # * "adgangsadresser"
        # * "historik/adresser"
        # * "historik/adgangsadresser"
        # Thus which fields are available on our `dar_response` depends on which of
        # these address-types succesfully looked up our DAR UUID.
        #
        # This is highly problematic as the historic endpoints are marked as
        # experimental by DAR, and thus may change their fields and behavior whenever.
        # It is also problematic as the historic endpoints return very little data
        # compared to their non-historic counterparts.
        # We should probably never have relied on finding historic addresses, but it is
        # our interface now, so we cannot easily change the behavior.
        #
        # Additionally some fields only occur on adresser and not on adgangsadresser,
        # which is not something that this code was ever designed to handle.
        #
        # In general it seems the entire AsyncDARClient interface is maldesigned and we
        # must conditionally check for the existence of all fields we need.
        # Thus we use `.get` for fields here instead of `[]` to communicate that we do
        # not in fact know if the fields are present or not.
        return dar_response.get(field)

    return extractor


@strawberry.type
class DARAddress(ResolvedAddress):
    # Lookup the UUID in DAR, cached via the dataloader
    async def resolve_dar(self, root: "DARAddress") -> dict[str, Any]:
        dar_loader = context["dar_loader"]
        return await dar_loader.load(UUID(root.value))

    # Unstructured fields, provided and computed
    description: str = extract_field("betegnelse")

    @strawberry.field
    async def name(self, root: "DARAddress") -> str:
        dar_response = await root.resolve_dar(root)
        return dar.name_from_dar_object(dar_response)

    # Structured fields
    road_code: int = extract_field("vejkode")
    road_name: str = extract_field("vejnavn")
    house_number: str = extract_field("husnr")
    floor: str | None = extract_field("etage")
    door: str | None = extract_field("dør")
    zip_code: str = extract_field("postnr")
    zip_code_name: str = extract_field("postnrnavn")
    municipality_code: str = extract_field("kommunekode")
    supplementary_city: str | None = extract_field("supplerendebynavn")

    # Global position
    longitude: float = extract_field("x")
    latitude: float = extract_field("y")

    # Links
    @strawberry.field
    async def href(self, root: "DARAddress") -> str:
        dar_response = await root.resolve_dar(root)
        href = dar_response["href"]
        return urlparse(href)._replace(scheme="https").geturl()

    @strawberry.field
    async def streetmap_href(self, root: "DARAddress") -> str | None:
        dar_response = await root.resolve_dar(root)
        return dar.open_street_map_href_from_dar_object(dar_response)


async def _get_handler_object(root: AddressRead, info: Info) -> AddressHandler:
    # This function assumes that scope never changes for a class
    # If this assumption was to be broken, we would have to split the Address object on
    # scope changes, or alternatively return the attributes (value, name, etc) as
    # validities split on the scope changes, as different scopes imply different
    # interpretation of the value data.
    # TODO: Enforce this invariant during edits

    # We access the class_loader directly here for performance reasons, such that we can
    # set `start` and `end` explicitly on the LoadKey, `start` and `end` are used for
    # grouping up tasks within the `load_mo` function used within `class_loader`
    # DataLoader instance, thus having unique `start` and `end` values yield unique
    # database queries, whereas having the same values yield a single database query.
    # TODO: If the scope invariant was enforced on edits, we could simply load any
    #       address_type class validity here, instead of loading all of them.
    #       This would probably yield better performance than loading all validities,
    #       but for now however we load all of them to check our invariant.
    validities: list[ClassRead] = await info.context["class_loader"].load(
        LoadKey(
            uuid=root.address_type_uuid, start=None, end=None, registration_time=None
        )
    )
    scopes = {x.scope for x in validities}
    scope = one(scopes)
    # TODO: Consider whether it would be more sane to default to TEXT if scope is None
    assert scope is not None
    handler = get_handler_for_scope(scope)
    return handler(root.value, root.visibility_uuid, root.value2)


@strawberry.experimental.pydantic.type(
    model=AddressRead,
    description=dedent(
        """
        Address information for either an employee or organisational unit
        """
    ),
)
class Address:
    address_type_response: Response[LazyClass] = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.address_type_uuid),
        description=dedent(
            """
            The address category or type.

            In OS2mo addresses can be of a variety of different types:
            * Phone numbers
            * Addresses
            * Registration numbers
            * Card codes

            This field is what encodes the type of an address.

            Examples of user-keys:
            * "EmailUnit"
            * "p-nummer"
            * "PhoneEmployee"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    address_type: LazyClass = strawberry.field(
        resolver=to_one(
            seed_resolver(
                class_resolver, {"uuids": lambda root: [root.address_type_uuid]}
            )
        ),
        description=dedent(
            """
            The address category or type.

            In OS2mo addresses can be of a variety of different types:
            * Phone numbers
            * Addresses
            * Registration numbers
            * Card codes

            This field is what encodes the type of an address.

            Examples of user-keys:
            * "EmailUnit"
            * "p-nummer"
            * "PhoneEmployee"
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'address_type_response' instead. Will be removed in a future version of OS2mo.",
    )

    visibility_response: Response[LazyClass] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="class", uuid=root.visibility_uuid)
        if root.visibility_uuid
        else None,
        description=dedent(
            """
            Determines who can see the address and how it is exported.

            In OS2mo addresses can be of a variety of privacy classes.
            For instance OS2mo may contain a list of phone numbers for an employee;
            * A private mobile phone number
            * An internal work mobile phone number
            * A shared external phone number

            This field is what encodes the privacy class of an address.
            Thereby stating who should be allowed to see what addresses.

            Examples of user-keys:
            * `null`: Undetermined / non-classified.
            * "Secret": Should be treated carefully and perhaps not be exported.
            * "Internal" Should be treated carefully but perhaps exposed to an internal intranet.
            * "External": Can probably be exposed to the internet
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
    )

    visibility: LazyClass | None = strawberry.field(
        resolver=to_only(
            seed_resolver(
                class_resolver, {"uuids": lambda root: uuid2list(root.visibility_uuid)}
            )
        ),
        description=dedent(
            """
            Determines who can see the address and how it is exported.

            In OS2mo addresses can be of a variety of privacy classes.
            For instance OS2mo may contain a list of phone numbers for an employee;
            * A private mobile phone number
            * An internal work mobile phone number
            * A shared external phone number

            This field is what encodes the privacy class of an address.
            Thereby stating who should be allowed to see what addresses.

            Examples of user-keys:
            * `null`: Undetermined / non-classified.
            * "Secret": Should be treated carefully and perhaps not be exported.
            * "Internal" Should be treated carefully but perhaps exposed to an internal intranet.
            * "External": Can probably be exposed to the internet
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("class")],
        deprecation_reason="Use 'visibility_response' instead. Will be removed in a future version of OS2mo.",
    )

    employee: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    employee_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.employee_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            Connected employee.

            Note:
            This field is mutually exclusive with the `org_unit` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person' instead. Will be removed in a future version of OS2mo.",
    )

    person_response: Response[LazyEmployee] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="employee", uuid=root.employee_uuid)
        if root.employee_uuid
        else None,
        description=dedent(
            """
            Connected person.

            Note:
            This field is mutually exclusive with the `org_unit` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
    )

    person: list[LazyEmployee] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    employee_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.employee_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            Connected person.

            Note:
            This field is mutually exclusive with the `org_unit` field.
            """
        )
        + list_to_optional_field_warning,
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("employee")],
        deprecation_reason="Use 'person_response' instead. Will be removed in a future version of OS2mo.",
    )

    org_unit_response: Response[LazyOrganisationUnit] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(
            model="org_unit", uuid=root.org_unit_uuid
        )
        if root.org_unit_uuid
        else None,
        description=dedent(
            """
            Connected organisation unit.

            Note:
            This field is mutually exclusive with the `employee` field.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
    )

    org_unit: list[LazyOrganisationUnit] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    organisation_unit_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.org_unit_uuid,
                        )
                    },
                )
            ),
        ),
        description=dedent(
            """
            Connected organisation unit.

            Note:
            This field is mutually exclusive with the `employee` field.
            """
        ),
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("org_unit")],
        deprecation_reason="Use 'org_unit_response' instead. Will be removed in a future version of OS2mo.",
    )

    engagement_response: Response[LazyEngagement] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="engagement", uuid=root.engagement_uuid)
        if root.engagement_uuid
        else None,
        description=dedent(
            """
            Connected engagement.

            Note:
            This field is **not** mutually exclusive with neither the `employee` nor the `org_unit` field.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
    )

    engagement: list[LazyEngagement] | None = strawberry.field(
        resolver=force_none_return_wrapper(
            to_list(
                seed_resolver(
                    engagement_resolver,
                    {
                        "uuids": partial(
                            raise_force_none_return_if_uuid_none,
                            get_uuid=lambda root: root.engagement_uuid,
                        )
                    },
                )
            )
        ),
        description=dedent(
            """
            Connected engagement.

            Note:
            This field is **not** mutually exclusive with neither the `employee` nor the `org_unit` field.
            """
        ),
        permission_classes=[
            IsAuthenticatedPermission,
            gen_read_permission("engagement"),
        ],
        deprecation_reason="Use 'engagement_response' instead. Will be removed in a future version of OS2mo.",
    )

    ituser_response: Response[LazyITUser] | None = strawberry.field(  # type: ignore
        resolver=lambda root: Response(model="ituser", uuid=root.it_user_uuid)
        if root.it_user_uuid
        else None,
        description="Connected IT-user.\n",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
    )

    ituser: list[LazyITUser] = strawberry.field(
        resolver=to_list(
            seed_resolver(
                it_user_resolver, {"uuids": lambda root: uuid2list(root.it_user_uuid)}
            )
        ),
        description="Connected IT-user.\n",
        permission_classes=[IsAuthenticatedPermission, gen_read_permission("ituser")],
        deprecation_reason="Use 'ituser_response' instead. Will be removed in a future version of OS2mo.",
    )

    @strawberry.field(
        description=dedent(
            """
        Human readable name of the address.

        Name is *usually* equal to `value`, but may differ if `value` is not human readable.
        This may for instance be the case for `DAR` addresses, where the value is the DAR UUID, while the name is a human readable address.

        This is the value that should be shown to users in UIs.

        Examples:
        * "Vifdam 20, 1. th, 6000 Kolding"
        * "25052943"
        * "info@magenta.dk"
        * "Building 11"

        Note:
        Requesting this field may incur a performance penalty as the returned value may be dynamically resolved from the `value`-field.
        """
        )
    )
    async def name(self, root: AddressRead, info: Info) -> str | None:
        obj = await _get_handler_object(root, info)

        # TODO: Use AddressHandler implementation?
        if obj.scope == "DAR":
            dar_loader = context["dar_loader"]
            address_object = await dar_loader.load(UUID(root.value))
            return dar.name_from_dar_object(address_object)

        return obj.name

    @strawberry.field
    async def resolve(self, root: AddressRead, info: Info) -> ResolvedAddress:
        obj = await _get_handler_object(root, info)

        if obj.scope == "MULTIFIELD_TEXT":  # pragma: no cover
            return MultifieldAddress(value=root.value, value2=root.value2)  # type: ignore

        if obj.scope == "DAR":
            return DARAddress(value=root.value)  # type: ignore

        return DefaultAddress(value=root.value)  # type: ignore

    @strawberry.field(
        description=dedent(
            """
        Hypertext Reference of the address.

        The `href` field makes a hyperlink from the address value, such that the link can be included in user interfaces.

        Examples:
        * `null`: For non-hyperlinkable addresses.
        * "tel:88888888": For phone numbers.
        * "mailto:info@magenta.dk": For email addresses.
        * "https://www.openstreetmap.org/?mlon=11&mlat=56": For postal addresses, locations, etc

        Note:
        Requesting this field may incur a performance penalty as the returned value may be dynamically resolved from the `value`-field.

        """
        )
    )
    async def href(self, root: AddressRead, info: Info) -> str | None:
        obj = await _get_handler_object(root, info)

        # TODO: Use AddressHandler implementation?
        if obj.scope == "DAR":
            dar_loader = context["dar_loader"]
            address_object = await dar_loader.load(UUID(root.value))
            if address_object is None:
                return None
            return dar.open_street_map_href_from_dar_object(address_object)

        return obj.href

    @strawberry.field(description="UUID of the entity")
    async def uuid(self, root: AddressRead) -> UUID:
        return root.uuid

    @strawberry.field(
        description=dedent(
            """
            Short unique key.

            Usually set to the `value` provided on object creation.
            May also be set to the key used in external systems.

            Examples:
            * "25052943"
            * "info@magenta.dk"
            * "Building 11"
            """
        )
    )
    async def user_key(self, root: AddressRead) -> str:
        return root.user_key

    @strawberry.field(
        description=dedent(
            """
            The object type.

            Always contains the string `address`.
            """
        ),
        deprecation_reason=dedent(
            """
            Unintentionally exposed implementation detail.
            Provides no value whatsoever.
            """
        ),
    )
    async def type(self, root: AddressRead) -> str:
        """Implemented for backwards compatability."""
        return root.type_

    @strawberry.field(
        description="UUID of the address type class.",
        deprecation_reason=gen_uuid_field_deprecation("address_type"),
    )
    async def address_type_uuid(self, root: AddressRead) -> UUID:
        return root.address_type_uuid

    @strawberry.field(
        description="UUID of the employee related to the address.",
        deprecation_reason=gen_uuid_field_deprecation("employee"),
    )
    async def employee_uuid(self, root: AddressRead) -> UUID | None:
        return root.employee_uuid

    @strawberry.field(
        description="UUID of the organisation unit related to the address.",
        deprecation_reason=gen_uuid_field_deprecation("org_unit"),
    )
    async def org_unit_uuid(self, root: AddressRead) -> UUID | None:
        return root.org_unit_uuid

    @strawberry.field(
        description="Optional UUID of an associated engagement.",
        deprecation_reason=gen_uuid_field_deprecation("engagement"),
    )
    async def engagement_uuid(self, root: AddressRead) -> UUID | None:
        return root.engagement_uuid

    @strawberry.field(
        description="UUID of the it-user related to the address.",
        deprecation_reason=gen_uuid_field_deprecation("ituser"),
    )
    async def ituser_uuid(self, root: AddressRead) -> UUID | None:
        return root.it_user_uuid

    @strawberry.field(
        description="UUID of the visibility class of the address.",
        deprecation_reason=gen_uuid_field_deprecation("visibility"),
    )
    async def visibility_uuid(self, root: AddressRead) -> UUID | None:
        return root.visibility_uuid

    @strawberry.field(
        description=dedent(
            """
            Machine processable value of the address.

            The value of the address, which may or may not be fit for human consumption.
            If an address for human consumption is required, consider using `name` or `href` instead.

            Examples:
            * "3cb0a0c6-37d0-0e4a-e044-0003ba298018"
            * "25052943"
            * "info@magenta.dk"
            * "Building 11"
            """
        )
    )
    async def value(self, root: AddressRead, info: Info) -> str:
        obj = await _get_handler_object(root, info)
        return obj.value

    @strawberry.field(
        description=dedent(
            """
            Optional second machine processable value of the address.

            This value is `null` for most address types, but may be utilized by some address-types for extra information.

            Examples:
            * `null`
            * "Office 12"
            * "+45"
            """
        )
    )
    async def value2(self, root: AddressRead, info: Info) -> str | None:
        obj = await _get_handler_object(root, info)
        return obj.value2

    validity: Validity = strawberry.auto
