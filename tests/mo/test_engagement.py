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

from ramodels.mo.engagement import Engagement
from ramodels.mo.engagement import EngagementAssociation
from tests.conftest import unexpected_value_error
from tests.mo.test__shared import valid_eng_assoc_type
from tests.mo.test__shared import valid_eng_ref
from tests.mo.test__shared import valid_eng_type
from tests.mo.test__shared import valid_job_fun
from tests.mo.test__shared import valid_org_unit_ref
from tests.mo.test__shared import valid_pers
from tests.mo.test__shared import valid_primary
from tests.mo.test__shared import valid_validity

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def engagement_strat(draw):
    required = {
        "org_unit": valid_org_unit_ref(),
        "person": valid_pers(),
        "job_function": valid_job_fun(),
        "engagement_type": valid_eng_type(),
        "validity": valid_validity(),
        "primary": valid_primary(),
        "user_key": st.text(),
    }
    optional = {
        "type": st.just("engagement"),
        "extension_1": st.text() | st.none(),
        "extension_2": st.text() | st.none(),
        "extension_3": st.text() | st.none(),
        "extension_4": st.text() | st.none(),
        "extension_5": st.text() | st.none(),
        "extension_6": st.text() | st.none(),
        "extension_7": st.text() | st.none(),
        "extension_8": st.text() | st.none(),
        "extension_9": st.text() | st.none(),
        "extension_10": st.text() | st.none(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def engagement_fsf_strat(draw):
    iso_dt = st.dates().map(lambda date: date.isoformat())
    required = {
        "uuid": st.uuids(),
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
        "job_function_uuid": st.uuids(),
        "engagement_type_uuid": st.uuids(),
        "primary_uuid": st.uuids(),
        "user_key": st.text(),
    }
    optional = {
        "from_date": iso_dt,
        "to_date": iso_dt | st.none(),
        "extension_1": st.text() | st.none(),
        "extension_2": st.text() | st.none(),
        "extension_3": st.text() | st.none(),
        "extension_4": st.text() | st.none(),
        "extension_5": st.text() | st.none(),
        "extension_6": st.text() | st.none(),
        "extension_7": st.text() | st.none(),
        "extension_8": st.text() | st.none(),
        "extension_9": st.text() | st.none(),
        "extension_10": st.text() | st.none(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(date.fromisoformat(from_date) <= date.fromisoformat(to_date))
    if from_date is None and to_date:
        assume(date.fromisoformat(to_date) >= date(1930, 1, 1))
    return st_dict


class TestEngagement:
    @given(engagement_strat())
    def test_init(self, model_dict):
        assert Engagement(**model_dict)

    @given(engagement_strat(), st.text().filter(lambda s: s != "engagement"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            Engagement(**model_dict)

    @given(engagement_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert Engagement.from_simplified_fields(**simp_fields_dict)


@st.composite
def engagement_assoc_strat(draw):
    required = {
        "org_unit": valid_org_unit_ref(),
        "engagement": valid_eng_ref(),
        "engagement_association_type": valid_eng_assoc_type(),
        "validity": valid_validity(),
    }
    optional = {"type": st.just("engagement_association")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


@st.composite
def engagement_assoc_fsf_strat(draw):
    iso_dt = st.dates().map(lambda date: date.isoformat())
    required = {
        "uuid": st.uuids(),
        "org_unit_uuid": st.uuids(),
        "engagement_uuid": st.uuids(),
        "engagement_association_type_uuid": st.uuids(),
    }
    optional = {"from_date": iso_dt, "to_date": iso_dt | st.none()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    from_date, to_date = st_dict.get("from_date"), st_dict.get("to_date")
    if all([from_date, to_date]):
        assume(date.fromisoformat(from_date) <= date.fromisoformat(to_date))
    if from_date is None and to_date:
        assume(date.fromisoformat(to_date) >= date(1930, 1, 1))
    return st_dict


class TestEngagementAssociation:
    @given(engagement_assoc_strat())
    def test_init(self, model_dict):
        assert EngagementAssociation(**model_dict)

    @given(
        engagement_assoc_strat(),
        st.text().filter(lambda s: s != "engagement_association"),
    )
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            EngagementAssociation(**model_dict)

    @given(engagement_assoc_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert EngagementAssociation.from_simplified_fields(**simp_fields_dict)
