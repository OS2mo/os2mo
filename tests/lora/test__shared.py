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
from typing import List
from typing import Union
from uuid import uuid4

import pytest
from hypothesis import assume
from hypothesis import example
from hypothesis import given
from hypothesis import strategies as st
from pydantic import BaseModel
from pydantic import ValidationError

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


def single_item(model, key, list):
    with pytest.raises(ValidationError, match="ensure this value has at most 1 items"):
        model(**{key: list})

    with pytest.raises(ValidationError, match="ensure this value has at least 1 items"):
        model(**{key: []})


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


class TestInfiniteDatetime:
    fail_int = 1
    fail_str = "fail"
    # TODO: We need a test strategy to generate this type of data
    # Biggest issue is probably date/datetime strings?
    accept_dt: List[Union[str, datetime]] = [
        "infinity",
        "-infinity",
        "2011-06-26",
        datetime(2060, 12, 15),
    ]

    @given(st.text(), st.integers())
    def test_init(self, hy_str, hy_int):
        # Unfortunately, this currently works just fine :(
        assert InfiniteDatetime(hy_str) == hy_str
        assert InfiniteDatetime(hy_int) == str(hy_int)

    @given(st.integers())
    def test_from_value(self, hy_int):
        # This should always work
        for dt in self.accept_dt:
            assert InfiniteDatetime.from_value(dt)

        # but this shouldn't
        with pytest.raises(TypeError, match="string or datetime required"):
            InfiniteDatetime.from_value(hy_int)  # type: ignore

        # and this string cannot be parsed
        with pytest.raises(
            ValueError,
            match=f"Unable to parse '{self.fail_str}' as an ISO-8601 datetime string",
        ):
            InfiniteDatetime.from_value(self.fail_str)

    @given(st.integers())
    def test_in_model(self, hy_int):
        class DTModel(BaseModel):
            dt: InfiniteDatetime

        # Same values should work
        for dt in self.accept_dt:
            assert DTModel(dt=dt)

        # But fail values should raise validation errors
        with pytest.raises(ValidationError):
            for err_dt in [hy_int, self.fail_str]:
                DTModel(dt=err_dt)

    @given(st.tuples(st.datetimes(), st.datetimes()))
    @example(
        (
            datetime.fromisoformat("3059-01-01T00:00:00.035840+01:00"),
            datetime.fromisoformat("3059-01-01T00:00:00.035841+01:00"),
        )
    )
    def test_ordering(self, hy_dts):
        from_dt, to_dt = hy_dts
        assume(from_dt < to_dt)
        assert InfiniteDatetime(from_dt) < InfiniteDatetime(to_dt)

    def test_infinity_ordering(self):
        pos_inf_dt = InfiniteDatetime("infinity")
        neg_inf_dt = InfiniteDatetime("-infinity")
        assert neg_inf_dt < pos_inf_dt
        assert (neg_inf_dt < neg_inf_dt) is False
        assert (pos_inf_dt < pos_inf_dt) is False


# --------------------------------------------------------------------------------------
# EffectiveTime
# --------------------------------------------------------------------------------------


class TestEffectiveTime:
    # TODO: This should generate valid InfiniteDatetimes
    # cf. previously mentioned strategy

    @given(st.tuples(st.datetimes(), st.datetimes()))
    @example(
        (
            datetime.fromisoformat("3059-01-01T00:00:00.035840+01:00"),
            datetime.fromisoformat("3059-01-01T00:00:00.035841+01:00"),
        )
    )
    def test_init(self, hy_dts):
        from_dt, to_dt = hy_dts
        assume(from_dt < to_dt)
        assert EffectiveTime(from_date=from_dt, to_date=to_dt)

    @given(st.tuples(st.datetimes(), st.datetimes()))
    def test_validator(self, hy_dts):
        from_dt, to_dt = hy_dts
        assume(from_dt >= to_dt)
        with pytest.raises(
            ValidationError, match="from_date must be strictly less than to_date"
        ):
            EffectiveTime(from_date=from_dt, to_date=to_dt)


@st.composite
def valid_edt(draw):
    from_dt = draw(st.datetimes())
    to_dt = draw(st.datetimes())
    assume(from_dt < to_dt)
    return EffectiveTime(from_date=from_dt, to_date=to_dt)


# --------------------------------------------------------------------------------------
# Authority
# --------------------------------------------------------------------------------------


