# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from oio_rest.utils import is_uuid

from tests.oio_rest import util
from tests.oio_rest.util import DBTestCase


class TestItSystem(DBTestCase):
    def test_it_system(self) -> None:
        result = self.client.post(
            "lora/organisation/itsystem",
            data={
                "json": util.get_fixture("itsystem_opret.json", as_text=False),
            },
        )
        assert result.status_code == 201
        uuid_ = result.json()["uuid"]
        assert is_uuid(uuid_)
