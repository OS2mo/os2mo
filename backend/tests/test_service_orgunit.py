# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import datetime

import freezegun

from mora import util
from mora.service.orgunit import get_lora_dict_current_attr


@freezegun.freeze_time("2023-01-25T00:00:00")
async def test_service_orgunit_edit_lora_attr_filter():
    now = datetime.datetime.now(tz=util.DEFAULT_TIMEZONE).replace(hour=0)
    tomorrow = (now + datetime.timedelta(days=1)).replace(hour=0)

    future_name = "ÅÅ ham-der"
    test_lora_dict_with_attrs = {
        "attributter": {
            "organisationenhedegenskaber": [
                {
                    "brugervendtnoegle": "d30bb56e-2c6a-4867-b6ba-da9e928ef977",
                    "enhedsnavn": future_name,
                    "virkning": {
                        "from": tomorrow.isoformat().replace("T", " "),
                        "to": "infinity",
                        "from_included": True,
                        "to_included": False,
                    },
                },
                {
                    "brugervendtnoegle": "d30bb56e-2c6a-4867-b6ba-da9e928ef977",
                    "enhedsnavn": "ham-der",
                    "virkning": {
                        "from": now.isoformat().replace("T", " "),
                        "to": tomorrow.isoformat().replace("T", " "),
                        "from_included": True,
                        "to_included": False,
                    },
                },
            ]
        }
    }

    current_lora_attr = get_lora_dict_current_attr(
        test_lora_dict_with_attrs, tomorrow, util.POSITIVE_INFINITY
    )
    assert current_lora_attr is not None
    assert current_lora_attr["enhedsnavn"] == future_name
