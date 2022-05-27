# SPDX-FileCopyrightText: 2018-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastapi import Body

from mora.service.configuration import router as config_router


@config_router.post("/ou/{unitid}/configuration", status_code=410)
def set_org_unit_configuration(unitid: UUID, configuration: dict = Body(...)) -> bool:
    """Removed configuration setting endpoint."""
    return False


@config_router.post("/configuration", status_code=410)
def set_global_configuration(configuration: dict = Body(...)) -> bool:
    """Removed global configuration setting endpoint."""
    return False
