#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st

from .test__shared import valid_auth
from .test__shared import valid_orgprop
from .test__shared import valid_orgstate
from ramodels.lora import Organisation
from ramodels.lora._shared import OrganisationAttributes
from ramodels.lora._shared import OrganisationRelations
from ramodels.lora._shared import OrganisationStates

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------


@st.composite
def valid_oa(draw):
    orgp_list = draw(st.lists(valid_orgprop(), min_size=1, max_size=1))
    return OrganisationAttributes(properties=orgp_list)


@st.composite
def valid_os(draw):
    orgs_list = draw(st.lists(valid_orgstate(), min_size=1, max_size=1))
    return OrganisationStates(valid_state=orgs_list)


@st.composite
def valid_or(draw):
    auth_list = draw(st.lists(valid_auth(), min_size=1, max_size=1))
    return OrganisationRelations(authority=auth_list)


@st.composite
def valid_dt_range(draw):
    from_dt = draw(st.dates())
    to_dt = draw(st.dates())
    assume(from_dt < to_dt)
    return from_dt.isoformat(), to_dt.isoformat()


class TestOrganisation:
    @given(valid_oa(), valid_os(), valid_or())
    def test_init(self, valid_oa, valid_os, valid_or):
        # Required
        assert Organisation(attributes=valid_oa, states=valid_os)

        # Optioanl
        assert Organisation(attributes=valid_oa, states=valid_os, relations=valid_or)

    @given(st.uuids(), st.text(), st.text(), st.integers(), valid_dt_range())
    def test_from_simplified_fields(self, uuid, name, user_key, mun_code, valid_dts):
        # Required
        assert Organisation.from_simplified_fields(uuid, name, user_key)

        # Optional
        from_dt, to_dt = valid_dts
        assert Organisation.from_simplified_fields(
            uuid, name, user_key, mun_code, from_dt, to_dt
        )
