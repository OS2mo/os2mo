# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import collections
from queue import Empty
from queue import Queue
from uuid import UUID

from ..lora import Scope
from ..mapping import FieldTuple


def queue_iterator(queue):
    """Iterate through a queue without blocking, stop when empty."""

    def stop_iteration_wait():
        try:
            return queue.get(block=False)
        except Empty:
            raise StopIteration

    yield from iter(stop_iteration_wait, None)


async def prepare_ancestor_tree(
    connector_entry: Scope,
    mapping_parent: FieldTuple,
    uuids: list[UUID],
    get_children_args,
    with_siblings=False,
):
    """Return a tree helper structure, bounded by the given uuids.

    Args:
        connector_entry (Connector):
            Lora Connector instance from mora/lora.py.
        mapping_parent (FieldTuple):
            Mapping entry from mora/mapping.py.
        get_children_args (Function):
            Function from (uuid, parent_uuid, cache) --> dict, the dict being
            applied as a filter to the connector_entry.get_all call when fetching
            children of the current uuid.
        with_siblings (bool):
            Add siblings of ancestors to children and cache.

    Returns:
        set, dict(set), dict:
            root_uuids:
                set of root UUIDs, i.e. set of all top-level entries.
            children:
                dict(set) from UUID to set of children UUIDs.
            cache:
                dict from UUID to JSON object.
    """

    # UUID --> Object cache
    # Not really used here, but returned to callers to avoid multiple calls
    cache = {}

    async def get(uuid):
        # Return cached entry if already fetched
        if uuid in cache:
            return cache[uuid]
        # Otherwise go fetch it
        obj = await connector_entry.get(uuid)
        cache[uuid] = obj
        return obj

    async def get_bulk(uuids: list[UUID]):
        objs = dict(await connector_entry.get_all_by_uuid(uuids=uuids))
        cache.update(objs)
        return objs

    async def get_children(uuid, parent_uuid) -> dict:
        children = dict(
            await connector_entry.get_all(**get_children_args(uuid, parent_uuid, cache))
        )
        cache.update(children)
        return children

    async def get_parent(uuid):
        obj = await get(uuid)
        for parent_uuid in mapping_parent.get_uuids(obj):
            return parent_uuid

    # Parent-UUID --> set(Children-UUIDs)
    children = collections.defaultdict(set)

    # set(Root-UUIDs)
    root_uuids = set()

    # Bulk cache for performance
    await get_bulk(uuids)

    # Initialize our queue
    task_queue = Queue()

    async def process_parent(uuid: UUID):
        # Fetch parent, if no parent is found, we must be a root node
        parent_uuid = await get_parent(uuid)
        assert parent_uuid != uuid  # provably ensures we don't loop forever
        if not parent_uuid:
            root_uuids.add(uuid)
            return

        # We do have a parent, so we should process said parent at some point
        task_queue.put(process_parent(parent_uuid))

        # Build parent --> children map
        children[parent_uuid].add(uuid)
        if with_siblings:
            siblings = await get_children(uuid, parent_uuid)
            sibling_uuids = siblings.keys()
            children[parent_uuid].update(sibling_uuids)

    # create tasks in parallel
    for uuid in set(uuids):
        task_queue.put(process_parent(uuid))

    # Loop until queue is exhausted
    for task in queue_iterator(task_queue):
        await task

    return root_uuids, children, cache
