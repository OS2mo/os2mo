# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from mora.graphapi.models import EngagementModel
from mora.graphapi.models import OrganisationUnit as OrganisationUnitModel
from mora.util import CPR

# https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
CPRType = strawberry.scalar(
    CPR,
    serialize=str,
    parse_value=CPR.validate,
)


@strawberry.experimental.pydantic.type(
    model=OrganisationUnitModel,
    all_fields=True,
    description="GraphQL type for/of a organization unit",
)
class OrganizationUnit:
    pass


@strawberry.experimental.pydantic.type(
    model=EngagementModel,
    all_fields=True,
    description="GraphQL type for an engagement",
)
class EngagementTerminateType:
    pass
