#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import re
from datetime import datetime
from functools import partial

import pytest
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st
from pydantic import BaseModel
from pydantic import ValidationError

from ramodels.exceptions import ISOParseError
from ramodels.lora._shared import Authority
from ramodels.lora._shared import EffectiveTime
from ramodels.lora._shared import FacetAttributes
from ramodels.lora._shared import FacetProperties
from ramodels.lora._shared import FacetRef
from ramodels.lora._shared import FacetRelations
from ramodels.lora._shared import FacetStates
from ramodels.lora._shared import InfiniteDatetime
from ramodels.lora._shared import KlasseAttributes
from ramodels.lora._shared import KlasseProperties
from ramodels.lora._shared import KlasseRelations
from ramodels.lora._shared import KlasseStates
from ramodels.lora._shared import LoraBase
from ramodels.lora._shared import OrganisationAttributes
from ramodels.lora._shared import OrganisationProperties
from ramodels.lora._shared import OrganisationRelations
from ramodels.lora._shared import OrganisationStates
from ramodels.lora._shared import OrganisationValidState
from ramodels.lora._shared import Published
from ramodels.lora._shared import Responsible
from tests.conftest import date_strat
from tests.conftest import tz_dt_strat
from tests.conftest import unexpected_value_error
from tests.test_base import is_isodt_str

single_item_error = partial(
    pytest.raises,
    ValidationError,
    match=r"ensure this value has at (most|least) 1 items",
)


# --------------------------------------------------------------------------------------
# LoraBase
# --------------------------------------------------------------------------------------


class TestLoraBase:
    def test_init(self):
        # LoraBase cannot be instantiated
        with pytest.raises(TypeError, match="may not be instantiated"):
            LoraBase()

    def test_fields(self):
        # Subclasses of LoraBase should have a UUID field
        class LoraSub(LoraBase):
            pass

        assert LoraSub.__fields__.get("uuid")

    @given(st.uuids())
    def test_validators(self, hy_uuid):
        class LoraSub(LoraBase):
            pass

        # UUIDs should be auto-generated
        lora_sub = LoraSub()
        assert lora_sub.uuid.version == 4

        # But we should also be able to set them explicitly
        lora_sub_with_uuid = LoraSub(uuid=hy_uuid)
        assert lora_sub_with_uuid.uuid == hy_uuid


# --------------------------------------------------------------------------------------
# InfiniteDatetime
# --------------------------------------------------------------------------------------


@st.composite
def inf_dt_strat(draw):
    valid_str = (
        date_strat().map(lambda date: date.isoformat())  # type: ignore
        | st.just("-infinity")
        | st.just("infinity")
    )
    return draw(tz_dt_strat() | valid_str)


