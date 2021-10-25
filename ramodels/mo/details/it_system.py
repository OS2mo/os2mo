#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Literal
from typing import Optional

from pydantic import Field

from .._shared import ITSystemRef
from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import Validity

# --------------------------------------------------------------------------------------
# IT Systems
# --------------------------------------------------------------------------------------


class ITSystemBinding(MOBase):
    type_: Literal["it"] = Field("it", alias="type", description="The object type.")
    user_key: str = Field(description="The IT system account name.")
    itsystem: ITSystemRef = Field(
        description="The IT system for which to create this binding."
    )
    person: Optional[PersonRef] = Field(
        description="Reference to the person object for which the binding should "
        "be created."
    )
    org_unit: Optional[OrgUnitRef] = Field(
        description="Reference to the organisation unit for which the binding should "
        "be created."
    )
    validity: Validity = Field(
        description="Validity of the created IT system binding object."
    )
