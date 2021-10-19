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

from .._shared import MOBase
from .._shared import OrgUnitRef
from .._shared import PersonRef
from .._shared import RoleType
from .._shared import Validity

# --------------------------------------------------------------------------------------
# Role
# --------------------------------------------------------------------------------------


class Role(MOBase):
    type_: Literal["role"] = Field("role", alias="type", description="The object type.")
    user_key: Optional[str] = Field(description="Short, unique key.")
    role_type: RoleType = Field(description="Reference to the role type facet")
    person: PersonRef = Field(
        description="Reference to the person object for which the role should "
        "be created."
    )
    org_unit: OrgUnitRef = Field(
        description="Reference to the organisation unit for which the role should "
        "be created."
    )
    validity: Validity = Field(description="Validity of the created role object.")
