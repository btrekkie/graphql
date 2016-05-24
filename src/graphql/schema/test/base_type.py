import unittest

from graphql.schema import GraphQlInterfaceType


class GraphQlBaseTypeTest(unittest.TestCase):
    def add_child(self, parent, child):
        """Equivalent implementation is contractual.

        GraphQlInterfaceType parent - The parent interface.
        GraphQlType child - The child type.
        """
        parent.add_child_type(child)
        child.add_parent_type(parent)

    def test_is_subtype(self):
        """Test GraphQlBaseType.is_subtype."""
        # 1A   1B   1C
        # | \ / |   |
        # |  X  |   |
        # | / \ |   |
        # 2A   2B   2C
        # | \ / |   /
        # |  X  |  /
        # | / \ | /
        # 3A   3B
        type1a = GraphQlInterfaceType('Type1A', None)
        type1b = GraphQlInterfaceType('Type1B', None)
        type1c = GraphQlInterfaceType('Type1C', None)
        type2a = GraphQlInterfaceType('Type2A', None)
        type2b = GraphQlInterfaceType('Type2B', None)
        type2c = GraphQlInterfaceType('Type2C', None)
        type3a = GraphQlInterfaceType('Type3A', None)
        type3b = GraphQlInterfaceType('Type3B', None)

        self.add_child(type1a, type2a)
        self.add_child(type1a, type2b)
        self.add_child(type1b, type2a)
        self.add_child(type1b, type2b)
        self.add_child(type1c, type2c)
        self.add_child(type2a, type3a)
        self.add_child(type2a, type3b)
        self.add_child(type2b, type3a)
        self.add_child(type2b, type3b)
        self.add_child(type2c, type3b)

        self.assertTrue(type1a.is_subtype(type1a))
        self.assertTrue(type1b.is_subtype(type1b))
        self.assertTrue(type1c.is_subtype(type1c))
        self.assertTrue(type2a.is_subtype(type2a))
        self.assertTrue(type2b.is_subtype(type2b))
        self.assertTrue(type2c.is_subtype(type2c))
        self.assertTrue(type3a.is_subtype(type3a))
        self.assertTrue(type3b.is_subtype(type3b))

        self.assertTrue(type3a.is_subtype(type1a))
        self.assertTrue(type3b.is_subtype(type1a))
        self.assertFalse(type3a.is_subtype(type1c))
        self.assertTrue(type3b.is_subtype(type1c))
        self.assertTrue(type3a.is_subtype(type2a))
        self.assertTrue(type3a.is_subtype(type2b))
        self.assertTrue(type3b.is_subtype(type2a))
        self.assertTrue(type3b.is_subtype(type2b))
        self.assertTrue(type2a.is_subtype(type1a))
        self.assertTrue(type2a.is_subtype(type1b))
        self.assertTrue(type2b.is_subtype(type1a))
        self.assertTrue(type2b.is_subtype(type1b))

        self.assertFalse(type1a.is_subtype(type1b))
        self.assertFalse(type1a.is_subtype(type1c))
        self.assertFalse(type1a.is_subtype(type2a))
        self.assertFalse(type1a.is_subtype(type3a))

    def test_ancestor_types(self):
        """Test GraphQlBaseType.ancestor_types."""
        type1a = GraphQlInterfaceType('Type1A', None)
        type1b = GraphQlInterfaceType('Type1B', None)
        type1c = GraphQlInterfaceType('Type1C', None)
        type2a = GraphQlInterfaceType('Type2A', None)
        type2b = GraphQlInterfaceType('Type2B', None)
        type2c = GraphQlInterfaceType('Type2C', None)
        type3a = GraphQlInterfaceType('Type3A', None)
        type3b = GraphQlInterfaceType('Type3B', None)

        self.add_child(type1a, type2a)
        self.add_child(type1a, type2b)
        self.add_child(type1b, type2a)
        self.add_child(type1b, type2b)
        self.add_child(type1c, type2c)
        self.add_child(type2a, type3a)
        self.add_child(type2a, type3b)
        self.add_child(type2b, type3a)
        self.add_child(type2b, type3b)
        self.add_child(type2c, type3b)

        self.assertEqual([], type1a.ancestor_types())
        self.assertEqual([], type1b.ancestor_types())
        self.assertEqual([], type1c.ancestor_types())
        self.assertEqual(set([type1a, type1b]), set(type2a.ancestor_types()))
        self.assertEqual(set([type1a, type1b]), set(type2b.ancestor_types()))
        self.assertEqual([type1c], type2c.ancestor_types())
        self.assertEqual(
            set([type1a, type1b, type2a, type2b]),
            set(type3a.ancestor_types()))
        self.assertEqual(
            set([type1a, type1b, type1c, type2a, type2b, type2c]),
            set(type3b.ancestor_types()))
