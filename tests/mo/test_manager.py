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

from ramodels.mo import Manager
from ramodels.mo._shared import ManagerLevel
from ramodels.mo._shared import ManagerType
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Responsibility
from ramodels.mo._shared import Validity
from tests.conftest import unexpected_value_error

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def manager_strat(draw):
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
        "responsibility": st.lists(st.builds(Responsibility)),
        "manager_level": st.builds(ManagerLevel),
        "manager_type": st.builds(ManagerType),
        "validity": st.builds(Validity),
    }
    optional = {"type": st.just("manager")}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def manager_fsf_strat(draw):
    iso_dt = st.dates().map(lambda date: date.isoformat())
    required = {
        "uuid": st.uuids(),
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
        "responsibility_uuid": st.uuids(),
        "manager_level_uuid": st.uuids(),
        "manager_type_uuid": st.uuids(),
    }

    optional = {"from_date": iso_dt, "to_date": iso_dt | st.none()}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(date.fromisoformat(from_date) <= date.fromisoformat(to_date))
    if from_date is None and to_date:
        assume(date.fromisoformat(to_date) >= date(1930, 1, 1))

    return st_dict


class TestManager:
    @given(manager_strat())
    def test_init(self, model_dict):
        assert Manager(**model_dict)

    @given(
        manager_strat(),
        st.text().filter(lambda s: s != "manager"),
    )
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Manager(**model_dict)

    @given(manager_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        # Required
        assert Manager.from_simplified_fields(**simp_fields_dict)
