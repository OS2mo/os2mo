#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import assume
from hypothesis import strategies as st

# --------------------------------------------------------------------------------------
# Shared fixtures and strategies
# --------------------------------------------------------------------------------------


@st.composite
def valid_dt_range(draw):
    from_dt = draw(st.dates())
    to_dt = draw(st.dates())
    assume(from_dt <= to_dt)
    return from_dt.isoformat(), to_dt.isoformat()