class TestInfiniteDatetime:
    @given(
        st.text().filter(
            lambda s: not is_isodt_str(s) and s not in {"-infinity", "infinity"}
        ),
        st.integers(),
    )
    def test_init(self, ht_str, ht_int):
        # Unfortunately, this currently works just fine :(
        assert isinstance(InfiniteDatetime(ht_str), InfiniteDatetime)
        assert isinstance(InfiniteDatetime(ht_int), InfiniteDatetime)

        # But a direct call to validate breaks
        with pytest.raises(ISOParseError):
            InfiniteDatetime.validate(ht_str)
        with pytest.raises(TypeError):
            InfiniteDatetime.validate(ht_int)

    @given(
        inf_dt_strat(),
        st.text().filter(
            lambda s: not is_isodt_str(s) and s not in {"-infinity", "infinity"}
        ),
        st.integers(),
    )
    def test_from_value(self, valid_infdt, ht_str, ht_int):
        # This should always work
        assert InfiniteDatetime.from_value(valid_infdt)

        # but this shouldn't
        with pytest.raises(TypeError, match="string or datetime required"):
            InfiniteDatetime.from_value(ht_int)  # type: ignore

        # and this string cannot be parsed
        with pytest.raises(
            ISOParseError,
            match=re.escape(
                f"Unable to parse '{ht_str}' as an ISO-8601 datetime string"
            ),
        ):
            InfiniteDatetime.from_value(ht_str)

    @given(
        inf_dt_strat(),
        st.text().filter(
            lambda s: not is_isodt_str(s) and s not in {"-infinity", "infinity"}
        ),
        st.integers(),
    )
    def test_in_model(self, valid_infdt, ht_str, ht_int):
        class DTModel(BaseModel):
            dt: InfiniteDatetime

        assert DTModel(dt=valid_infdt)

        # But fail values should raise validation errors
        with pytest.raises(ValidationError):
            for err_dt in [ht_str, ht_int]:
                DTModel(dt=err_dt)

    @given(
        st.tuples(
            tz_dt_strat(),
            tz_dt_strat(),
        ).filter(lambda x: x[0] < x[1])
    )
    @example(
        (
            datetime.fromisoformat("3059-01-01T00:00:00.035840+01:00"),
            datetime.fromisoformat("3059-01-01T00:00:00.035841+01:00"),
        ),
        (
            datetime.fromisoformat("2000-01-01T00:00:00+01:00"),
            datetime.fromisoformat("2000-01-01T00:00:00+00:00"),
        ),
    )
    def test_ordering(self, ht_dts):
        from_dt, to_dt = ht_dts
        from_inf_dt, to_inf_dt = InfiniteDatetime(from_dt), InfiniteDatetime(to_dt)
        assert from_inf_dt < to_inf_dt
        assert (from_inf_dt >= to_inf_dt) is False

        pos_inf_dt = InfiniteDatetime("infinity")
        neg_inf_dt = InfiniteDatetime("-infinity")
        assert neg_inf_dt < from_inf_dt < to_inf_dt < pos_inf_dt
        assert (neg_inf_dt < neg_inf_dt) is False
        assert (pos_inf_dt < pos_inf_dt) is False


@st.composite
def valid_inf_dt(draw):
    valid_input = draw(inf_dt_strat())
    return InfiniteDatetime.from_value(valid_input)


# --------------------------------------------------------------------------------------
# EffectiveTime
# --------------------------------------------------------------------------------------


@st.composite
def effective_time_strat(draw):
    required = {
        "from_date": valid_inf_dt(),
        "to_date": valid_inf_dt(),
    }
    st_dict = draw(
        st.fixed_dictionaries(required).filter(lambda d: d["from_date"] < d["to_date"])
    )
    return st_dict


class TestEffectiveTime:
    @given(effective_time_strat())
    @example(
        {
            "from_date": InfiniteDatetime("2000-01-01T00:00:00+01:00"),
            "to_date": InfiniteDatetime("2000-01-01T00:00:00+00:00"),
        }
    )
    def test_init(self, model_dict):
        assert EffectiveTime(**model_dict)

    @given(
        st.tuples(valid_inf_dt(), valid_inf_dt()).filter(lambda dts: dts[0] >= dts[1])
    )
    def test_validator(self, dt_range):
        from_dt, to_dt = dt_range
        with pytest.raises(
            ValidationError, match="from_date must be strictly less than to_date"
        ):
            EffectiveTime(from_date=from_dt, to_date=to_dt)


@st.composite
def valid_edt(draw):
    dt_range = st.tuples(st.datetimes(), st.datetimes()).filter(
        lambda dts: dts[0] < dts[1]
    )
    from_dt, to_dt = draw(dt_range)
    return EffectiveTime(from_date=from_dt, to_date=to_dt)


# --------------------------------------------------------------------------------------
# Authority
# --------------------------------------------------------------------------------------

urn_regex = re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$")


