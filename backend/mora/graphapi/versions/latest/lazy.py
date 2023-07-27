# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Lazy strawberry types."""
from typing import Annotated

import strawberry

LazySchema = strawberry.lazy(".schema")

LazyAddress = Annotated["Address", LazySchema]
LazyAssociation = Annotated["Association", LazySchema]
LazyClass = Annotated["Class", LazySchema]
LazyEmployee = Annotated["Employee", LazySchema]
LazyEngagement = Annotated["Engagement", LazySchema]
LazyEngagementAssociation = Annotated["EngagementAssociation", LazySchema]
LazyFacet = Annotated["Facet", LazySchema]
LazyITSystem = Annotated["ITSystem", LazySchema]
LazyITUser = Annotated["ITUser", LazySchema]
LazyKLE = Annotated["KLE", LazySchema]
LazyLeave = Annotated["Leave", LazySchema]
LazyManager = Annotated["Manager", LazySchema]
LazyOwner = Annotated["Owner", LazySchema]
LazyOrganisationUnit = Annotated["OrganisationUnit", LazySchema]
LazyRelatedUnit = Annotated["RelatedUnit", LazySchema]
LazyRole = Annotated["Role", LazySchema]

LazyResponse = Annotated["Response", LazySchema]
