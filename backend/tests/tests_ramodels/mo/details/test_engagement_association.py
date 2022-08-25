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
from ramodels.mo._shared import OrgUnitRef
from ramodels.mo._shared import Validity
from ramodels.mo.details.engagement_association import EngagementAssociation
from ramodels.mo.details.engagement_association import EngagementAssociationBase
from ramodels.mo.details.engagement_association import EngagementAssociationRead
from tests.tests_ramodels.conftest import from_date_strat
from tests.tests_ramodels.conftest import not_from_regex
from tests.tests_ramodels.conftest import to_date_strat
from tests.tests_ramodels.conftest import unexpected_value_error


@st.composite
def base_strat(draw):
    required = {
        "validity": st.builds(Validity),
        "type": st.just("engagement_association"),
    }

    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


@st.composite
def read_strat(draw):
    base_dict = draw(base_strat())
    required = {
        "org_unit_uuid": st.uuids(),
        "engagement_uuid": st.uuids(),
        "engagement_association_type_uuid": st.uuids(),
    }

    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return {**base_dict, **st_dict}


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
        "org_unit_uuid": st.uuids(),
        "engagement_uuid": st.uuids(),
        "engagement_association_type_uuid": st.uuids(),
        "from_date": from_date_strat(),
    }
    optional = {
        "uuid": st.none() | st.uuids(),
        "to_date": st.none() | to_date_strat(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestEngagementAssociation:
    @given(engagement_assoc_strat())
    def test_init(self, model_dict):
        assert EngagementAssociation(**model_dict)

    @given(engagement_assoc_strat(), not_from_regex(r"^engagement_association$"))
    def test_validators(self, model_dict, invalid_type):
        with unexpected_value_error():
            model_dict["type"] = invalid_type
            EngagementAssociation(**model_dict)

    @given(engagement_assoc_fsf_strat())
    def test_from_simplified_fields(self, simp_fields_dict):
        assert EngagementAssociation.from_simplified_fields(**simp_fields_dict)

    @given(base_strat())
    def test_base(self, model_dict):
        assert EngagementAssociationBase(**model_dict)

    @given(read_strat())
    def test_read(self, model_dict):
        assert EngagementAssociationRead(**model_dict)
