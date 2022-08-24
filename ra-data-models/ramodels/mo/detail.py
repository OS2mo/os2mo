#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from typing import Literal

from pydantic import Field
from ramodels.mo._shared import TerminateValidity
from ramodels.mo._shared import UUIDBase


class Detail(UUIDBase):
    type: Literal[
        "address", "association", "engagement", "org_unit", "manager"
    ] = Field(
        description="Name of the type of detail we wish to terminate. "
        "Must be a valid lora role_type like:  'address', "
        "'association' etc."
    )


class DetailTermination(Detail):

    validity: TerminateValidity = Field(
        description="MO unit validity, determining in what date-interval "
        "a unit is available."
    )

    def to_dict(self) -> dict:
        request_dict = self.dict(by_alias=True)
        request_dict["uuid"] = str(self.uuid)
        if self.validity.from_date:
            request_dict["validity"][
                "from"
            ] = self.validity.from_date.date().isoformat()
        else:
            del request_dict["validity"]["from"]

        if self.validity.to_date:
            request_dict["validity"]["to"] = self.validity.to_date.date().isoformat()

        return request_dict
