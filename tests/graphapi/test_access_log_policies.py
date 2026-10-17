# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Reading the fields of access log entries."""

from unittest.mock import ANY
from uuid import uuid4

import pytest

from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth


@pytest.mark.integration_test
@pytest.mark.envvar({"ACCESS_LOG_ENABLE": "True"})
@pytest.mark.usefixtures("empty_db")
async def test_a_reader_reads_the_fields_of_an_access_log_entry(
    set_auth: SetAuth, graphapi_post: GraphAPIPost
) -> None:
    """A reader reads every field of an access log entry."""
    reader = uuid4()
    set_auth({"reader"}, reader)
    query = """
        query {
          access_log {
            objects { id time actor actor_object { uuid } model uuids }
          }
        }
    """
    # The second read reads the entry logged by the first
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"access_log": {"objects": []}}

    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {
        "access_log": {
            "objects": [
                {
                    "id": ANY,
                    "time": ANY,
                    "actor": str(reader),
                    "actor_object": {"uuid": str(reader)},
                    "model": "ACCESS_LOG",
                    "uuids": [],
                }
            ]
        }
    }
