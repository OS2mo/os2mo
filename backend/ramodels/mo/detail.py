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

from ramodels.mo._shared import UUIDBase


class Detail(UUIDBase):
    type: Literal[
        "address", "association", "engagement", "org_unit", "manager", "it", "role"
    ] = Field(
        description="Name of the type of detail we wish to terminate. "
        "Must be a valid lora role_type like:  'address', "
        "'association' etc."
    )


class DetailTermination(Detail):

    validity: Optional[dict] = Field(
        description="MO unit validity, determining in what date-interval "
        "a unit is available."
    )

    def to_dict(self) -> dict:
        request_dict = self.dict(by_alias=True)
        request_dict["uuid"] = str(self.uuid)

        if request_dict["validity"] is None:
            del request_dict["validity"]

        return request_dict
