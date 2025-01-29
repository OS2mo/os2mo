# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from datetime import datetime
from functools import partial
from typing import Literal
from typing import cast

import pytest
from hypothesis import assume
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st
from pydantic import BaseModel
from pydantic import Field
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
from ramodels.lora._shared import ITSystemAttributes
from ramodels.lora._shared import ITSystemProperties
from ramodels.lora._shared import ITSystemRelations
from ramodels.lora._shared import ITSystemStates
from ramodels.lora._shared import ITSystemValidState
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
from ramodels.lora._shared import OwnerRef
from ramodels.lora._shared import Published
from ramodels.lora._shared import Relation
from ramodels.lora._shared import Responsible
from ramodels.lora._shared import get_relations

from ramodels_tests.conftest import date_strat
from ramodels_tests.conftest import not_from_regex
from ramodels_tests.conftest import tz_dt_strat
from ramodels_tests.conftest import unexpected_value_error
from ramodels_tests.test_base import is_isodt_str

single_item_error = partial(
    pytest.raises,
    ValidationError,
    match=r"ensure this value has at (most|least) 1 items",
)


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
    def test_uuid_validator(self, hy_uuid):
        class LoraSub(LoraBase):
            pass

        # UUIDs should be auto-generated
        lora_sub = LoraSub()
        assert lora_sub.uuid.version == 4

        # But we should also be able to set them explicitly
        lora_sub_with_uuid = LoraSub(uuid=hy_uuid)
        assert lora_sub_with_uuid.uuid == hy_uuid

    def test_object_type_validator(self):
        class LoRaSub(LoraBase):
            object_type: Literal["my_type"] = Field("my_type")

        assert LoRaSub()
        assert LoRaSub(object_type="My_Type")  # type: ignore

        # Test non-string object_type for coverage
        with pytest.raises(ValidationError):
            LoRaSub(object_type=123)  # type: ignore


@st.composite
def inf_dt_strat(draw):
    valid_str = (
        date_strat().map(lambda date: date.isoformat())  # type: ignore
        | st.just("-infinity")
        | st.just("infinity")
    )
    return draw(tz_dt_strat() | valid_str)


