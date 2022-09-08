#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 - 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------------------------
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# --------------------------------------------------------------------------------------
# Code
# --------------------------------------------------------------------------------------

pytestmark = pytest.mark.serial


@pytest.mark.usefixtures("sample_structures")
class TestOrganisationEndpoints:
    def test_list_organisation(self, service_client: TestClient):
        response = service_client.get("/service/o/")
        assert response.status_code == 200
        assert response.json() == [
            {
                "name": "Aarhus Universitet",
                "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
                "user_key": "AU",
            }
        ]

    def test_get_organisation(self, service_client: TestClient):
        response = service_client.get(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/"
        )
        assert response.status_code == 200
        assert response.json() == {
            "name": "Aarhus Universitet",
            "uuid": "456362c4-0ee4-4e5e-a72c-751239745e62",
            "user_key": "AU",
            "unit_count": 9,
            "person_count": 4,
            "engagement_count": 3,
            "association_count": 1,
            "leave_count": 1,
            "role_count": 1,
            "manager_count": 1,
            "child_count": 2,
        }

    def test_get_children(self, service_client: TestClient):
        response = service_client.get(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/children",
        )
        assert response.status_code == 200
        assert response.json() == [
            {
                "child_count": 4,
                "name": "Overordnet Enhed",
                "user_key": "root",
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {
                    "from": "2016-01-01",
                    "to": None,
                },
            },
            {
                "child_count": 1,
                "name": "Lønorganisation",
                "user_key": "løn",
                "uuid": "b1f69701-86d8-496e-a3f1-ccef18ac1958",
                "validity": {
                    "from": "2017-01-01",
                    "to": None,
                },
            },
        ]

    def test_get_children_with_counts(self, service_client: TestClient):
        response = service_client.get(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/children",
            params={"count": {"engagement", "association"}},
        )
        assert response.status_code == 200
        assert response.json() == [
            {
                "child_count": 4,
                "association_count": 0,
                "engagement_count": 0,
                "name": "Overordnet Enhed",
                "user_key": "root",
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {
                    "from": "2016-01-01",
                    "to": None,
                },
            },
            {
                "child_count": 1,
                "association_count": 0,
                "engagement_count": 0,
                "name": "Lønorganisation",
                "user_key": "løn",
                "uuid": "b1f69701-86d8-496e-a3f1-ccef18ac1958",
                "validity": {
                    "from": "2017-01-01",
                    "to": None,
                },
            },
        ]

    def test_get_children_with_hierarchy(self, service_client: TestClient):
        response = service_client.get(
            "/service/o/456362c4-0ee4-4e5e-a72c-751239745e62/children",
            params={"org_unit_hierarchy": uuid4()},
        )
        # This was not tested previously and we only use it in Aarhus
        # Unsure whether we acutally have fixture data for this?
        # Tested locally and it works as expected
        # Random UUID gives child count = 0 because no children belong to the
        # hierarchy
        assert response.status_code == 200
        assert response.json() == [
            {
                "child_count": 0,
                "name": "Overordnet Enhed",
                "user_key": "root",
                "uuid": "2874e1dc-85e6-4269-823a-e1125484dfd3",
                "validity": {
                    "from": "2016-01-01",
                    "to": None,
                },
            },
            {
                "child_count": 0,
                "name": "Lønorganisation",
                "user_key": "løn",
                "uuid": "b1f69701-86d8-496e-a3f1-ccef18ac1958",
                "validity": {
                    "from": "2017-01-01",
                    "to": None,
                },
            },
        ]

    def test_get_children_invalid(self, service_client: TestClient):
        # Doesn't exist
        response = service_client.get(
            "/service/o/00000000-0000-0000-0000-000000000000/children"
        )
        assert response.status_code == 404
        # Is an org unit
        response = service_client.get(
            "/service/o/2874e1dc-85e6-4269-823a-e1125484dfd3/children"
        )
        assert response.status_code == 404