@st.composite
def authority_strat(draw):
    required = {
        "urn": st.from_regex(urn_regex),
        "effective_time": valid_edt(),
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestAuthority:
    @given(authority_strat())
    def test_init(self, model_dict):
        assert Authority(**model_dict)

    @given(authority_strat(), st.text().filter(lambda s: urn_regex.match(s) is None))
    def test_validators(self, model_dict, invalid_urn):
        model_dict["urn"] = invalid_urn
        with pytest.raises(ValidationError, match="string does not match regex"):
            Authority(**model_dict)


@st.composite
def valid_auth(draw):
    model_dict = draw(authority_strat())
    return Authority(**model_dict)


# --------------------------------------------------------------------------------------
# FacetProperties
# --------------------------------------------------------------------------------------


@st.composite
def facet_prop_strat(draw):
    required = {"user_key": st.text(), "effective_time": valid_edt()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestFacetProperties:
    @given(facet_prop_strat())
    def test_init(self, model_dict):
        assert FacetProperties(**model_dict)


@st.composite
def valid_fp(draw):
    model_dict = draw(facet_prop_strat())
    return FacetProperties(**model_dict)


# --------------------------------------------------------------------------------------
# FacetAttributes
# --------------------------------------------------------------------------------------


@st.composite
def facet_attr_strat(draw):
    required = {"properties": st.lists(valid_fp(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def invalid_facet_attr_strat(draw):
    required = {
        "properties": st.lists(valid_fp(), min_size=2, max_size=5)
        | st.lists(valid_fp(), max_size=0)
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestFacetAttributes:
    @given(facet_attr_strat())
    def test_init(self, model_dict):
        assert FacetAttributes(**model_dict)

    @given(invalid_facet_attr_strat())
    def test_validators(self, invalid_model_dict):
        with single_item_error():
            FacetAttributes(**invalid_model_dict)


@st.composite
def valid_facet_attrs(draw):
    model_dict = draw(facet_attr_strat())
    return FacetAttributes(**model_dict)


# --------------------------------------------------------------------------------------
# Published
# --------------------------------------------------------------------------------------


@st.composite
def published_strat(draw):
    required = {"effective_time": valid_edt()}
    optional = {"published": st.text()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestPublished:
    @given(published_strat())
    def test_init(self, model_dict):
        assert Published(**model_dict)


@st.composite
def valid_pub(draw):
    model_dict = draw(published_strat())
    return Published(**model_dict)


# --------------------------------------------------------------------------------------
# FacetStates
# --------------------------------------------------------------------------------------


@st.composite
def facet_states_strat(draw):
    required = {"published_state": st.lists(valid_pub(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def invalid_facet_states_strat(draw):
    required = {
        "published_state": st.lists(valid_pub(), min_size=2)
        | st.lists(valid_pub(), max_size=0)
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestFacetStates:
    @given(facet_states_strat())
    def test_init(self, model_dict):
        assert FacetStates(**model_dict)

    @given(invalid_facet_states_strat())
    def test_validators(self, invalid_model_dict):
        with single_item_error():
            FacetStates(**invalid_model_dict)


@st.composite
def valid_facet_states(draw):
    model_dict = draw(facet_states_strat())
    return FacetStates(**model_dict)


# --------------------------------------------------------------------------------------
# Responsible
# --------------------------------------------------------------------------------------


@st.composite
def responsible_strat(draw):
    required = {"uuid": st.uuids(), "effective_time": valid_edt()}
    optional = {"object_type": st.just("organisation")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestResponsible:
    @given(responsible_strat())
    def test_init(self, model_dict):
        assert Responsible(**model_dict)

    @given(responsible_strat(), st.text().filter(lambda s: s != "organisation"))
    def test_validators(self, model_dict, invalid_object_type):
        model_dict["object_type"] = invalid_object_type
        with unexpected_value_error():
            Responsible(**model_dict)


@st.composite
def valid_resp(draw):
    model_dict = draw(responsible_strat())
    return Responsible(**model_dict)


# --------------------------------------------------------------------------------------
# FacetRef
# --------------------------------------------------------------------------------------


@st.composite
def facet_ref_strat(draw):
    required = {"uuid": st.uuids(), "effective_time": valid_edt()}
    optional = {"object_type": st.just("facet")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestFacetRef:
    @given(facet_ref_strat())
    def test_init(self, model_dict):
        assert FacetRef(**model_dict)

    @given(facet_ref_strat(), st.text().filter(lambda s: s != "facet"))
    def test_validators(self, model_dict, invalid_object_type):
        model_dict["object_type"] = invalid_object_type
        with unexpected_value_error():
            FacetRef(**model_dict)


@st.composite
def valid_fref(draw):
    model_dict = draw(facet_ref_strat())
    return FacetRef(**model_dict)


# --------------------------------------------------------------------------------------
# FacetRelations
# --------------------------------------------------------------------------------------


@st.composite
def facet_relations_strat(draw):
    required = {"responsible": st.lists(valid_resp(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def invalid_facet_relations_strat(draw):
    required = {
        # Max size explicitly set for faster data generation
        "responsible": st.lists(valid_resp(), min_size=2, max_size=5)
        | st.lists(valid_resp(), max_size=0)
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestFacetRelations:
    @given(facet_relations_strat())
    def test_init(self, model_dict):
        assert FacetRelations(**model_dict)

    @given(invalid_facet_relations_strat())
    def test_validators(self, invalid_model_dict):
        with single_item_error():
            FacetRelations(**invalid_model_dict)


@st.composite
def valid_facet_relations(draw):
    model_dict = draw(facet_relations_strat())
    return FacetRelations(**model_dict)


# --------------------------------------------------------------------------------------
# KlasseProperties
# --------------------------------------------------------------------------------------


@st.composite
def klasse_prop_strat(draw):
    required = {
        "user_key": st.text(),
        "title": st.text(),
        "effective_time": valid_edt(),
    }
    optional = {"scope": st.text() | st.none()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestKlasseProperties:
    @given(klasse_prop_strat())
    def test_init(self, model_dict):
        assert KlasseProperties(**model_dict)


@st.composite
def valid_klsprop(draw):
    model_dict = draw(klasse_prop_strat())
    return KlasseProperties(**model_dict)


# --------------------------------------------------------------------------------------
# KlasseRelations
# --------------------------------------------------------------------------------------


@st.composite
def klasse_relations_strat(draw):
    required = {
        "responsible": st.lists(valid_resp(), min_size=1, max_size=1),
        "facet": st.lists(valid_fref(), min_size=1, max_size=1),
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestKlasseRelations:
    @given(klasse_relations_strat())
    def test_init(self, model_dict):
        assert KlasseRelations(**model_dict)

    # Max size explicitly set for faster data generation
    @given(
        klasse_relations_strat(),
        st.lists(valid_resp(), min_size=2, max_size=5)
        | st.lists(valid_resp(), max_size=0),
    )
    def test_validators_resp(self, model_dict, invalid_resp):
        model_dict["responsible"] = invalid_resp
        with single_item_error():
            KlasseRelations(**model_dict)

    # Max size explicitly set for faster data generation
    @given(
        klasse_relations_strat(),
        st.lists(valid_fref(), min_size=2, max_size=5)
        | st.lists(valid_resp(), max_size=0),
    )
    def test_validators_fref(self, model_dict, invalid_fref):
        model_dict["facet"] = invalid_fref
        with single_item_error():
            KlasseRelations(**model_dict)


@st.composite
def valid_klasse_relations(draw):
    model_dict = draw(klasse_relations_strat())
    return KlasseRelations(**model_dict)


# --------------------------------------------------------------------------------------
# KlasseAttributes
# --------------------------------------------------------------------------------------


@st.composite
def klasse_attr_strat(draw):
    required = {"properties": st.lists(valid_klsprop(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestKlasseAttributes:
    @given(klasse_attr_strat())
    def test_init(self, model_dict):
        assert KlasseAttributes(**model_dict)

    # Max size explicitly set for faster data generation
    @given(
        klasse_attr_strat(),
        st.lists(valid_klsprop(), min_size=2, max_size=5)
        | st.lists(valid_klsprop(), max_size=0),
    )
    def test_validators(self, model_dict, invalid_klsprop):
        model_dict["properties"] = invalid_klsprop
        with single_item_error():
            KlasseAttributes(**model_dict)


@st.composite
def valid_klasse_attrs(draw):
    model_dict = draw(klasse_attr_strat())
    return KlasseAttributes(**model_dict)


# --------------------------------------------------------------------------------------
# KlasseStates
# --------------------------------------------------------------------------------------


@st.composite
def klasse_states_strat(draw):
    required = {"published_state": st.lists(valid_pub(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestKlasseStates:
    @given(klasse_states_strat())
    def test_init(self, model_dict):
        assert KlasseStates(**model_dict)

    # Max size explicitly set for faster data generation
    @given(
        klasse_states_strat(),
        st.lists(valid_pub(), min_size=2, max_size=5)
        | st.lists(valid_pub(), max_size=0),
    )
    def test_validators(self, model_dict, invalid_pub_list):
        model_dict["published_state"] = invalid_pub_list
        with single_item_error():
            KlasseStates(**model_dict)


@st.composite
def valid_klasse_states(draw):
    model_dict = draw(klasse_states_strat())
    return KlasseStates(**model_dict)


# --------------------------------------------------------------------------------------
# OrganisationProperties
# --------------------------------------------------------------------------------------


@st.composite
def org_prop_strat(draw):
    required = {"user_key": st.text(), "name": st.text(), "effective_time": valid_edt()}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrganisationProperties:
    @given(org_prop_strat())
    def test_init(self, model_dict):
        assert OrganisationProperties(**model_dict)


@st.composite
def valid_orgprop(draw):
    model_dict = draw(org_prop_strat())
    return OrganisationProperties(**model_dict)


# --------------------------------------------------------------------------------------
# OrganisationAttributes
# --------------------------------------------------------------------------------------


@st.composite
def org_attr_strat(draw):
    required = {"properties": st.lists(valid_orgprop(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrganisationAttributes:
    @given(org_attr_strat())
    def test_init(self, model_dict):
        assert OrganisationAttributes(**model_dict)

    # Max size explicitly set for faster data generation
    @given(
        org_attr_strat(),
        st.lists(valid_orgprop(), min_size=2, max_size=5)
        | st.lists(valid_orgprop(), max_size=0),
    )
    def test_validators(self, model_dict, invalid_orgprop):
        model_dict["properties"] = invalid_orgprop
        with single_item_error():
            OrganisationAttributes(**model_dict)


@st.composite
def valid_org_attrs(draw):
    model_dict = draw(org_attr_strat())
    return OrganisationAttributes(**model_dict)


# --------------------------------------------------------------------------------------
# OrganisationValidState
# --------------------------------------------------------------------------------------


@st.composite
def org_valid_states_strat(draw):
    required = {"effective_time": valid_edt()}
    optional = {"state": st.text()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestOrganisationValidState:
    @given(org_valid_states_strat())
    def test_init(self, model_dict):
        assert OrganisationValidState(**model_dict)


@st.composite
def valid_orgstate(draw):
    model_dict = draw(org_valid_states_strat())
    return OrganisationValidState(**model_dict)


# --------------------------------------------------------------------------------------
# OrganisationStates
# --------------------------------------------------------------------------------------


@st.composite
def org_states_strat(draw):
    required = {"valid_state": st.lists(valid_orgstate(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrganisationStates:
    @given(org_states_strat())
    def test_init(self, model_dict):
        assert OrganisationStates(**model_dict)

    # Max size explicitly set for faster data generation
    @given(
        org_states_strat(),
        st.lists(valid_orgstate(), min_size=2, max_size=5)
        | st.lists(valid_orgstate(), max_size=0),
    )
    def test_validators(self, model_dict, invalid_orgstate):
        model_dict["valid_state"] = invalid_orgstate
        with single_item_error():
            OrganisationStates(**model_dict)


@st.composite
def valid_org_states(draw):
    model_dict = draw(org_states_strat())
    return OrganisationStates(**model_dict)


# --------------------------------------------------------------------------------------
# OrganisationRelations
# --------------------------------------------------------------------------------------


@st.composite
def org_relations_strat(draw):
    required = {"authority": st.lists(valid_auth(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestOrganisationRelations:
    @given(org_relations_strat())
    def test_init(self, model_dict):
        assert OrganisationRelations(**model_dict)

    # Max size explicitly set for faster data generation
    @given(
        org_relations_strat(),
        st.lists(valid_auth(), min_size=2, max_size=5)
        | st.lists(valid_auth(), max_size=0),
    )
    def test_validators(self, model_dict, invalid_auth):
        model_dict["authority"] = invalid_auth
        with single_item_error():
            OrganisationRelations(**model_dict)


@st.composite
def valid_org_relations(draw):
    model_dict = draw(org_relations_strat())
    return OrganisationRelations(**model_dict)