@st.composite
def everything_except_inf_dt(draw):
    def not_instance_inf_dt(t) -> bool:
        return not isinstance(t, InfiniteDatetime)

    # Using filter here as per the from_type example in hypothesis gives a mypy
    # covariant type error. Ignoring the error using type: ignore gives a SUPER WEIRD
    # mypy error in line 886 (which doesn't exist). So I decided to use assume. /NKJ
    types = st.from_type(type).flatmap(st.from_type)
    assume(not_instance_inf_dt(types))
    return draw(types)


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
            for err_dt in (ht_str, ht_int):
                DTModel(dt=err_dt)

    @given(
        st.tuples(
            tz_dt_strat(),
            tz_dt_strat(),
        ).filter(lambda x: x[0] < x[1]),
        everything_except_inf_dt(),
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
    def test_ordering(self, ht_dts, not_inf_dt):
        from_dt, to_dt = ht_dts
        from_inf_dt, to_inf_dt = InfiniteDatetime(from_dt), InfiniteDatetime(to_dt)
        assert from_inf_dt < to_inf_dt
        assert (from_inf_dt >= to_inf_dt) is False

        # Not defined betweeen InfiniteDatetime and other things
        with pytest.raises(TypeError):
            from_inf_dt < not_inf_dt

        pos_inf_dt = InfiniteDatetime("infinity")
        neg_inf_dt = InfiniteDatetime("-infinity")
        assert neg_inf_dt < from_inf_dt < to_inf_dt < pos_inf_dt
        assert (neg_inf_dt < neg_inf_dt) is False
        assert (pos_inf_dt < pos_inf_dt) is False


@st.composite
def valid_inf_dt(draw):
    valid_input = draw(inf_dt_strat())
    return InfiniteDatetime.from_value(valid_input)


@st.composite
def effective_time_strat(draw):
    required = {
        "from_date": valid_inf_dt(),
        "to_date": valid_inf_dt(),
    }
    optional = {
        "from_included": st.none() | st.booleans(),
        "to_included": st.none() | st.booleans(),
        "actor_type": st.none() | st.text(),
        "actor_ref": st.none() | st.uuids(),
    }
    st_dict = draw(
        st.fixed_dictionaries(required, optional=optional).filter(  # type: ignore
            lambda d: d["from_date"] < d["to_date"]
        )
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


urn_pat = r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$"


@st.composite
def authority_strat(draw):
    required = {
        "urn": st.from_regex(urn_pat),
        "effective_time": valid_edt(),
    }
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


class TestAuthority:
    @given(authority_strat())
    def test_init(self, model_dict):
        assert Authority(**model_dict)

    @given(authority_strat(), not_from_regex(urn_pat))
    def test_validators(self, model_dict, invalid_urn):
        model_dict["urn"] = invalid_urn
        with pytest.raises(ValidationError, match="string does not match regex"):
            Authority(**model_dict)


@st.composite
def valid_auth(draw):
    model_dict = draw(authority_strat())
    return Authority(**model_dict)


@st.composite
def facet_prop_strat(draw):
    required = {"user_key": st.text(), "effective_time": valid_edt()}
    optional = {"description": st.none() | st.text()}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestFacetProperties:
    @given(facet_prop_strat())
    def test_init(self, model_dict):
        assert FacetProperties(**model_dict)

    @given(facet_prop_strat())
    def test_remove_integration_data(self, model_dict):
        model_dict["integration_data"] = "test"
        result = FacetProperties(**model_dict)
        assert "integration_data" not in result.dict()

    @given(facet_prop_strat())
    def test_remove_integrationsdata(self, model_dict):
        model_dict["integrationsdata"] = "test"
        result = FacetProperties(**model_dict)
        assert "integrationsdata" not in result.dict()


@st.composite
def valid_fp(draw):
    model_dict = draw(facet_prop_strat())
    return FacetProperties(**model_dict)


@st.composite
def facet_attr_strat(draw):
    required = {"properties": st.lists(valid_fp(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def invalid_facet_attr_strat(draw):
    prop_strat = st.lists(valid_fp(), max_size=0) | st.lists(
        valid_fp(), min_size=2, max_size=5
    )
    required = {"properties": prop_strat}
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


@st.composite
def facet_states_strat(draw):
    required = {"published_state": st.lists(valid_pub(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def invalid_facet_states_strat(draw):
    pub_st_strat = st.lists(valid_pub(), max_size=0) | st.lists(valid_pub(), min_size=2)
    required = {"published_state": pub_st_strat}
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

    @given(responsible_strat(), not_from_regex(r"^organisation$"))
    def test_validators(self, model_dict, invalid_object_type):
        model_dict["object_type"] = invalid_object_type
        with unexpected_value_error():
            Responsible(**model_dict)


@st.composite
def valid_resp(draw):
    model_dict = draw(responsible_strat())
    return Responsible(**model_dict)


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

    @given(facet_ref_strat(), not_from_regex(r"^facet$"))
    def test_validators(self, model_dict, invalid_object_type):
        model_dict["object_type"] = invalid_object_type
        with unexpected_value_error():
            FacetRef(**model_dict)


@st.composite
def valid_fref(draw):
    model_dict = draw(facet_ref_strat())
    return FacetRef(**model_dict)


@st.composite
def owner_ref_strat(draw):
    required = {"uuid": st.uuids(), "effective_time": valid_edt()}
    optional = {"object_type": st.just("organisationenhed")}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))
    return st_dict


class TestOwnerRef:
    @given(owner_ref_strat())
    def test_init(self, model_dict):
        assert OwnerRef(**model_dict)

    @given(owner_ref_strat(), not_from_regex(r"^organisationenhed$"))
    def test_validators(self, model_dict, invalid_object_type):
        model_dict["object_type"] = invalid_object_type
        with unexpected_value_error():
            OwnerRef(**model_dict)


@st.composite
def valid_oref(draw):
    model_dict = draw(owner_ref_strat())
    return OwnerRef(**model_dict)


@st.composite
def facet_relations_strat(draw):
    required = {"responsible": st.lists(valid_resp(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))
    return st_dict


@st.composite
def invalid_facet_relations_strat(draw):
    resp_strat = st.lists(valid_resp(), max_size=0) | st.lists(
        valid_resp(), min_size=2, max_size=5
    )
    required = {
        # Max size explicitly set for faster data generation
        "responsible": resp_strat
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


@st.composite
def itsys_prop_strat(draw):
    required = {"user_key": st.text(), "effective_time": valid_edt()}
    optional = {
        "name": st.text(),
        "type": st.text(),
        "configuration_ref": st.lists(st.text()),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestITSysProperties:
    @given(itsys_prop_strat())
    def test_init(self, model_dict):
        assert ITSystemProperties(**model_dict)


@st.composite
def itsys_valid_prop(draw):
    model_dict = draw(itsys_prop_strat())
    return ITSystemProperties(**model_dict)


@st.composite
def itsys_attr_strat(draw):
    required = {"properties": st.lists(itsys_valid_prop(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


@st.composite
def invalid_itsys_attr_strat(draw):
    required = {
        "properties": (
            st.lists(itsys_valid_prop(), max_size=0)
            | st.lists(itsys_valid_prop(), min_size=2, max_size=5)
        )
    }
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


class TestITSysAttributes:
    @given(itsys_attr_strat())
    def test_init(self, model_dict):
        assert ITSystemAttributes(**model_dict)

    @given(invalid_itsys_attr_strat())
    def test_validators(self, invalid_model_dict):
        with single_item_error():
            ITSystemAttributes(**invalid_model_dict)


@st.composite
def valid_itsys_attr(draw):
    model_dict = draw(itsys_attr_strat())
    return ITSystemAttributes(**model_dict)


@st.composite
def relation_strat(draw):
    required = {"uuid": st.uuids(), "effective_time": valid_edt()}
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


class TestRelation:
    @given(relation_strat())
    def test_init(self, model_dict):
        assert Relation(**model_dict)


@st.composite
def valid_relation(draw):
    model_dict = draw(relation_strat())
    return Relation(**model_dict)


@st.composite
def get_relations_strat(draw):
    required = {
        "uuids": st.none() | st.uuids() | st.lists(st.uuids(), min_size=1),
        "effective_time": valid_edt(),
    }
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


class TestGetRelations:
    @given(get_relations_strat())
    def test_get_relations(self, params):
        uuids = params.get("uuids")
        if uuids is None:
            assert get_relations(**params) is None
        elif isinstance(uuids, list):
            assert len(cast(list, get_relations(**params))) == len(uuids)
        else:
            # single UUID
            assert len(cast(list, get_relations(**params))) == 1


@st.composite
def itsys_relations_strat(draw):
    optional = {
        "belongs_to": st.none() | st.lists(valid_relation(), min_size=1, max_size=1),
        "affiliated_orgs": st.none() | st.lists(valid_relation(), min_size=1),
        "affiliated_units": st.none() | st.lists(valid_relation(), min_size=1),
        "affiliated_functions": st.none() | st.lists(valid_relation(), min_size=1),
        "affiliated_users": st.none() | st.lists(valid_relation(), min_size=1),
        "affiliated_interests": st.none() | st.lists(valid_relation(), min_size=1),
        "affiliated_itsystems": st.none() | st.lists(valid_relation(), min_size=1),
        "affiliated_persons": st.none() | st.lists(valid_relation(), min_size=1),
        "addresses": st.none() | st.lists(valid_relation(), min_size=1),
        "system_types": st.none() | st.lists(valid_relation(), min_size=1),
        "tasks": st.none() | st.lists(valid_relation(), min_size=1),
    }
    st_dict = draw(st.fixed_dictionaries({}, optional=optional))  # type: ignore
    return st_dict


@st.composite
def invalid_itsys_relations_strat(draw):
    required = {
        "belongs_to": (
            st.lists(valid_relation(), max_size=0)
            | st.lists(valid_relation(), min_size=2, max_size=5)
        ),
        "affiliated_orgs": st.lists(valid_relation(), max_size=0),
        "affiliated_units": st.lists(valid_relation(), max_size=0),
        "affiliated_functions": st.lists(valid_relation(), max_size=0),
        "affiliated_users": st.lists(valid_relation(), max_size=0),
        "affiliated_interests": st.lists(valid_relation(), max_size=0),
        "affiliated_itsystems": st.lists(valid_relation(), max_size=0),
        "affiliated_persons": st.lists(valid_relation(), max_size=0),
        "addresses": st.lists(valid_relation(), max_size=0),
        "system_types": st.lists(valid_relation(), max_size=0),
        "tasks": st.lists(valid_relation(), max_size=0),
    }
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


class TestITSysRelations:
    @given(itsys_relations_strat())
    def test_init(self, model_dict):
        assert ITSystemRelations(**model_dict)

    @given(invalid_itsys_relations_strat())
    def test_validators(self, invalid_model_dict):
        with single_item_error():
            ITSystemRelations(**invalid_model_dict)


@st.composite
def valid_itsys_relations(draw):
    model_dict = draw(itsys_relations_strat())
    return ITSystemRelations(**model_dict)


@st.composite
def itsys_valid_state_strat(draw):
    required = {"state": st.text(), "effective_time": valid_edt()}
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


class TestITSysValidState:
    @given(itsys_valid_state_strat())
    def test_init(self, model_dict):
        assert ITSystemValidState(**model_dict)


@st.composite
def itsys_valid_state(draw):
    model_dict = draw(itsys_valid_state_strat())
    return ITSystemValidState(**model_dict)


@st.composite
def itsys_states_strat(draw):
    required = {"valid_state": st.lists(itsys_valid_state(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


@st.composite
def invalid_itsys_states_strat(draw):
    required = {
        "valid_state": (
            st.lists(itsys_valid_state(), max_size=0)
            | st.lists(itsys_valid_state(), min_size=2, max_size=5)
        )
    }
    st_dict = draw(st.fixed_dictionaries(required))  # type: ignore
    return st_dict


class TestITSysStates:
    @given(itsys_states_strat())
    def test_init(self, model_dict):
        assert ITSystemStates(**model_dict)

    @given(invalid_itsys_states_strat())
    def test_validators(self, invalid_model_dict):
        with single_item_error():
            ITSystemStates(**invalid_model_dict)


@st.composite
def valid_itsys_states(draw):
    model_dict = draw(itsys_states_strat())
    return ITSystemStates(**model_dict)


@st.composite
def klasse_prop_strat(draw):
    required = {
        "user_key": st.text(),
        "title": st.text(),
        "effective_time": valid_edt(),
    }
    optional = {
        "scope": st.none() | st.text(),
        "example": st.none() | st.text(),
        "description": st.none() | st.text(),
    }
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


@st.composite
def klasse_relations_strat(draw):
    required = {
        "responsible": st.lists(valid_resp(), min_size=1, max_size=1),
        "facet": st.lists(valid_fref(), min_size=1, max_size=1),
    }
    optional = {"owner": st.none() | st.lists(valid_oref(), min_size=1, max_size=1)}
    st_dict = draw(st.fixed_dictionaries(required, optional=optional))  # type: ignore
    return st_dict


class TestKlasseRelations:
    @given(klasse_relations_strat())
    def test_init(self, model_dict):
        assert KlasseRelations(**model_dict)

    # Max size explicitly set for faster data generation
    invalid_resp = st.lists(valid_resp(), max_size=0) | st.lists(
        valid_resp(), min_size=2, max_size=5
    )

    @given(klasse_relations_strat(), invalid_resp)
    def test_validators_resp(self, model_dict, invalid_resp):
        model_dict["responsible"] = invalid_resp
        with single_item_error():
            KlasseRelations(**model_dict)

    # Max size explicitly set for faster data generation
    invalid_fref = st.lists(valid_fref(), max_size=0) | st.lists(
        valid_fref(), min_size=2, max_size=5
    )

    @given(klasse_relations_strat(), invalid_fref)
    def test_validators_fref(self, model_dict, invalid_fref):
        model_dict["facet"] = invalid_fref
        with single_item_error():
            KlasseRelations(**model_dict)


@st.composite
def valid_klasse_relations(draw):
    model_dict = draw(klasse_relations_strat())
    return KlasseRelations(**model_dict)


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
    invalid_klsprop = st.lists(valid_klsprop(), max_size=0) | st.lists(
        valid_klsprop(), min_size=2, max_size=5
    )

    @given(klasse_attr_strat(), invalid_klsprop)
    def test_validators(self, model_dict, invalid_klsprop):
        model_dict["properties"] = invalid_klsprop
        with single_item_error():
            KlasseAttributes(**model_dict)


@st.composite
def valid_klasse_attrs(draw):
    model_dict = draw(klasse_attr_strat())
    return KlasseAttributes(**model_dict)


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
    invalid_pub = st.lists(valid_pub(), max_size=0) | st.lists(
        valid_pub(), min_size=2, max_size=5
    )

    @given(klasse_states_strat(), invalid_pub)
    def test_validators(self, model_dict, invalid_pub):
        model_dict["published_state"] = invalid_pub
        with single_item_error():
            KlasseStates(**model_dict)


@st.composite
def valid_klasse_states(draw):
    model_dict = draw(klasse_states_strat())
    return KlasseStates(**model_dict)


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
    invalid_orgprop = st.lists(valid_orgprop(), max_size=0) | st.lists(
        valid_orgprop(), min_size=2, max_size=5
    )

    @given(org_attr_strat(), invalid_orgprop)
    def test_validators(self, model_dict, invalid_orgprop):
        model_dict["properties"] = invalid_orgprop
        with single_item_error():
            OrganisationAttributes(**model_dict)


@st.composite
def valid_org_attrs(draw):
    model_dict = draw(org_attr_strat())
    return OrganisationAttributes(**model_dict)


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
    invalid_orgstate = st.lists(valid_orgstate(), max_size=0) | st.lists(
        valid_orgstate(), min_size=2, max_size=5
    )

    @given(org_states_strat(), invalid_orgstate)
    def test_validators(self, model_dict, invalid_orgstate):
        model_dict["valid_state"] = invalid_orgstate
        with single_item_error():
            OrganisationStates(**model_dict)


@st.composite
def valid_org_states(draw):
    model_dict = draw(org_states_strat())
    return OrganisationStates(**model_dict)


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
    invalid_auth = st.lists(valid_auth(), max_size=0) | st.lists(
        valid_auth(), min_size=2, max_size=5
    )

    @given(org_relations_strat(), invalid_auth)
    def test_validators(self, model_dict, invalid_auth):
        model_dict["authority"] = invalid_auth
        with single_item_error():
            OrganisationRelations(**model_dict)


@st.composite
def valid_org_relations(draw):
    model_dict = draw(org_relations_strat())
    return OrganisationRelations(**model_dict)
