# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry lazy types for breaking cyclic dependencies."""

from typing import TYPE_CHECKING
from typing import Annotated

import strawberry

if TYPE_CHECKING:
    from .schema import KLE
    from .schema import Address
    from .schema import Association
    from .schema import Class
    from .schema import Employee
    from .schema import Engagement
    from .schema import Facet
    from .schema import ITSystem
    from .schema import ITUser
    from .schema import Leave
    from .schema import Manager
    from .schema import OrganisationUnit
    from .schema import Owner
    from .schema import RelatedUnit
    from .schema import RoleBinding


LazySchema = strawberry.lazy(".schema")

LazyAddress = Annotated["Address", LazySchema]
LazyAssociation = Annotated["Association", LazySchema]
LazyClass = Annotated["Class", LazySchema]
LazyEmployee = Annotated["Employee", LazySchema]
LazyEngagement = Annotated["Engagement", LazySchema]
LazyFacet = Annotated["Facet", LazySchema]
LazyITSystem = Annotated["ITSystem", LazySchema]
LazyITUser = Annotated["ITUser", LazySchema]
LazyKLE = Annotated["KLE", LazySchema]
LazyLeave = Annotated["Leave", LazySchema]
LazyManager = Annotated["Manager", LazySchema]
LazyOwner = Annotated["Owner", LazySchema]
LazyOrganisationUnit = Annotated["OrganisationUnit", LazySchema]
LazyRelatedUnit = Annotated["RelatedUnit", LazySchema]
LazyRoleBinding = Annotated["RoleBinding", LazySchema]
