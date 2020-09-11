# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from queue import Queue, Empty
import collections


def queue_iterator(queue):
    """Iterate through a queue without blocking, stop when empty."""
    def stop_iteration_wait():
        try:
            return queue.get(block=False)
        except Empty:
            raise StopIteration
    yield from iter(stop_iteration_wait, None)


def prepare_ancestor_tree(connector_entry, mapping_parent, uuids,
                          get_children_args, with_siblings=False):
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

    def get(uuid):
        # Return cached entry if already fetched
        if uuid in cache:
            return cache[uuid]
        # Otherwise go fetch it
        obj = connector_entry.get(uuid)
        cache[uuid] = obj
        return obj

    def get_bulk(uuids):
        objs = dict(connector_entry.get_all(uuid=uuids))
        cache.update(objs)
        return objs

    def get_children(uuid, parent_uuid):
        children = dict(connector_entry.get_all(
            **get_children_args(uuid, parent_uuid, cache)
        ))
        cache.update(children)
        return children

    def get_parent(uuid):
        obj = get(uuid)
        for parent_uuid in mapping_parent.get_uuids(obj):
            return parent_uuid

    # Parent-UUID --> set(Children-UUIDs)
    children = collections.defaultdict(set)

    # set(Root-UUIDs)
    root_uuids = set()

    # Initialize our queue
    queue = Queue()
    # Bulk cache for performance
    get_bulk(uuids)
    for uuid in set(uuids):
        queue.put(uuid)

    # Loop until queue is exhausted
    for uuid in queue_iterator(queue):
        # Fetch parent, if no parent is found, we must be a root node
        parent_uuid = get_parent(uuid)
        if not parent_uuid:
            root_uuids.add(uuid)
            continue
        # We do have a parent, so we should process said parent at some point
        queue.put(parent_uuid)
        # Build parent --> children map
        children[parent_uuid].add(uuid)
        if with_siblings:
            siblings = get_children(uuid, parent_uuid)
            sibling_uuids = siblings.keys()
            children[parent_uuid].update(sibling_uuids)

    return root_uuids, children, cache
