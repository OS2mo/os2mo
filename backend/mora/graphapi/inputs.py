#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import strawberry

from mora.graphapi.models import ITSystemWrite

# --------------------------------------------------------------------------------------
# Graphapi input models
# --------------------------------------------------------------------------------------


@strawberry.experimental.pydantic.input(model=ITSystemWrite)
class ITSystemInput:
    """Pydantic -> Strawberry model for class mutator."""

    uuid: strawberry.auto
    user_key: strawberry.auto
    state: strawberry.auto
    name: strawberry.auto
    system_type: strawberry.auto
