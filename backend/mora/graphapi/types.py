# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import strawberry

from mora.graphapi.models import Employee as EmployeeModel
from mora.util import CPR

# OBS: If we don't rename this to "EmployeeModel", I get
# the following error from uvicorn:
#       Error loading ASGI app factory: Mutation fields cannot be resolved.
#       Unexpected type '<class 'mora.graphapi.models.Employee'>'
# OBS2: pre-commit hook `Reorder python imports` keeps moving this comment block.

# https://strawberry.rocks/docs/integrations/pydantic#classes-with-__get_validators__
CPRType = strawberry.scalar(
    CPR,
    serialize=str,
    parse_value=CPR.validate,
)


# OBS: I was unable to name the type "Employee" since I got the following error back
# from GraphQL: "Expected value of type 'Employee' but got: <Employee instance>."..
@strawberry.experimental.pydantic.type(
    model=EmployeeModel,
    all_fields=True,
)
class EmployeeType:
    """GraphQL type for/of an employee."""

    pass
