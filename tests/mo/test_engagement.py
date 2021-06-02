#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import given
from hypothesis import strategies as st

from ramodels.mo._shared import EngagementAssociationType
from ramodels.mo._shared import EngagementRef
from ramodels.mo._shared import EngagementType
from ramodels.mo._shared import JobFunction
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import PersonRef
from ramodels.mo._shared import Primary
from ramodels.mo._shared import Validity
from ramodels.mo.engagement import Engagement
from ramodels.mo.engagement import EngagementAssociation
from tests.conftest import from_date_strat
from tests.conftest import to_date_strat
from tests.conftest import unexpected_value_error

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def engagement_strat(draw):
    required = {
        "org_unit": st.builds(OrgUnitRef),
        "person": st.builds(PersonRef),
        "job_function": st.builds(JobFunction),
        "engagement_type": st.builds(EngagementType),
        "validity": st.builds(Validity),
        "primary": st.builds(Primary),
        "user_key": st.text(),
    }
    optional = {
        "type": st.just("engagement"),
        "extension_1": st.none() | st.text(),
        "extension_2": st.none() | st.text(),
        "extension_3": st.none() | st.text(),
        "extension_4": st.none() | st.text(),
        "extension_5": st.none() | st.text(),
        "extension_6": st.none() | st.text(),
        "extension_7": st.none() | st.text(),
        "extension_8": st.none() | st.text(),
        "extension_9": st.none() | st.text(),
        "extension_10": st.none() | st.text(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def engagement_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "org_unit_uuid": st.uuids(),
        "person_uuid": st.uuids(),
        "job_function_uuid": st.uuids(),
        "engagement_type_uuid": st.uuids(),
        "primary_uuid": st.uuids(),
        "user_key": st.text(),
        "from_date": from_date_strat(),
    }
    optional = {
        "to_date": st.none() | to_date_strat(),
        "extension_1": st.none() | st.text(),
        "extension_2": st.none() | st.text(),
        "extension_3": st.none() | st.text(),
        "extension_4": st.none() | st.text(),
        "extension_5": st.none() | st.text(),
        "extension_6": st.none() | st.text(),
        "extension_7": st.none() | st.text(),
        "extension_8": st.none() | st.text(),
        "extension_9": st.none() | st.text(),
        "extension_10": st.none() | st.text(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
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
        "org_unit": st.builds(OrgUnitRef),
        "engagement": st.builds(EngagementRef),
        "engagement_association_type": st.builds(EngagementAssociationType),
        "validity": st.builds(Validity),
    }
    optional = {"type": st.just("engagement_association")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


@st.composite
def engagement_assoc_fsf_strat(draw):
    required = {
        "uuid": st.uuids(),
        "org_unit_uuid": st.uuids(),
        "engagement_uuid": st.uuids(),
        "engagement_association_type_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }
    optional = {"to_date": st.none() | to_date_strat()}

    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
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
