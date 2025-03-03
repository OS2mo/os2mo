# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from asyncio import gather
from contextlib import suppress
from itertools import starmap
from uuid import UUID

from mora import common
from mora import util
from mora.lora import AutocompleteScope


async def get_results(
    entity: str, class_uuids: list[UUID], query: str
) -> dict[str, list]:  # pragma: no cover
    """Run an autocomplete search query.

    Args:
        entity:
            The entity type to autocomplete.
            One of 'bruger' and 'organisationsenhed'.
        class_uuids:
            List of class UUIDs whose title and value will be displayed for match.
        query:
            The search query string.

    Returns:
        A dictionary with key 'items' and a value that are the matches.
    """
    if not query:
        return {"items": []}

    connector = common.get_connector()
    # Build map of {uuid: class data} so that we can look up each class title later.
    class_uuids = class_uuids or []
    loaded_classes = await gather(*map(connector.klasse.get, class_uuids))
    class_map = dict(zip(class_uuids, loaded_classes))

    # Fetch autocomplete results from LoRa
    scope = AutocompleteScope(connector, entity)
    results = await scope.fetch(
        phrase=util.query_to_search_phrase(query),
        class_uuids=class_uuids,
    )

    def convert_attrs(class_uuid, value):
        title = None
        with suppress((KeyError, TypeError)):
            class_data = class_map[UUID(class_uuid)]
            title = class_data["attributter"]["klasseegenskaber"][0]["titel"]
        return {
            "uuid": class_uuid,
            "value": value,
            "title": title,
        }

    # Convert RowMapping to dict to make it mutable
    results["items"] = [dict(x) for x in results["items"]]

    # Add class title to each attr of each result
    for result in results["items"]:
        attrs = result.get("attrs")
        if attrs is None:
            continue
        result["attrs"] = list(starmap(convert_attrs, attrs))

    return results
