# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

import pytest
from hypothesis import assume
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError
from ramodels.mo._shared import MOBase
from ramodels.mo._shared import MORef
from ramodels.mo._shared import OpenValidity
from ramodels.mo._shared import UUIDBase
from ramodels.mo._shared import Validity
from ramodels.mo._shared import deprecation
from ramodels.mo._shared import split_name
from ramodels.mo._shared import validate_cpr
from ramodels.mo._shared import validate_names

from ramodels_tests.conftest import from_date_strat
from ramodels_tests.conftest import not_from_regex
from ramodels_tests.conftest import to_date_strat


class TestUUIDBase:
    class UUIDSub(UUIDBase):
        pass

    def test_init(self):
        # UUIDBase cannot be instantiated.
        with pytest.raises(TypeError, match="may not be instantiated"):
            UUIDBase()

    def test_fields(self):
        # Subclasses of UUIDBase should have a UUID field
        assert self.UUIDSub.__fields__.get("uuid")

    @given(st.uuids())
    def test_validators(self, ht_uuid):
        # UUIDs should be auto-generated
        assert self.UUIDSub().uuid.version == 4

        # But we should also be able to set them explicitly
        assert self.UUIDSub(uuid=ht_uuid).uuid == ht_uuid


class TestMOBase:
    class MOSub(MOBase):
        pass

    def test_init(self):
        # MOBase cannot be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            MOBase()

    def test_fields(self):
        # Subclasses of MOBase should have a user_key field
        assert self.MOSub.__fields__.get("user_key")

    def test_validators(self):
        # User key must default to UUID
        mo_sub = self.MOSub()
        assert mo_sub.user_key == str(mo_sub.uuid)
        # But we should also be able to set it explicitly
        assert self.MOSub(user_key="test").user_key == "test"

    @given(st.text(), st.text())
    def test_type_validator(self, type_1, type_2):
        # Things should work with no type_ present in the model
        assert self.MOSub()

        # And when type_ is required:
        class MOTypeRequired(MOBase):
            type_: str

        assert MOTypeRequired(type_=type_1)

        # Things should work when setting the default value
        class MOType(MOBase):
            type_: str = type_1

        # assert MOType()
        assert MOType(type_=type_1)

        # But not when setting anything else
        assume(type_1 != type_2)
        with pytest.raises(ValidationError):
            MOType(type_=type_2)


@st.composite
def mo_ref_strat(draw):
    required = {"uuid": st.uuids()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestMORef:
    @given(mo_ref_strat())
    def test_init(self, model_dict):
        assert MORef(**model_dict)


@st.composite
def open_validity_strat(draw):
    optional = {
        "from_date": st.none() | from_date_strat(),
        "to_date": st.none() | to_date_strat(),
    }
    st_dict = draw(st.fixed_dictionaries({}, optional=optional))  # type: ignore
    return st_dict


@st.composite
def validity_strat(draw):
    required = {"from_date": from_date_strat()}
    optional = {"to_date": st.none() | to_date_strat()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestOpenValidity:
    @given(open_validity_strat())
    def test_init(self, model_dict):
        assert OpenValidity(**model_dict)

    @given(
        st.tuples(st.datetimes(), st.datetimes()).filter(lambda dts: dts[0] > dts[1]),
        st.dates(),
    )
    def test_validators(self, dt_tup, from_date_no_tz):
        # tz unaware date becomes tz aware datetime
        validity = OpenValidity(from_date=from_date_no_tz)
        assert isinstance(validity.from_date, datetime)
        assert validity.from_date.tzinfo

        # from_date > to_date should fail
        from_dt, to_dt = dt_tup
        with pytest.raises(
            ValidationError,
            match="from_date .* must be less than or equal to to_date .*",
        ):
            OpenValidity(from_date=from_dt, to_date=to_dt)


class TestValidity:
    @given(validity_strat())
    def test_init(self, model_dict):
        assert Validity(**model_dict)

    @given(st.none())
    def test_none_date(self, from_date):
        # from_date is not allowed to be None
        # We test this because it's allowed in Validity's super class
        with pytest.raises(ValidationError, match="none is not an allowed value"):
            Validity(from_date=from_date)


@st.composite
def invalid_name_combo(draw):
    name_strats = st.just("givenname"), st.just("surname")
    name_dict = draw(
        st.dictionaries(keys=st.one_of(*name_strats), values=st.text(), min_size=1)
    )
    name_dict["name"] = draw(st.text())
    return name_dict


class TestValidatorFunctions:
    def test_deprecation(self):
        msg = "Deprecated"
        with pytest.deprecated_call(match=msg):
            deprecation(msg)

    @given(st.text())
    def test_split_name(self, name):
        assert len(split_name(name)) == 2

    @given(invalid_name_combo(), st.text())
    def test_validate_names(self, invalid_name_dict, name):
        # Test dict with mutually exclusive keys
        with pytest.raises(ValueError, match="mutually exclusive"):
            validate_names(invalid_name_dict, "name", "givenname", "surname")
        # A dict with only name raises a deprecation warning
        with pytest.deprecated_call(match="will be deprecated in a future version"):
            validate_names({"name": name}, "name", "givenname", "surname")

    @given(not_from_regex(r"^\d{10}$"), st.from_regex(r"^([3-5][2-9]|9[2-9])\d{8}$"))
    @example("", "3201012101")
    @example("", "3201014101")
    @example("", "3201559101")
    @example("", "3201016101")
    @example("", "3201767101")
    def test_cpr_validation(self, invalid_regex, invalid_cpr):
        with pytest.raises(ValueError, match="string is invalid"):
            validate_cpr(invalid_regex)
        with pytest.raises(ValueError, match="number is invalid"):
            validate_cpr(invalid_cpr)
