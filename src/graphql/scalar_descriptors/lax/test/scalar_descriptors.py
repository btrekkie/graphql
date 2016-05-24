import unittest

from graphql.scalar_descriptors.lax import GraphQlLaxBooleanDescriptor
from graphql.scalar_descriptors.lax import GraphQlLaxFloatDescriptor
from graphql.scalar_descriptors.lax import GraphQlLaxIdDescriptor
from graphql.scalar_descriptors.lax import GraphQlLaxIntDescriptor
from graphql.scalar_descriptors.lax import GraphQlLaxStringDescriptor


class GraphQlLaxScalarDescriptorsTest(unittest.TestCase):
    """Tests scalar descriptors in graphql.scalar_descriptors.lax."""

    def test_string(self):
        """Test GraphQlLaxStringDescriptor."""
        descriptor = GraphQlLaxStringDescriptor('String')

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
        self.assertEqual('None', descriptor.python_to_graphql(None))
        self.assertEqual('12', descriptor.python_to_graphql(12))
        self.assertEqual('True', descriptor.python_to_graphql(True))
        self.assertEqual('6.2', descriptor.python_to_graphql(6.2))

        # Make sure this doesn't raise an exception
        descriptor.python_to_graphql(object())

    def test_id(self):
        """Test GraphQlLaxIdDescriptor."""
        descriptor = GraphQlLaxIdDescriptor('ID')

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
        self.assertEqual('None', descriptor.python_to_graphql(None))
        self.assertEqual('12', descriptor.python_to_graphql(12))
        self.assertEqual('True', descriptor.python_to_graphql(True))
        self.assertEqual('6.2', descriptor.python_to_graphql(6.2))

        # Make sure this doesn't raise an exception
        descriptor.python_to_graphql(object())

    def test_int(self):
        """Test GraphQlLaxIntDescriptor."""
        descriptor = GraphQlLaxIntDescriptor('Integer')

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
        with self.assertRaises(ValueError):
            descriptor.graphql_to_python(123456789012)
        with self.assertRaises(TypeError):
            descriptor.graphql_to_python(object())

        # python_to_graphql
        self.assertEqual(42, descriptor.python_to_graphql(42))
        self.assertEqual(-12, descriptor.python_to_graphql(-12))
        self.assertEqual(0, descriptor.python_to_graphql(0))
        self.assertEqual(14, descriptor.python_to_graphql('14'))
        self.assertEqual(2, descriptor.python_to_graphql(2.6))
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(None)
        with self.assertRaises(ValueError):
            descriptor.python_to_graphql('2.6')
        with self.assertRaises(ValueError):
            descriptor.python_to_graphql(123456789012)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(object())

    def test_float(self):
        """Test GraphQlLaxFloatDescriptor."""
        descriptor = GraphQlLaxFloatDescriptor('Float')

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
        self.assertEqual(14, descriptor.python_to_graphql('14'))
        self.assertEqual(6.5, descriptor.python_to_graphql('6.5'))
        self.assertEqual(0.065, descriptor.python_to_graphql('6.5e-2'))
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(None)
        with self.assertRaises(TypeError):
            descriptor.python_to_graphql(object())

    def test_boolean(self):
        """Test GraphQlLaxBooleanDescriptor."""
        descriptor = GraphQlLaxBooleanDescriptor('Boolean')

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
        self.assertEqual(False, descriptor.python_to_graphql(None))
        self.assertEqual(True, descriptor.python_to_graphql('12'))
        self.assertEqual(True, descriptor.python_to_graphql('true'))
        self.assertEqual(True, descriptor.python_to_graphql(42))
        self.assertEqual(True, descriptor.python_to_graphql(object()))
