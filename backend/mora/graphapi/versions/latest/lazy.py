# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry lazy types for breaking cyclic dependencies."""

from typing import TYPE_CHECKING
from typing import Annotated

import strawberry

if TYPE_CHECKING:
    from .collections.address import Address
    from .collections.association import Association
    from .collections.classes import Class
    from .collections.employee import Employee
    from .collections.engagement import Engagement
    from .collections.facet import Facet
    from .collections.it import ITSystem
    from .collections.it import ITUser
    from .collections.kle import KLE
    from .collections.leave import Leave
    from .collections.manager import Manager
    from .collections.organisation_unit import OrganisationUnit
    from .collections.owner import Owner
    from .collections.related_unit import RelatedUnit
    from .collections.role_binding import RoleBinding


LazyAddress = Annotated["Address", strawberry.lazy(".collections.address")]
LazyAssociation = Annotated["Association", strawberry.lazy(".collections.association")]
LazyClass = Annotated["Class", strawberry.lazy(".collections.classes")]
LazyEmployee = Annotated["Employee", strawberry.lazy(".collections.employee")]
LazyEngagement = Annotated["Engagement", strawberry.lazy(".collections.engagement")]
LazyFacet = Annotated["Facet", strawberry.lazy(".collections.facet")]
LazyITSystem = Annotated["ITSystem", strawberry.lazy(".collections.it")]
LazyITUser = Annotated["ITUser", strawberry.lazy(".collections.it")]
LazyKLE = Annotated["KLE", strawberry.lazy(".collections.kle")]
LazyLeave = Annotated["Leave", strawberry.lazy(".collections.leave")]
LazyManager = Annotated["Manager", strawberry.lazy(".collections.manager")]
LazyOwner = Annotated["Owner", strawberry.lazy(".collections.owner")]
LazyOrganisationUnit = Annotated[
    "OrganisationUnit", strawberry.lazy(".collections.organisation_unit")
]
LazyRelatedUnit = Annotated["RelatedUnit", strawberry.lazy(".collections.related_unit")]
LazyRoleBinding = Annotated["RoleBinding", strawberry.lazy(".collections.role_binding")]
