#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import os
from datetime import date
from datetime import datetime
from datetime import timedelta
from functools import partial

import hypothesis as ht
import pytest
from dateutil.tz import gettz
from dateutil.tz import UTC
from hypothesis import HealthCheck
from hypothesis import strategies as st
from hypothesis.extra import dateutil as ht_dateutil
from pydantic import ValidationError


# --------------------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------------------
ht.settings.register_profile(
    "ci", deadline=None, suppress_health_check=[HealthCheck.too_slow]
)
ht.settings.register_profile(
    "dev",
    max_examples=50,
    deadline=timedelta(seconds=2),
    suppress_health_check=[HealthCheck.too_slow],
)
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


@st.composite
def tz_dt_strat(draw):
    dts = st.datetimes(
        min_value=datetime(1930, 1, 1),
        timezones=ht_dateutil.timezones().filter(
            lambda tz: tz is UTC or tz is gettz("Europe/Copenhagen")
        ),  # this is not great and I'm sorry
        allow_imaginary=False,
    )
    return draw(dts)


@st.composite
def date_strat(draw):
    dates = st.dates(min_value=date(1930, 1, 1))
    return draw(dates)


@st.composite
def dt_minmax(draw):
    dt_shared = st.shared(st.dates(min_value=date(1930, 1, 1)), key="dtminmax")
    return draw(dt_shared)


@st.composite
def from_date_strat(draw):
    max_date = draw(dt_minmax())
    dates = st.dates(min_value=date(1930, 1, 1), max_value=max_date).map(
        lambda date: date.isoformat()
    )
    return draw(dates)


@st.composite
def to_date_strat(draw):
    min_date = draw(dt_minmax()) + timedelta(days=1)
    dates = st.dates(min_value=min_date).map(lambda date: date.isoformat())
    return draw(dates)
