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

from ramodels.mo.organisation_unit import OrganisationUnit
from tests.conftest import unexpected_value_error
from tests.mo.test__shared import valid_org_unit_hier
from tests.mo.test__shared import valid_org_unit_level
from tests.mo.test__shared import valid_org_unit_type
from tests.mo.test__shared import valid_parent
from tests.mo.test__shared import valid_validity

# --------------------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------------------


@st.composite
def organisation_unit_strat(draw):
    required = {
        "user_key": st.text(),
        "validity": valid_validity(),
        "name": st.text(),
        "org_unit_type": valid_org_unit_type(),
        "org_unit_level": valid_org_unit_level(),
    }
    optional = {
        "type": st.just("org_unit"),
        "parent": valid_parent() | st.none(),
        "org_unit_hierarchy": valid_org_unit_hier() | st.none(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def organisation_unit_fsf_strat(draw):
    iso_dt = st.dates().map(lambda date: date.isoformat())
    required = {
        "uuid": st.uuids(),
        "user_key": st.text(),
        "name": st.text(),
        "org_unit_type_uuid": st.uuids(),
        "org_unit_level_uuid": st.uuids(),
    }
    optional = {
        "parent_uuid": st.uuids() | st.none(),
        "org_unit_hierarchy_uuid": st.uuids() | st.none(),
        "from_date": iso_dt,
        "to_date": iso_dt | st.none(),
    }

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(date.fromisoformat(from_date) <= date.fromisoformat(to_date))
    if from_date is None and to_date:
        assume(date.fromisoformat(to_date) >= date(1930, 1, 1))
    return st_dict


class TestOrganisationUnit:
    @given(organisation_unit_strat())
    def test_init(self, model_dict):
        # Required
        assert OrganisationUnit(**model_dict)

    @given(organisation_unit_strat(), st.text().filter(lambda s: s != "org_unit"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            OrganisationUnit(**model_dict)

    @given(organisation_unit_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert OrganisationUnit.from_simplified_fields(**simp_fields_dict)
