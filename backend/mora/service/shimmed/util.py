# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Iterable
from typing import Any


def filter_data(data: Iterable, key: str, value: Any) -> filter:
    return filter(lambda obj: obj[key] == value, data)
