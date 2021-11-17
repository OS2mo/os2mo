#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import date

from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st

from ramodels.mo._shared import AssociationType
from ramodels.mo._shared import DynamicClasses
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Primary
from ramodels.mo._shared import Validity
from ramodels.mo.details import Association
from ramodels.mo.details import AssociationBase
from ramodels.mo.details import AssociationRead
from ramodels.mo.details import AssociationWrite
from tests.conftest import from_date_strat
from tests.conftest import not_from_regex
from tests.conftest import to_date_strat
from tests.conftest import unexpected_value_error

# ---------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
    }
    optional = {
        "type": st.just("association"),
        "user_key": st.none() | st.text(),
        "dynamic_classes": st.none() | st.lists(st.builds(DynamicClasses)),
    }
    st_dict = st.fixed_dictionaries(required, optional=optional)  # type: ignore
    return draw(st_dict)


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit": st.uuids(),
        "person": st.uuids(),
        "association_type": st.uuids(),
    }
    optional = {
        "primary": st.none() | st.uuids(),
        "substitute": st.none() | st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def write_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
        "association_type": st.builds(AssociationType),
    }
    optional = {
        "primary": st.none() | st.builds(Primary),
        "substitute": st.none() | st.builds(PersonRef),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return {**base_dict, **st_dict}


@st.composite
def association_strat(draw):
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
        "association_type": st.builds(AssociationType),
        "validity": st.builds(Validity),
    }
    optional = {"type": st.just("association")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def association_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
        "association_type_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }

    optional = {"to_date": st.none() | to_date_strat()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore

    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(date.fromisoformat(from_date) <= date.fromisoformat(to_date))
    if from_date is None and to_date:
        assume(date.fromisoformat(to_date) >= date(1930, 1, 1))

    return st_dict


class TestAssociation:
    @given(association_strat())
    def test_init(self, model_dict):
        assert Association(**model_dict)

    @given(association_strat(), not_from_regex(r"^association$"))
    def test_invalid_type(self, model_dict, invalid_type):
        model_dict["type"] = invalid_type
        with unexpected_value_error():
            Association(**model_dict)

    @given(association_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Association.from_simplified_fields(**simp_fields_dict)

    @given(base_strat())
    def test_base(self, model_dict):
        assert AssociationBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert AssociationRead(**model_dict)

    @given(write_strat())
    def test_write(self, model_dict):
        assert AssociationWrite(**model_dict)
