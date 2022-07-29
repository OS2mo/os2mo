# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from mora.graphapi.models import Employee as EmployeeModel
from mora.util import CPR

# https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
CPRType = strawberry.scalar(
    CPR,
    serialize=str,
    parse_value=CPR.validate,
)


@strawberry.experimental.pydantic.type(
    model=EmployeeModel,
    all_fields=True,
    description="GraphQL type for/of an employee",
)
class Employee:
    pass
