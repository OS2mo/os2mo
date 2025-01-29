# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Strawberry types describing the MO graph."""

import strawberry

from mora.graphapi.gmodels.mo._shared import OpenValidity as OpenValidityModel
from mora.graphapi.gmodels.mo._shared import Validity as ValidityModel


# Validities
# ----------
@strawberry.experimental.pydantic.type(
    model=ValidityModel,
    all_fields=True,
    description="Validity of objects with required from date",
)
class Validity:
    pass


@strawberry.experimental.pydantic.type(
    model=OpenValidityModel,
    all_fields=True,
    description="Validity of objects with optional from date",
)
class OpenValidity:
    pass
