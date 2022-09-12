# SPDX-FileCopyrightText: 2021- Magenta ApS
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
import pytest
from hypothesis import given
from hypothesis import strategies as st

from mora.graphapi.versions.latest.graphql_utils import PrintableStr
from mora.graphapi.versions.latest.models import ClassCreate

# --------------------------------------------------------------------------------------
# Class mutator tests
# --------------------------------------------------------------------------------------

OPTIONAL = {
    "published": st.none() | st.text(),
    "scope": st.none() | st.text(),
    "parent_uuid": st.none() | st.uuids(),
    "example": st.none() | st.text(),
    "owner": st.none() | st.uuids(),
}


@st.composite
def write_strat(draw):
    required = {
        "uuid": st.uuids(),
        "type": st.just("class"),
        "user_key": st.text(),
        "name": st.from_regex(PrintableStr.regex),
        "facet_uuid": st.uuids(),
        "org_uuid": st.uuids(),
    }
    st_dict = draw(st.fixed_dictionaries(required, optional=OPTIONAL))
    return st_dict


class TestClassMutator:
    @given(write_strat())
    def test_write(self, model_dict):

        assert ClassCreate(**model_dict)

    @pytest.mark.parametrize(
        "uuid, type_, user_key, name, org_uuid",
        [
            (
                "23d891b5-85aa-4eee-bec7-e84fe21883c5",
                "class",
                "",
                "\x01",
                "8d6c00dd-4be9-4bdb-a558-1f85183cd920",
            ),
            (
                "23d891b5-85aa-4eee-bec7-e84fe21883c5",
                "class",
                "",
                "",
                "8d6c00dd-4be9-4bdb-a558-1f85183cd920",
            ),
        ],
    )
    def test_write_fails(self, uuid, type_, user_key, name, org_uuid):

        with pytest.raises(Exception):
            ClassCreate(uuid, user_key, type_, name, org_uuid)
