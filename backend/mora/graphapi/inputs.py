#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import strawberry
from mora.graphapi.models import ClassTerminate


@strawberry.experimental.pydantic.input(
    model=ClassTerminate,
    all_fields=True,
    description="Input type for terminating classes",
)
class ClassTerminationInput:
    """Data representation of the input fields required to terminate a class."""

    pass

# @strawberry.experimental.pydantic.input(model=ClassRead)
# class ClassWriteStrawberry:
#     """Pydantic -> Strawberry model for class mutator."""

#     """TODO: input model bør muligvis ændres til ClassWrite.
#     Men da alle Fields i ClassWrite er Optional fungerer den ikke.
#     Derfor er der indtil videre brugt ClassRead.
#     ClassWrite bør måske ændres?
#     ClassRead/Write ligger i ra-data-models.
#     """

#     uuid: strawberry.auto
#     type_: strawberry.auto
#     facet_uuid: strawberry.auto
#     org_uuid: strawberry.auto
#     scope: strawberry.auto
#     published: strawberry.auto
#     parent_uuid: strawberry.auto
#     example: strawberry.auto
#     owner: strawberry.auto
#     name: strawberry.auto
#     user_key: strawberry.auto
