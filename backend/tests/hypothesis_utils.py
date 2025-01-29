# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import date
from datetime import timedelta
from functools import partial

from hypothesis import strategies as st
from ramodels.mo import Validity

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
def validity_strat(draw):
    required = {"from_date": from_date_strat()}
    optional = {"to_date": st.none() | to_date_strat()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def validity_model_strat(draw) -> Validity:
    st_dict = draw(validity_strat())
    return Validity(**st_dict)
