# SPDX-FileCopyrightText: 2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
from .. import common
from .. import util
from ..lora import AutocompleteScope


async def get_results(entity, class_uuids, query):
    connector = common.get_connector()
    if query:
        # Build map of {uuid: class data} so that we can look up each class
        # title later.
        class_uuids = class_uuids or []
        class_map = {
            str(class_uuid): await connector.klasse.get(class_uuid)
            for class_uuid in class_uuids
        }

        # Fetch autocomplete results from LoRa
        scope = AutocompleteScope(connector, entity)
        results = await scope.fetch(
            phrase=util.query_to_search_phrase(query),
            class_uuids=class_uuids,
        )

        # Add class title to each attr of each result
        for result in results["items"]:
            attrs = result.get("attrs") or []
            for idx, attr in enumerate(attrs):
                class_uuid = attr[0]
                out = {"uuid": class_uuid, "value": attr[1]}
                try:
                    class_data = class_map[class_uuid]
                    out["title"] = class_data["attributter"]["klasseegenskaber"][0][
                        "titel"
                    ]
                except (KeyError, TypeError):
                    out["title"] = None
                attrs[idx] = out

        return results

    return {"items": []}
