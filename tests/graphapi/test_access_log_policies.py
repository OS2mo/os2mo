# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""The fields of access log entries are guarded by read policies."""

from unittest.mock import ANY
from uuid import uuid4

import pytest
from more_itertools import one

from mora.db import Collection
from tests.conftest import GraphAPIPost
from tests.conftest import SetAuth
from tests.conftest import SetRules


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


@pytest.mark.integration_test
@pytest.mark.envvar({"ACCESS_LOG_ENABLE": "True"})
@pytest.mark.usefixtures("empty_db")
async def test_an_access_log_field_no_rule_grants_is_denied(
    set_auth: SetAuth, graphapi_post: GraphAPIPost, set_rules: SetRules
) -> None:
    """A field of an access log entry no rule grants is denied where it is read."""
    await set_rules("policy_reader", Collection.AccessLog, {"model"})
    set_auth({"policy_reader"}, uuid4())
    query = "query { access_log { objects { model actor } } }"
    # The second read reads the entry logged by the first
    response = graphapi_post(query)
    assert response.errors is None
    assert response.data == {"access_log": {"objects": []}}

    response = graphapi_post(query)
    assert response.data is None
    error = one(response.errors)
    assert error["message"] == "No policy approved the access"
    assert error["path"] == ["access_log", "objects", 0, "actor"]
