#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from datetime import datetime

import pytest
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from ramodels.mo._shared import MOBase
from ramodels.mo._shared import MORef
from ramodels.mo._shared import Validity
from tests.conftest import from_date_strat
from tests.conftest import to_date_strat

# --------------------------------------------------------------------------------------
# MOBase
# --------------------------------------------------------------------------------------


class TestMOBase:
    def test_init(self):
        # MOBase cannot be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            MOBase()

    def test_fields(self):
        # Subclasses of MOBase should have a UUID field
        class MOSub(MOBase):
            pass

        assert MOSub.__fields__.get("uuid")


# --------------------------------------------------------------------------------------
# MORef
# --------------------------------------------------------------------------------------


@st.composite
def mo_ref_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestMORef:
    @given(mo_ref_strat())
    def test_init(self, model_dict):
        assert MORef(**model_dict)


# --------------------------------------------------------------------------------------
# Validity
# --------------------------------------------------------------------------------------


@st.composite
def validity_strat(draw):
    required = {"from_date": from_date_strat()}
    optional = {"to_date": st.none() | to_date_strat()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestValidity:
    @given(validity_strat())
    def test_init(self, model_dict):
        assert Validity(**model_dict)

    @given(st.tuples(st.datetimes(), st.datetimes()), st.dates())
    def test_validators(self, dt_tup, from_date_no_tz):
        # tz unaware date becomes tz aware datetime
        validity = Validity(from_date=from_date_no_tz)
        assert isinstance(validity.from_date, datetime)
        assert validity.from_date.tzinfo

        # from_date > to_date should fail
        from_dt, to_dt = dt_tup
        assume(from_dt > to_dt)
        with pytest.raises(
            ValidationError, match="from_date must be less than or equal to to_date"
        ):
            Validity(from_date=from_dt, to_date=to_dt)
