# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import pytest
from _pytest.monkeypatch import MonkeyPatch
from mora.audit import audit_log
from mora.db import AuditLogOperation
from mora.db import AuditLogRead
from more_itertools import first
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from tests.conftest import GQLResponse
from tests.conftest import GraphAPIPost


@pytest.mark.integration_test
async def test_query_auditlog(
    another_transaction,
    set_settings: MonkeyPatch,
    graphapi_post: GraphAPIPost,
    fixture_db: async_sessionmaker,
) -> None:
    """Test querying audit log across v17 shim."""

    # Remove all audit log entries present
    async with another_transaction() as (_, session):
        await session.execute(delete(AuditLogRead))
        await session.execute(delete(AuditLogOperation))

    set_settings(AUDIT_READLOG_ENABLE="True")

    async with another_transaction() as (_, session):
        audit_log(session, "test_auditlog", "OrganisationFunktion", {}, [])

    query = """
        query TestAuditLog($filter: AuditLogFilter!) {
            auditlog(filter: $filter, limit: 1) {
                objects {
                    model
                }
            }
        }
    """

    # filter under v17 schema
    v17_input = {"filter": {"models": "OrganisationFunktion"}}
    # filter under v18 schema
    v18_input = {"filter": {"models": "ORGANISATION_FUNCTION"}}

    # Test it
    response_v17: GQLResponse = graphapi_post(query, v17_input, url="/graphql/v17")
    assert response_v17.errors is None
    assert response_v17.data["auditlog"]["objects"] == [
        {"model": "OrganisationFunktion"}
    ]

    response_v18: GQLResponse = graphapi_post(query, v18_input, url="/graphql/v18")
    assert response_v18.errors is None
    assert response_v18.data["auditlog"]["objects"] == [
        {"model": "ORGANISATION_FUNCTION"}
    ]

    # Running v17 filter on v18 schema
    response = graphapi_post(query, v17_input, url="/graphql/v18")
    error = first(response.errors)
    assert (
        "Variable '$filter' got invalid value 'OrganisationFunktion' at 'filter.models'"
        in error["message"]
    )

    # Running v18 filter on v17 schema
    # Not an error, just searching for something non-existent
    response = graphapi_post(query, v18_input, url="/graphql/v17")
    assert response.errors is None
    assert response.data["auditlog"]["objects"] == []
