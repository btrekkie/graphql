import unittest

from graphql.scalar_descriptors.strict import GraphQlStrictBooleanDescriptor
from graphql.scalar_descriptors.strict import GraphQlStrictFloatDescriptor
from graphql.scalar_descriptors.strict import GraphQlStrictIdDescriptor
from graphql.scalar_descriptors.strict import GraphQlStrictIntDescriptor
from graphql.scalar_descriptors.strict import GraphQlStrictStringDescriptor


class GraphQlStrictScalarDescriptorsTest(unittest.TestCase):
    """Tests scalar descriptors in graphql.scalar_descriptors.strict."""

    def test_string(self):
        """Test GraphQlStrictStringDescriptor."""
        descriptor = GraphQlStrictStringDescriptor('String')

        # graphql_to_python
        self.assertEqual('foo', descriptor.graphql_to_python('foo'))
        self.assertEqual('', descriptor.graphql_to_python(''))
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(None)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(12)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(True)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(6.2)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(object())

        # python_to_graphql
        self.assertEqual('foo', descriptor.python_to_graphql('foo'))
        self.assertEqual('', descriptor.python_to_graphql(''))
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(None)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(12)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(True)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(6.2)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(object())

    def test_id(self):
        """Test GraphQlStrictIdDescriptor."""
        descriptor = GraphQlStrictIdDescriptor('String')

        # graphql_to_python
        self.assertEqual('foo', descriptor.graphql_to_python('foo'))
        self.assertEqual('', descriptor.graphql_to_python(''))
        self.assertEqual('12', descriptor.graphql_to_python(12))
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(None)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(True)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(6.2)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(object())

        # python_to_graphql
        self.assertEqual('foo', descriptor.python_to_graphql('foo'))
        self.assertEqual('', descriptor.python_to_graphql(''))
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(None)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(12)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(True)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(6.2)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(object())

    def test_int(self):
        """Test GraphQlStrictIntDescriptor."""
        descriptor = GraphQlStrictIntDescriptor('Integer')

        # graphql_to_python
        self.assertEqual(42, descriptor.graphql_to_python(42))
        self.assertEqual(-12, descriptor.graphql_to_python(-12))
        self.assertEqual(0, descriptor.graphql_to_python(0))
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(None)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python('14')
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(2.6)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python('2.6')
        with self.assertRaises(ValueError):
            descriptor.graphql_to_python(123456789012)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(object())

        # python_to_graphql
        self.assertEqual(42, descriptor.python_to_graphql(42))
        self.assertEqual(-12, descriptor.python_to_graphql(-12))
        self.assertEqual(0, descriptor.python_to_graphql(0))
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(None)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql('14')
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(2.6)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql('2.6')
        with self.assertRaises(ValueError):
            descriptor.python_to_graphql(123456789012)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(object())

    def test_float(self):
        """Test GraphQlStrictFloatDescriptor."""
        descriptor = GraphQlStrictFloatDescriptor('Float')

        # graphql_to_python
        self.assertEqual(42, descriptor.graphql_to_python(42))
        self.assertEqual(-12, descriptor.graphql_to_python(-12))
        self.assertEqual(0, descriptor.graphql_to_python(0))
        self.assertTrue(
            descriptor.graphql_to_python(123456789123456789123456789L) in
            (
                123456789123456789123456789L,
                float(123456789123456789123456789L),
            ))
        self.assertEqual(4.3, descriptor.graphql_to_python(4.3))
        self.assertEqual(-15.3, descriptor.graphql_to_python(-15.3))
        self.assertEqual(1.4e28, descriptor.graphql_to_python(1.4e28))
        self.assertEqual(2.6e-8, descriptor.graphql_to_python(2.6e-8))
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(None)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python('14')
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python('6.5')
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python('6.5e-2')
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(object())

        # python_to_graphql
        self.assertEqual(42, descriptor.python_to_graphql(42))
        self.assertEqual(-12, descriptor.python_to_graphql(-12))
        self.assertEqual(0, descriptor.python_to_graphql(0))
        self.assertTrue(
            descriptor.python_to_graphql(123456789123456789123456789L) in
            (
                123456789123456789123456789L,
                float(123456789123456789123456789L),
            ))
        self.assertEqual(4.3, descriptor.python_to_graphql(4.3))
        self.assertEqual(-15.3, descriptor.python_to_graphql(-15.3))
        self.assertEqual(1.4e28, descriptor.python_to_graphql(1.4e28))
        self.assertEqual(2.6e-8, descriptor.python_to_graphql(2.6e-8))
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(None)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql('14')
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql('6.5')
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql('6.5e-2')
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(object())

    def test_boolean(self):
        """Test GraphQlStrictBooleanDescriptor."""
        descriptor = GraphQlStrictBooleanDescriptor('Boolean')

        # graphql_to_python
        self.assertEqual(True, descriptor.graphql_to_python(True))
        self.assertEqual(False, descriptor.graphql_to_python(False))
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(None)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python('12')
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python('true')
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(42)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(object())

        # python_to_graphql
        self.assertEqual(True, descriptor.python_to_graphql(True))
        self.assertEqual(False, descriptor.python_to_graphql(False))
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(None)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql('12')
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql('true')
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(42)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(object())
