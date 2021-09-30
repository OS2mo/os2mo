# SPDX-FileCopyrightText: 2017-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from httpx import AsyncClient

from mora import config


client = AsyncClient(timeout=config.get_settings().httpx_timeout)
