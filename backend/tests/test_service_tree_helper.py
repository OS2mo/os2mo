# SPDX-FileCopyrightText: 2017-2021 Magenta ApS
# SPDX-License-Identifier: MPL-2.0

from anytree import Node
from anytree.search import find

from mora.async_util import async_to_sync
from mora.lora import Connector
from mora.service.tree_helper import build_tree_from_org_units, find_nodes
from . import util


class TestBuildTreeFromOrgUnits(util.LoRATestCase):
    """Tests for `mora.service.tree_helper.build_tree_from_org_units`"""

    def setUp(self):
        super().setUp()
        self.load_sample_structures()
        self._connector = Connector(virkningfra="-infinity", virkningtil="infinity")
        self._org_units = async_to_sync(self._connector.organisationenhed.get_all)()

    def test_roots(self):
        roots = build_tree_from_org_units(self._org_units)

        # The sample structure contains two roots ("Overordnet Enhed" and
        # "Lønorganisation".)
        self.assertEqual(len(roots), 2)

        # Each root is an instance of `anytree.Node`
        self.assertTrue(all(isinstance(root, Node) for root in roots))

        # Check node names
        self.assertEqual(roots[0].name, "Overordnet Enhed")
        self.assertEqual(roots[1].name, "Lønorganisation")

    def test_find_leaf_node(self):
        # Test structure of returned tree by checking the lowest leaf node of
        # the first root.
        roots = build_tree_from_org_units(self._org_units)
        leaf = find(roots[0], lambda n: n.name == 'Afdeling for Fortidshistorik')
        self.assertIsInstance(leaf, Node)
        self.assertEqual(leaf.depth, 3)
        self.assertListEqual(
            [a.name for a in leaf.ancestors],
            ['Overordnet Enhed', 'Humanistisk fakultet', 'Historisk Institut'],
        )


class TestFindNodes(util.LoRATestCase):
    """Tests for `mora.service.tree_helper.find_nodes`"""

    def setUp(self):
        super().setUp()
        self.load_sample_structures()
        self._connector = Connector(virkningfra="-infinity", virkningtil="infinity")
        self._org_units = async_to_sync(self._connector.organisationenhed.get_all)()
        self._roots = build_tree_from_org_units(self._org_units)

    def test_matching_predicate(self):
        # The children of the first root look like this:
        #
        # Overordnet Enhed
        # ├──  Social og sundhed
        # ├──  Humanistisk fakultet
        # │   ├──  Filosofisk Institut
        # │   └──  Historisk Institut
        # │       └──  Afdeling for Fortidshistorik
        # ├──  Samfundsvidenskabelige fakultet
        # └──  Skole og Børn
        #
        # Given a predicate that matches 'fortidshistorik', and an anchor that
        # is the ID of 'Humanistisk Fakultet', we want to find the org unit
        # 'Historisk Institut'. This is because we need to show 'Historisk
        # Institut' in the org tree UI, to let the user navigate all the way
        # down to the org unit which actually matches the predicate.
        matches = find_nodes(
            self._roots,
            '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',  # anchor: 'Humanistisk Fakultet'
            lambda node: 'fortidshistorik' in node.name.lower(),  # predicate
        )
        self.assertListEqual([node.name for node in matches], ["Historisk Institut"])

    def test_matching_predicate_immediate(self):
        # Given a predicate that matches a node immediately below the anchor,
        # return the matching node.
        matches = find_nodes(
            self._roots,
            '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',  # anchor: 'Humanistisk Fakultet'
            lambda node: 'historisk institut' in node.name.lower(),  # predicate
        )
        self.assertListEqual([node.name for node in matches], ["Historisk Institut"])

    def test_non_matching_predicate(self):
        # Given a non-matching predicate, return an empty generator.
        empty_gen = find_nodes(
            self._roots,
            '9d07123e-47ac-4a9a-88c8-da82e3a4bc9e',  # anchor: 'Humanistisk Fakultet'
            lambda node: 'nonexistent' in node.name.lower(),  # predicate
        )
        self.assertListEqual(list(empty_gen), [])
