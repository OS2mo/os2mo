# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import os
import re
from datetime import date
from datetime import datetime
from datetime import timedelta
from functools import lru_cache
from functools import partial
from re import Pattern

import hypothesis as ht
import pytest
from hypothesis import HealthCheck
from hypothesis import strategies as st
from pydantic import ValidationError
from ramodels.mo import Validity

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


unexpected_value_error = partial(
    pytest.raises, ValidationError, match="unexpected value;"
)


@st.composite
def tz_dt_strat(draw):
    dts = st.datetimes(
        min_value=datetime(1930, 1, 1),
        timezones=st.timezones(),
        allow_imaginary=False,
    )
    return draw(dts)


date_strat = partial(st.dates, min_value=date(1930, 1, 1))


@st.composite
def dt_minmax(draw):
    dt_shared = st.shared(date_strat(), key="dtminmax")
    return draw(dt_shared)


@st.composite
def from_date_strat(draw):
    max_date = draw(dt_minmax())
    dates = date_strat(max_value=max_date).map(lambda date: date.isoformat())
    return draw(dates)


@st.composite
def to_date_strat(draw):
    min_date = draw(dt_minmax()) + timedelta(days=1)
    dates = st.dates(min_value=min_date).map(lambda date: date.isoformat())
    return draw(dates)


@st.composite
def not_from_regex(draw, str_pat: str):
    @lru_cache
    def cached_regex(str_pat: str) -> Pattern:
        return re.compile(str_pat)

    regex = cached_regex(str_pat)
    not_match = st.text().filter(lambda s: regex.match(s) is None)
    return draw(not_match)


@st.composite
def validity_strat(draw):
    required = {"from_date": from_date_strat()}
    optional = {"to_date": st.none() | to_date_strat()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def validity_model_strat(draw) -> Validity:
    st_dict = draw(validity_strat())
    return Validity(**st_dict)


st.register_type_strategy(Validity, validity_model_strat())
