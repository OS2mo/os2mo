# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from .models import OrganisationCreate
from .types import OrganisationType


async def create_organisation(input: OrganisationCreate) -> OrganisationType:
    # 00000000-0000-0000-0000-000000000000
    return OrganisationType(uuid="00000000-0000-0000-0000-000000000000")
