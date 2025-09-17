# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo.detail import DetailTermination


class TestDetailTerminate:
    @given(
        st.tuples(st.datetimes() | st.none(), st.datetimes() | st.none()).filter(
            lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
        )
    )
    def test_to_dict(self, dt_from_to) -> None:
        given_from_date, given_to_date = dt_from_to

        details_terminate_args = {
            "uuid": "7902e588-3c69-405a-8f6c-1717d396086a",
            "type": "address",
        }

        if given_from_date or given_to_date:
            details_terminate_args["validity"] = {
                "from": given_from_date,
                "to": given_to_date,
            }

        details_terminate = DetailTermination(**details_terminate_args)
        details_terminate_dict = details_terminate.to_dict()

        # Assert normal stuff
        assert details_terminate_dict.get("uuid", None) == str(details_terminate.uuid)
        assert details_terminate_dict.get("type", None) == details_terminate.type

        # Assert validity
        dict_validity = details_terminate_dict.get("validity", {})
        model_validity = details_terminate.validity or {}

        assert dict_validity.get("from", None) == model_validity.get("from", None)
        assert dict_validity.get("to", None) == model_validity.get("to", None)
