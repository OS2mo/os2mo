#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import os
from datetime import timedelta
from functools import partial

import hypothesis as ht
import pytest
from pydantic import ValidationError

# --------------------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------------------
ht.settings.register_profile("ci", max_examples=100, deadline=None)
ht.settings.register_profile("dev", max_examples=10, deadline=timedelta(seconds=2))
ht.settings.register_profile(
    "debug",
    max_examples=10,
    deadline=timedelta(seconds=2),
    verbosity=ht.Verbosity.verbose,
)
ht.settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))

# --------------------------------------------------------------------------------------
# Shared fixtures and strategies
# --------------------------------------------------------------------------------------


unexpected_value_error = partial(
    pytest.raises, ValidationError, match="unexpected value;"
)
