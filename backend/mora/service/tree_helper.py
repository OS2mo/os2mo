# SPDX-FileCopyrightText: 2019-2020 Magenta ApS
# SPDX-License-Identifier: MPL-2.0
import collections
from asyncio import create_task
from queue import Empty, Queue
from typing import Dict

from anytree import Node
from anytree.search import findall

from ..lora import Scope
from ..mapping import (
    ORG_UNIT_EGENSKABER_FIELD,
    ORG_UNIT_NAME_KEY,
    PARENT_FIELD,
    FieldTuple,
)


def queue_iterator(queue):
    """Iterate through a queue without blocking, stop when empty."""

    def stop_iteration_wait():
        try:
            return queue.get(block=False)
        except Empty:
            raise StopIteration

    yield from iter(stop_iteration_wait, None)


async def prepare_ancestor_tree(connector_entry: Scope, mapping_parent: FieldTuple,
                                uuids, get_children_args, with_siblings=False):
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

    async def get_bulk(uuids):
        objs = dict(await connector_entry.get_all_by_uuid(uuids=uuids))
        cache.update(objs)
        return objs

    async def get_children(uuid, parent_uuid) -> Dict:
        children = dict(await connector_entry.get_all(
            **get_children_args(uuid, parent_uuid, cache)
        ))
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

    async def process_parent(uuid):
        # Fetch parent, if no parent is found, we must be a root node
        parent_uuid = await get_parent(uuid)
        if not parent_uuid:
            root_uuids.add(uuid)
            return

        # We do have a parent, so we should process said parent at some point
        task_queue.put(create_task(process_parent(parent_uuid)))

        # Build parent --> children map
        children[parent_uuid].add(uuid)
        if with_siblings:
            siblings = await get_children(uuid, parent_uuid)
            sibling_uuids = siblings.keys()
            children[parent_uuid].update(sibling_uuids)

    # create tasks in parallel
    for uuid in set(uuids):
        task_queue.put(create_task(process_parent(uuid)))

    # Loop until queue is exhausted
    for task in queue_iterator(task_queue):
        await task

    return root_uuids, children, cache


def build_tree_from_org_units(org_units):
    """Return a list of tree roots in the list `org_units`"""

    # Convert an item in the LoRa JSON response to a `Node` instance
    def node(id, ou):
        parentid = PARENT_FIELD.get_uuid(ou)
        attrs = ORG_UNIT_EGENSKABER_FIELD.get(ou)
        name = attrs[0][ORG_UNIT_NAME_KEY]
        return Node(name=name, id=id, pid=parentid, obj=ou)

    nodes = {id: node(id, ou) for id, ou in org_units}
    roots = []

    for node in nodes.values():
        if (node.pid is None) or (node.pid not in nodes):
            # This node has no parent, or has an unknown parent ID.
            # Add it to the list of tree roots.
            roots.append(node)
        else:
            # This node has a parent. Add this node as child of parent.
            parent = nodes[node.pid]
            node.parent = parent

    return roots


def find_nodes(roots, anchor, predicate):
    for root in roots:
        # Find nodes matching predicate
        for match in findall(root, predicate):
            # Find the nodes which are immediate children of `anchor` and also
            # match the predicate.
            for parent in match.ancestors:
                if parent.pid == anchor:
                    yield parent
            # Yield matching node itself
            if match.pid == anchor:
                yield match
