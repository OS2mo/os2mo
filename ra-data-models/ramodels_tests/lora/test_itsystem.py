# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.lora import ITSystem

from ramodels_tests.conftest import from_date_strat
from ramodels_tests.conftest import to_date_strat

from .test__shared import valid_itsys_attr
from .test__shared import valid_itsys_relations
from .test__shared import valid_itsys_states


@st.composite
def itsystem_strat(draw):
    required = {
        "attributes": valid_itsys_attr(),
        "states": valid_itsys_states(),
    }
    optional = {
        "note": st.none() | st.text(),
        "relations": st.none() | valid_itsys_relations(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def itsystem_fsf_strat(draw):
    required = {
        "user_key": st.text(),
        "state": st.text(),
    }
    optional = {
        "uuid": st.uuids(),
        "name": st.none() | st.text(),
        "note": st.none() | st.text(),
        "type": st.none() | st.text(),
        "configuration_ref": st.none() | st.lists(st.text(), min_size=1),
        "belongs_to": st.none() | st.uuids(),
        "affiliated_orgs": st.none() | st.lists(st.uuids(), min_size=1),
        "affiliated_units": st.none() | st.lists(st.uuids(), min_size=1),
        "affiliated_functions": st.none() | st.lists(st.uuids(), min_size=1),
        "affiliated_users": st.none() | st.lists(st.uuids(), min_size=1),
        "affiliated_interests": st.none() | st.lists(st.uuids(), min_size=1),
        "affiliated_itsystems": st.none() | st.lists(st.uuids(), min_size=1),
        "affiliated_persons": st.none() | st.lists(st.uuids(), min_size=1),
        "addresses": st.none() | st.lists(st.uuids(), min_size=1),
        "system_types": st.none() | st.lists(st.uuids(), min_size=1),
        "tasks": st.none() | st.lists(st.uuids(), min_size=1),
        "from_date": from_date_strat(),
        "to_date": to_date_strat(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestITSystem:
    @given(itsystem_strat())
    def test_init(self, model_dict):
        assert ITSystem(**model_dict)

    @given(itsystem_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert ITSystem.from_simplified_fields(**simp_fields_dict)
