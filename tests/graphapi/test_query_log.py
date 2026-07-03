# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from fastapi.testclient import TestClient
from structlog.testing import capture_logs

from mora.db.query_log import QUERY_LOG_HEADER

QUERY = """
    query OrgUnits {
      org_units {
        objects {
          uuid
        }
      }
    }
"""


def _postgres_logs(logs: list[dict]) -> list[dict]:
    return [entry for entry in logs if entry.get("event") == "postgres_query"]


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_queries_logged_when_header_set(
    admin_client: TestClient,
    latest_graphql_url: str,
) -> None:
    """When the header is set, executed postgres queries are logged."""
    with capture_logs() as logs:
        response = admin_client.post(
            latest_graphql_url,
            json={"query": QUERY},
            headers={QUERY_LOG_HEADER: "true"},
        )
    assert response.status_code == 200
    assert response.json().get("errors") is None

    postgres_logs = _postgres_logs(logs)
    assert postgres_logs, "expected at least one postgres_query log entry"
    for entry in postgres_logs:
        assert "statement" in entry
        assert "parameters" in entry


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_queries_not_logged_by_default(
    admin_client: TestClient,
    latest_graphql_url: str,
) -> None:
    """Without the header, no postgres queries are logged."""
    with capture_logs() as logs:
        response = admin_client.post(
            latest_graphql_url,
            json={"query": QUERY},
        )
    assert response.status_code == 200
    assert response.json().get("errors") is None

    assert _postgres_logs(logs) == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_header_value_other_than_true_is_ignored(
    admin_client: TestClient,
    latest_graphql_url: str,
) -> None:
    """Any header value other than 'true' leaves logging disabled."""
    with capture_logs() as logs:
        response = admin_client.post(
            latest_graphql_url,
            json={"query": QUERY},
            headers={QUERY_LOG_HEADER: "yes"},
        )
    assert response.status_code == 200
    assert response.json().get("errors") is None

    assert _postgres_logs(logs) == []


@pytest.mark.integration_test
@pytest.mark.usefixtures("empty_db")
async def test_logging_flag_does_not_leak_between_requests(
    admin_client: TestClient,
    latest_graphql_url: str,
) -> None:
    """The flag is scoped to a single request cycle."""
    # First request opts in.
    admin_client.post(
        latest_graphql_url,
        json={"query": QUERY},
        headers={QUERY_LOG_HEADER: "true"},
    )

    # Second request without the header must not produce postgres logs.
    with capture_logs() as logs:
        response = admin_client.post(
            latest_graphql_url,
            json={"query": QUERY},
        )
    assert response.status_code == 200
    assert response.json().get("errors") is None

    assert _postgres_logs(logs) == []