urn_regex = re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[a-z0-9()+,\-.:=@;$_!*'%/?#]+$")


class TestAuthority:
    valid_urns = st.from_regex(urn_regex)
    invalid_urns = st.text().filter(lambda s: urn_regex.match(s) is None)

    @given(valid_urns, valid_edt())
    def test_init(self, valid_urn, valid_edt):
        assert Authority(urn=valid_urn, effective_time=valid_edt)

    @given(invalid_urns, valid_edt())
    def test_validators(self, invalid_urn, valid_edt):
        with pytest.raises(ValidationError, match="string does not match regex"):
            Authority(urn=invalid_urn, effective_time=valid_edt)


@st.composite
def valid_auth(draw):
    edt = draw(valid_edt())
    return Authority(urn="urn:test:1337", effective_time=edt)


# --------------------------------------------------------------------------------------
# FacetProperties
# --------------------------------------------------------------------------------------


class TestFacetProperties:
    @given(st.text(), valid_edt())
    def test_init(self, key_txt, valid_edt):
        assert FacetProperties(user_key=key_txt, effective_time=valid_edt)


@st.composite
def valid_fp(draw):
    edt = draw(valid_edt())
    return FacetProperties(user_key="test", effective_time=edt)


# --------------------------------------------------------------------------------------
# FacetAttributes
# --------------------------------------------------------------------------------------


class TestFacetAttributes:
    @given(st.lists(valid_fp(), min_size=1, max_size=1))
    def test_init(self, fp_list):
        assert FacetAttributes(properties=fp_list)

    @given(st.lists(valid_fp(), min_size=2))
    def test_validators(self, invalid_fp_list):
        single_item(FacetAttributes, "properties", invalid_fp_list)


# --------------------------------------------------------------------------------------
# Published
# --------------------------------------------------------------------------------------


class TestPublished:
    @given(st.text(), valid_edt())
    def test_init(self, pub_txt, edt):
        # required
        assert Published(effective_time=edt)

        # optional
        assert Published(published=pub_txt, effective_time=edt)


@st.composite
def valid_pub(draw):
    edt = draw(valid_edt())
    return Published(effective_time=edt)


# --------------------------------------------------------------------------------------
# FacetStates
# --------------------------------------------------------------------------------------


class TestFacetStates:
    @given(st.lists(valid_pub(), min_size=1, max_size=1))
    def test_init(self, pub_list):
        assert FacetStates(published_state=pub_list)

    @given(st.lists(valid_pub(), min_size=2))
    def test_validators(self, invalid_pub_list):
        single_item(FacetStates, "published_state", invalid_pub_list)


# --------------------------------------------------------------------------------------
# Responsible
# --------------------------------------------------------------------------------------


class TestResponsible:
    @given(st.uuids(), valid_edt())
    def test_init(self, hy_uuid, edt):
        assert Responsible(object_type="organisation", uuid=hy_uuid, effective_time=edt)

    not_org_str = st.text().filter(lambda s: s != "organisation")

    @given(not_org_str, st.uuids(), valid_edt())
    def test_validators(self, fail_str, hy_uuid, edt):
        with pytest.raises(ValidationError, match="unexpected value;"):
            Responsible(object_type=fail_str, uuid=hy_uuid, effective_time=edt)


@st.composite
def valid_resp(draw):
    edt = draw(valid_edt())
    return Responsible(object_type="organisation", uuid=uuid4(), effective_time=edt)


# --------------------------------------------------------------------------------------
# FacetRef
# --------------------------------------------------------------------------------------


class TestFacetRef:
    @given(st.uuids(), valid_edt())
    def test_init(self, hy_uuid, edt):
        assert FacetRef(object_type="facet", uuid=hy_uuid, effective_time=edt)

    not_facet_str = st.text().filter(lambda s: s != "facet")

    @given(not_facet_str, st.uuids(), valid_edt())
    def test_validators(self, fail_str, hy_uuid, edt):
        with pytest.raises(ValidationError, match="unexpected value;"):
            FacetRef(object_type=fail_str, uuid=hy_uuid, effective_time=edt)


@st.composite
def valid_fref(draw):
    edt = draw(valid_edt())
    return FacetRef(object_type="facet", uuid=uuid4(), effective_time=edt)


# --------------------------------------------------------------------------------------
# FacetRelations
# --------------------------------------------------------------------------------------


class TestFacetRelations:
    @given(st.lists(valid_resp(), min_size=1, max_size=1))
    def test_init(self, resp_list):
        assert FacetRelations(responsible=resp_list)

    @given(st.lists(valid_resp(), min_size=2))
    def test_validators(self, invalid_resp_list):
        single_item(FacetRelations, "responsible", invalid_resp_list)


# --------------------------------------------------------------------------------------
# KlasseProperties
# --------------------------------------------------------------------------------------


class TestKlasseProperties:
    @given(st.text(), st.text(), st.text(), valid_edt())
    def test_init(self, user_txt, title_txt, scope_txt, edt):
        # required
        assert KlasseProperties(user_key=user_txt, title=title_txt, effective_time=edt)

        # optional
        assert KlasseProperties(
            user_key=user_txt, title=title_txt, scope=scope_txt, effective_time=edt
        )


@st.composite
def valid_klsprop(draw):
    edt = draw(valid_edt())
    return KlasseProperties(user_key="user", title="test", effective_time=edt)


# --------------------------------------------------------------------------------------
# KlasseRelations
# --------------------------------------------------------------------------------------


class TestKlasseRelations:
    @given(
        st.lists(valid_resp(), min_size=1, max_size=1),
        st.lists(valid_fref(), min_size=1, max_size=1),
    )
    def test_init(self, resp_list, fref_list):
        assert KlasseRelations(responsible=resp_list, facet=fref_list)

    @given(st.lists(valid_resp(), min_size=2))
    def test_resp_length(self, invalid_resp):
        single_item(KlasseRelations, "responsible", invalid_resp)

    @given(st.lists(valid_fref(), min_size=2))
    def test_fref_length(self, invalid_fref):
        single_item(KlasseRelations, "facet", invalid_fref)


# --------------------------------------------------------------------------------------
# KlasseAttributes
# --------------------------------------------------------------------------------------
class TestKlasseAttributes:
    @given(st.lists(valid_klsprop(), min_size=1, max_size=1))
    def test_init(self, valid_klsprop):
        assert KlasseAttributes(properties=valid_klsprop)

    @given(st.lists(valid_klsprop(), min_size=2))
    def test_validators(self, invalid_klsprop):
        single_item(KlasseAttributes, "properties", invalid_klsprop)


# --------------------------------------------------------------------------------------
# KlasseStates
# --------------------------------------------------------------------------------------
class TestKlasseStates:
    @given(st.lists(valid_pub(), min_size=1, max_size=1))
    def test_init(self, pub_list):
        assert KlasseStates(published_state=pub_list)

    @given(st.lists(valid_pub(), min_size=2))
    def test_validators(self, invalid_pub_list):
        single_item(KlasseStates, "published_state", invalid_pub_list)


# --------------------------------------------------------------------------------------
# OrganisationProperties
# --------------------------------------------------------------------------------------


class TestOrganisationProperties:
    @given(st.text(), st.text(), valid_edt())
    def test_init(self, user_txt, name_txt, edt):
        assert OrganisationProperties(
            user_key=user_txt, name=name_txt, effective_time=edt
        )


@st.composite
def valid_orgprop(draw):
    edt = draw(valid_edt())
    return OrganisationProperties(user_key="user", name="test", effective_time=edt)


# --------------------------------------------------------------------------------------
# OrganisationAttributes
# --------------------------------------------------------------------------------------
class TestOrganisationAttributes:
    @given(st.lists(valid_orgprop(), min_size=1, max_size=1))
    def test_init(self, valid_orgprop):
        assert OrganisationAttributes(properties=valid_orgprop)

    @given(st.lists(valid_orgprop(), min_size=2))
    def test_validators(self, invalid_orgprop):
        single_item(OrganisationAttributes, "properties", invalid_orgprop)


# --------------------------------------------------------------------------------------
# OrganisationValidState
# --------------------------------------------------------------------------------------


class TestOrganisationValidState:
    @given(st.text(), valid_edt())
    def test_init(self, state_txt, edt):
        # required
        assert OrganisationValidState(effective_time=edt)

        # optional
        assert OrganisationValidState(state=state_txt, effective_time=edt)


@st.composite
def valid_orgstate(draw):
    edt = draw(valid_edt())
    return OrganisationValidState(effective_time=edt)


# --------------------------------------------------------------------------------------
# OrganisationStates
# --------------------------------------------------------------------------------------


class TestOrganisationStates:
    @given(st.lists(valid_orgstate(), min_size=1, max_size=1))
    def test_init(self, valid_orgstate):
        assert OrganisationStates(valid_state=valid_orgstate)

    @given(st.lists(valid_orgstate(), min_size=2))
    def test_validators(self, invalid_orgstate):
        single_item(OrganisationStates, "valid_state", invalid_orgstate)


# --------------------------------------------------------------------------------------
# OrganisationRelations
# --------------------------------------------------------------------------------------


class TestOrganisationRelations:
    @given(st.lists(valid_auth(), min_size=1, max_size=1))
    def test_init(self, valid_auth):
        assert OrganisationRelations(authority=valid_auth)

    @given(st.lists(valid_auth(), min_size=2))
    def test_validators(self, invalid_auth):
        single_item(OrganisationRelations, "authority", invalid_auth)
