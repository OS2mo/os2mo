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

from .._shared import EngagementRef
from .._shared import LeaveType
from .._shared import MOBase
from .._shared import PersonRef
from .._shared import Validity

# --------------------------------------------------------------------------------------
# Role
# --------------------------------------------------------------------------------------


class Leave(MOBase):
    type_: Literal["leave"] = Field(
        "leave", alias="type", description="The object type."
    )
    user_key: Optional[str] = Field(description="Short, unique key.")
    leave_type: LeaveType = Field(description="Reference to the leave type facet")
    person: PersonRef = Field(
        description="Reference to the person object for which the role should "
        "be created."
    )
    engagement: Optional[EngagementRef] = Field(
        description="Reference to the engagement for which the role should "
        "be created."
    )
    validity: Validity = Field(description="Validity of the created role object.")
