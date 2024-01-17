# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import re
from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock

import freezegun
from dateutil.tz import tzutc
from fastapi.encoders import jsonable_encoder
from hypothesis import given
from hypothesis import strategies as st
from pytest import MonkeyPatch

from mora import lora
from ramodels.mo import OpenValidity


@freezegun.freeze_time("1970-01-01")
def test_graphql_dates_default(
    graphapi_test, latest_graphql_url, monkeypatch: MonkeyPatch
):
    """Test that default GraphQL date arguments propagate to the LoRa connector."""
    mock = Mock(wraps=lora.Connector)
    monkeypatch.setattr(lora, "Connector", mock)
    response = graphapi_test.post(
        latest_graphql_url, json={"query": "{ employees { objects { uuid } } }"}
    )
    data, errors = response.json().get("data"), response.json().get("errors")
    assert data is not None
    assert errors is None
    now = datetime.now(tz=tzutc())
    assert mock.call_args.kwargs["virkningfra"] == now
    assert mock.call_args.kwargs["virkningtil"] == (now + timedelta(milliseconds=1))


@freezegun.freeze_time("1970-01-01")
@given(dates=st.builds(OpenValidity))
def test_graphql_dates_explicit(
    graphapi_test, dates, latest_graphql_url, monkeysession: MonkeyPatch
):
    """Test that explicit GraphQL date arguments propagate to the LoRa connector."""
    mock = Mock(wraps=lora.Connector)
    monkeysession.setattr(lora, "Connector", mock)
    query = """
            query TestQuery($from_date: DateTime, $to_date: DateTime) {
                employees(filter: {from_date: $from_date, to_date: $to_date}) {
                    objects {
                        uuid
                    }
                }
            }
            """
    response = graphapi_test.post(
        latest_graphql_url,
        json={
            "query": query,
            "variables": {"from_date": dates.from_date, "to_date": dates.to_date},
        },
    )
    data, errors = response.json().get("data"), response.json().get("errors")
    assert data is not None
    assert errors is None
    assert mock.call_args.kwargs["virkningfra"] == dates.from_date or "-infinity"
    assert mock.call_args.kwargs["virkningtil"] == dates.to_date or "infinity"


@given(
    dates=st.tuples(st.datetimes(), st.datetimes()).filter(lambda dts: dts[0] > dts[1]),
)
@freezegun.freeze_time("1970-01-01")
def test_graphql_dates_failure(graphapi_test_no_exc, dates, latest_graphql_url):
    """Test failing GraphQL date arguments.

    We use a test client that silences server side errors in order to
    check GraphQL's error response.
    """
    query = """
            query TestQuery($from_date: DateTime, $to_date: DateTime) {
                employees(filter: {from_date: $from_date, to_date: $to_date}) {
                    objects {
                        uuid
                    }
                }
            }
            """
    dates = jsonable_encoder(dates)
    response = graphapi_test_no_exc.post(
        latest_graphql_url,
        json={
            "query": query,
            "variables": {
                "from_date": dates[0],
                "to_date": dates[1],
            },
        },
    )
    data, errors = response.json().get("data"), response.json().get("errors")
    assert data is None
    assert errors is not None
    for error in errors:
        assert re.match(
            r"from_date .* must be less than or equal to to_date .*",
            error["message"],
        )

    # Test the specific case where from is None and to is UNSET
    response = graphapi_test_no_exc.post(
        latest_graphql_url,
        json={"query": query, "variables": {"from_date": None}},
    )
    data, errors = response.json().get("data"), response.json().get("errors")
    assert data is None
    assert errors is not None
    for error in errors:
        assert re.match(
            r"Cannot infer UNSET to_date from interval starting at -infinity",
            error["message"],
        )
