# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# type: ignore
from datetime import datetime
from typing import Any
from uuid import UUID

import strawberry
from fastapi.encoders import jsonable_encoder
from pydantic.v1 import ConstrainedStr
from pydantic.v1 import Field
from pydantic.v1 import parse_obj_as
from pydantic.v1 import root_validator
from strawberry.types import Info

from ..latest.models import EmployeeUpsert
from ..latest.permissions import gen_create_permission
from ..latest.permissions import gen_update_permission
from ..latest.permissions import IsAuthenticatedPermission
from ..v13.mutators import uuid2response
from ..v13.schema import Employee
from ..v13.schema import Response
from ..v13.version import GraphQLVersion as NextGraphQLVersion
from mora import exceptions
from mora.graphapi.gmodels.mo import EmployeeRead
from mora.graphapi.gmodels.mo import OpenValidity
from mora.graphapi.gmodels.mo import Validity as RAValidity
from mora.graphapi.shim import execute_graphql  # type: ignore
from mora.graphapi.versions.latest.inputs import all_fields
from mora.util import CPR


class NonEmptyString(ConstrainedStr):
    min_length: int = 1


class EmployeeUpsertV12(EmployeeUpsert):
    _ERR_INVALID_NICKNAME = "'nickname' is only allowed to be set, if 'nickname_given_name' & 'nickname_surname' are None."
    _ERR_INVALID_CPR_NUMBER = (
        "'cpr_number' is only allowed to be set, if 'cpr_no' is None."
    )

    name: str | None = Field(None, description="Combined name of the employee")

    nickname: str | None = Field(
        None,
        description="Nickname (combined) of the employee.",
    )

    @root_validator
    def combined_or_split_nickname(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("nickname") and (
            values.get("nickname_given_name") or values.get("nickname_surname")
        ):
            raise ValueError(cls._ERR_INVALID_NICKNAME)

        return values

    cpr_no: CPR | None = Field(None, description="New danish CPR No. of the employee.")

    @root_validator
    def cpr_validator(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("cpr_no") and values.get("cpr_number"):
            raise ValueError(cls._ERR_INVALID_CPR_NUMBER)

        return values


class EmployeeCreateV12(EmployeeUpsertV12):
    _ERR_INVALID_GIVEN_NAME = (
        "'given_name' is only allowed to be set, if 'given_name' is None."
    )
    _ERR_INVALID_NAME = (
        "'name' is only allowed to be set, if 'given_name' & 'surname' are None."
    )

    given_name: NonEmptyString | None = Field(
        None, description="Givenname (firstname) of the employee."
    )
    givenname: NonEmptyString | None = Field(
        description="Givenname (firstname) of the employee."
    )
    surname: NonEmptyString | None = Field(
        None, description="Surname (lastname) of the employee."
    )

    @root_validator
    def only_one_givenname(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("given_name") and values.get("givenname"):
            raise ValueError(cls._ERR_INVALID_GIVEN_NAME)

        return values

    @root_validator
    def combined_or_split_name(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("name") and (
            values.get("given_name") or values.get("givenname") or values.get("surname")
        ):
            raise ValueError(cls._ERR_INVALID_NAME)

        return values


class EmployeeUpdateV12(EmployeeUpsertV12, OpenValidity):
    # Error messages returned by the @root_validator
    _ERR_INVALID_NAME = (
        "EmployeeUpdate.name is only allowed to be set, if "
        '"given_name" & "surname" are None.'
    )
    _ERR_INVALID_GIVEN_NAME = (
        "'given_name' is only allowed to be set, if 'given_name' is None."
    )

    uuid: UUID = Field(description="UUID of the employee to be updated.")

    given_name: str | None = Field(
        None,
        description="New first-name value of the employee nickname.",
    )
    givenname: str | None = Field(description="Givenname (firstname) of the employee.")
    surname: str | None = Field(
        None,
        description="New last-name value of the employee nickname.",
    )

    validity: RAValidity | None = Field(description="Validity range for the change.")

    @root_validator
    def only_one_givenname(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("given_name") and values.get("givenname"):
            raise ValueError(cls._ERR_INVALID_GIVEN_NAME)

        return values

    @root_validator
    def combined_or_split_name(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("name") and (
            values.get("given_name") or values.get("givenname") or values.get("surname")
        ):
            raise ValueError(cls._ERR_INVALID_NAME)

        return values

    @root_validator
    def validity_check(cls, values: dict[str, Any]) -> dict[str, Any]:
        validity = values.get("validity")
        dates = values.get("from_date") or values.get("to_date")
        if validity and dates:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Can only set one of 'validity' and 'from_date' / 'to_date'"
            )
        if validity is None and dates is None:
            exceptions.ErrorCodes.E_INVALID_INPUT(
                "Must set one of 'validity' and 'from_date' / 'to_date'"
            )
        return values


@strawberry.experimental.pydantic.input(
    model=EmployeeCreateV12,
    fields=list(
        all_fields(EmployeeCreateV12) - {"name", "nickname", "cpr_no", "givenname"}
    ),
)
class EmployeeCreateInput:
    """Input model for creating an employee."""

    name: str | None = strawberry.field(
        deprecation_reason="Use 'given_name' and 'surname' instead. Will be removed in a future version of OS2mo."
    )
    nickname: str | None = strawberry.field(
        deprecation_reason="Use 'nickname_given_name' and 'nickname_surname' instead. Will be removed in a future version of OS2mo."
    )
    cpr_no: CPR | None = strawberry.field(
        deprecation_reason="Use 'cpr_number' instead. Will be removed in a future version of OS2mo."
    )
    givenname: str | None = strawberry.field(
        deprecation_reason="Use 'given_name' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.experimental.pydantic.input(
    model=EmployeeUpdateV12,
    fields=list(
        all_fields(EmployeeUpdateV12)
        - {"name", "nickname", "cpr_no", "givenname", "from_date", "to_date"}
    ),
)
class EmployeeUpdateInput:
    """Input model for updating an employee."""

    name: str | None = strawberry.field(
        deprecation_reason="Use 'given_name' and 'surname' instead. Will be removed in a future version of OS2mo."
    )
    nickname: str | None = strawberry.field(
        deprecation_reason="Use 'nickname_given_name' and 'nickname_surname' instead. Will be removed in a future version of OS2mo."
    )
    cpr_no: CPR | None = strawberry.field(
        deprecation_reason="Use 'cpr_number' instead. Will be removed in a future version of OS2mo."
    )
    givenname: str | None = strawberry.field(
        deprecation_reason="Use 'given_name' instead. Will be removed in a future version of OS2mo."
    )

    from_date: datetime | None = strawberry.field(
        deprecation_reason="Use 'validity.from_date' instead. Will be removed in a future version of OS2mo."
    )
    to_date: datetime | None = strawberry.field(
        deprecation_reason="Use 'validity.to_date' instead. Will be removed in a future version of OS2mo."
    )


@strawberry.type
class Mutation(NextGraphQLVersion.schema.mutation):  # type: ignore[name-defined]
    @strawberry.mutation(
        description="Creates an employee.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_create_permission("employee"),
        ],
    )
    async def employee_create(
        self, info: Info, input: EmployeeCreateInput
    ) -> Response[Employee]:
        input.to_pydantic()  # type: ignore

        if input.givenname:
            input.given_name = input.givenname
            input.givenname = None

        if input.name:
            input.given_name, input.surname = input.name.rsplit(" ", 1)
            input.name = None

        if input.nickname:
            input.nickname_given_name, input.nickname_surname = input.nickname.rsplit(
                " ", 1
            )
            input.nickname = None

        if input.cpr_no:
            input.cpr_number = input.cpr_no
            input.cpr_no = None

        input_dict = jsonable_encoder(input.to_pydantic().dict(by_alias=True))  # type: ignore
        input_dict = {k: v for k, v in input_dict.items() if v}
        response = await execute_graphql(
            """
            mutation EmployeeCreate($input: EmployeeCreateInput!){
                employee_create(input: $input) {
                    uuid
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"input": input_dict},
        )
        if response.errors:
            for error in response.errors:
                raise ValueError(error.message)
        uuid = response.data["employee_create"]["uuid"]
        return uuid2response(uuid, EmployeeRead)

    @strawberry.mutation(
        description="Updates an employee.",
        permission_classes=[
            IsAuthenticatedPermission,
            gen_update_permission("employee"),
        ],
    )
    async def employee_update(
        self, info: Info, input: EmployeeUpdateInput
    ) -> Response[Employee]:
        input.to_pydantic()  # type: ignore

        if input.givenname:
            input.given_name = input.givenname
            input.givenname = None

        if input.name:
            input.given_name, input.surname = input.name.rsplit(" ", 1)
            input.name = None

        if input.nickname:
            input.nickname_given_name, input.nickname_surname = input.nickname.rsplit(
                " ", 1
            )
            input.nickname = None

        if input.cpr_no:
            input.cpr_number = input.cpr_no
            input.cpr_no = None

        if input.from_date or input.to_date:
            input.validity = parse_obj_as(
                RAValidity, {"from": input.from_date, "to": input.to_date}
            )
            input.from_date = None
            input.to_date = None

        input_dict = jsonable_encoder(input.to_pydantic().dict(by_alias=True))  # type: ignore
        input_dict = {k: v for k, v in input_dict.items() if v}
        response = await execute_graphql(
            """
            mutation EmployeeUpdate($input: EmployeeUpdateInput!){
                employee_update(input: $input) {
                    uuid
                }
            }
            """,
            graphql_version=NextGraphQLVersion,
            context_value=info.context,
            variable_values={"input": input_dict},
        )
        if response.errors:
            for error in response.errors:
                raise ValueError(error.message)
        uuid = response.data["employee_update"]["uuid"]
        return uuid2response(uuid, EmployeeRead)


class GraphQLSchema(NextGraphQLVersion.schema):  # type: ignore
    """Version 12 of the GraphQL Schema.

    Version 13 introduced a breaking change to the `employee_create` and
    `employee_update` mutators.
    Version 12 ensures that the old functionality is still available.
    """

    mutation = Mutation


class GraphQLVersion(NextGraphQLVersion):
    """GraphQL Version 12."""

    version = 12
    schema = GraphQLSchema
