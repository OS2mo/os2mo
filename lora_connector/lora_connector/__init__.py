# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

__version__ = "0.1.0"


from .lora import Connector, LoraObjectType, Scope, get_version, set_lora_url


async def get_lora_version() -> str:
    return await get_version()
