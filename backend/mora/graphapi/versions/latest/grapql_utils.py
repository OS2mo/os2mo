# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re

from pydantic import ConstrainedStr


class CprNo(ConstrainedStr):
    regex = re.compile(r"^\d{10}$")
