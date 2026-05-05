# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import uuid

from oio_rest.utils import is_uuid

from tests.oio_rest import util
from tests.oio_rest.util import DBTestCase


class Test21660PutUpdate(DBTestCase):
    def test_21660(self):
        result = self.client.post(
            "lora/klassifikation/facet",
            data={
                "json": util.get_fixture("facet_opret.json", as_text=False),
            },
        )
        assert result.status_code == 201
        uuid_ = result.json()["uuid"]
        assert is_uuid(uuid_)

        result_put = self.client.put(
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture(
                    "facet_reduce_effective_time_21660.json",
                    as_text=False,
                ),
            },
        )
        assert result_put.status_code == 200
        assert result_put.json()["uuid"] == uuid_


class TestKlasse(DBTestCase):
    def test_klasse(self):
        result = self.client.post(
            "lora/klassifikation/klasse",
            data={
                "json": util.get_fixture("klasse_opret.json", as_text=False),
            },
        )
        assert result.status_code == 201
        uuid_ = result.json()["uuid"]
        assert is_uuid(uuid_)

        result_patch = self.client.patch(
            "lora/klassifikation/klasse/%s" % uuid_,
            data={
                "json": util.get_fixture("klasse_opdater.json", as_text=False),
            },
        )
        assert result_patch.status_code == 200
        assert result_patch.json()["uuid"] == uuid_


class TestImportDeletedPassivated(DBTestCase):
    def test_import_delete_passivated(self):
        result = self.client.post(
            "lora/klassifikation/facet",
            data={
                "json": util.get_fixture("facet_opret.json", as_text=False),
            },
        )
        assert result.status_code == 201
        uuid_ = result.json()["uuid"]
        assert is_uuid(uuid_)

        # Passivate object
        result_patch = self.client.patch(
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_passiv.json", as_text=False),
            },
        )
        assert result_patch.status_code == 200
        assert result_patch.json()["uuid"] == uuid_

        # Import object
        result_put = self.client.put(
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_opret.json", as_text=False),
            },
        )
        assert result_put.status_code == 200
        assert result_put.json()["uuid"] == uuid_

        # Delete object
        result_delete = self.client.request(
            "DELETE",
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_slet.json", as_text=False),
            },
        )
        assert result_delete.status_code == 202
        assert result_delete.json()["uuid"] == uuid_

        # Import object
        result_import = self.client.put(
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_opret.json", as_text=False),
            },
        )
        assert result_import.status_code == 200
        assert result_import.json()["uuid"] == uuid_


class TestFacet(DBTestCase):
    def test_facet(self):
        result = self.client.post(
            "lora/klassifikation/facet",
            data={
                "json": util.get_fixture("facet_opret.json", as_text=False),
            },
        )
        assert result.status_code == 201
        uuid_ = result.json()["uuid"]
        assert is_uuid(uuid_)

        import_uuid = str(uuid.uuid4())
        # Import new facet
        result_import = self.client.put(
            "lora/klassifikation/facet/%s" % import_uuid,
            data={
                "json": util.get_fixture("facet_opret.json", as_text=False),
            },
        )
        assert result_import.status_code == 200
        assert result_import.json()["uuid"] == import_uuid

        # Update facet
        result_patch = self.client.patch(
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_opdater.json", as_text=False),
            },
        )
        assert result_patch.status_code == 200
        assert result_patch.json()["uuid"] == uuid_

        # Replace the facet content with old ones
        result_put = self.client.put(
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_opret.json", as_text=False),
            },
        )
        assert result_put.status_code == 200
        assert result_put.json()["uuid"] == uuid_

        # Passivate facet
        result_patch = self.client.patch(
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_passiv.json", as_text=False),
            },
        )
        assert result_patch.status_code == 200
        assert result_patch.json()["uuid"] == uuid_

        # Delete facet
        result_delete = self.client.request(
            "DELETE",
            "lora/klassifikation/facet/%s" % uuid_,
            data={
                "json": util.get_fixture("facet_slet.json", as_text=False),
            },
        )
        assert result_delete.status_code == 202
        assert result_delete.json()["uuid"] == uuid_
