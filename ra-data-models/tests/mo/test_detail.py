from hypothesis import given
from hypothesis import strategies as st
from ramodels.mo._shared import OpenValidity
from ramodels.mo.detail import DetailTermination


class TestDetailTerminate:
    @given(
        st.tuples(st.datetimes() | st.none(), st.datetimes() | st.none()).filter(
            lambda dts: dts[0] <= dts[1] if dts[0] and dts[1] else True
        )
    )
    def test_to_dict(self, dt_from_to):
        given_from_date, given_to_date = dt_from_to
        details_terminate = DetailTermination(
            uuid="7902e588-3c69-405a-8f6c-1717d396086a",
            type="address",
            validity=OpenValidity(
                from_date=given_from_date,
                to_date=given_to_date,
            ),
        )
        details_terminate_dict = details_terminate.to_dict()
        assert details_terminate_dict.get("uuid", None) == str(details_terminate.uuid)
        assert details_terminate_dict.get("type", None) == details_terminate.type

        dict_validity = details_terminate_dict.get("validity", {})
        model_from_date = (
            details_terminate.validity.from_date.date().isoformat()
            if details_terminate.validity.from_date
            else None
        )
        assert dict_validity.get("from", None) == model_from_date

        model_to_date = (
            details_terminate.validity.to_date.date().isoformat()
            if details_terminate.validity.to_date
            else None
        )
        assert dict_validity.get("to", None) == model_to_date
