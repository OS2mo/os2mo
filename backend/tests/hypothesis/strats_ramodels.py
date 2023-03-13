# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import strategies as st

from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import FacetRef
from ramodels.lora._shared import OwnerRef
from ramodels.lora._shared import Responsible
from ramodels.lora.klasse import KlasseProperties
from ramodels.lora.klasse import KlasseRelations

# NOTE: Below hypothesis strategies are copies of existing ones in
# "ra-data-models/ramodels_tests/lora/test__shared.py". They are not accessible from backend/tests,
# which is why they have been duplicated.


@st.composite
def valid_effective_time(draw):
    dt_range = st.tuples(st.datetimes(), st.datetimes()).filter(
        lambda dts: dts[0] < dts[1]
    )
    from_dt, to_dt = draw(dt_range)
    return EffectiveTime(from_date=from_dt, to_date=to_dt)


@st.composite
def klasse_prop_strat(draw):
    required = {
        "user_key": st.text(),
        "title": st.text(),
        "effective_time": valid_effective_time(),
    }
    optional = {
        "scope": st.none() | st.text(),
        "example": st.none() | st.text(),
        "description": st.none() | st.text(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def valid_klsprop(draw):
    model_dict = draw(klasse_prop_strat())
    return KlasseProperties(**model_dict)


@st.composite
def responsible_strat(draw):
    required = {"uuid": st.uuids(), "effective_time": valid_effective_time()}
    optional = {"object_type": st.just("organisation")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def valid_resp(draw):
    model_dict = draw(responsible_strat())
    return Responsible(**model_dict)


@st.composite
def facet_ref_strat(draw):
    required = {"uuid": st.uuids(), "effective_time": valid_effective_time()}
    optional = {"object_type": st.just("facet")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def valid_fref(draw):
    model_dict = draw(facet_ref_strat())
    return FacetRef(**model_dict)


@st.composite
def owner_ref_strat(draw):
    required = {"uuid": st.uuids(), "effective_time": valid_effective_time()}
    optional = {"object_type": st.just("organisationenhed")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def valid_oref(draw):
    model_dict = draw(owner_ref_strat())
    return OwnerRef(**model_dict)


@st.composite
def klasse_relations_strat(draw):
    required = {
        "responsible": st.lists(valid_resp(), min_size=1, max_size=1),
        "facet": st.lists(valid_fref(), min_size=1, max_size=1),
    }
    optional = {"owner": st.none() | st.lists(valid_oref(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def valid_klasse_relations(draw):
    model_dict = draw(klasse_relations_strat())
    return KlasseRelations(**model_dict)
