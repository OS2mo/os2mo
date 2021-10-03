# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from mora.graphapi.main import get_schema
from mora.graphapi.dataloaders import get_loaders


async def execute_graphql(*args, **kwargs):
    return await get_schema().execute(*args, **kwargs, context_value=get_loaders())
