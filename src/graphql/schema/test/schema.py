import unittest

from graphql.schema import GraphQlEnumType
from graphql.schema import GraphQlInputObjectType
from graphql.schema import GraphQlInterfaceType
from graphql.schema import GraphQlObjectType
from graphql.schema import GraphQlScalarType
from graphql.schema import GraphQlSchema
from graphql.schema import GraphQlSchemaFactory
from graphql.schema import GraphQlUnionType


class GraphQlSchemaTest(unittest.TestCase):
    def _assert_field_descriptors_equal(
            self, field_descriptor1, field_descriptor2):
        """Assert that the specified GraphQlFieldDescriptors are the same."""
        self.assertEqual(field_descriptor1.name, field_descriptor2.name)
        self.assertEqual(
            field_descriptor1.description, field_descriptor2.description)
        self.assertEqual(
            field_descriptor1.is_deprecated, field_descriptor2.is_deprecated)
        self.assertEqual(
            field_descriptor1.deprecation_reason,
            field_descriptor2.deprecation_reason)
        self.assertEqual(
            field_descriptor1.field_type.type_str(),
            field_descriptor2.field_type.type_str())
        self.assertEqual(
            set(field_descriptor1.args.iterkeys()),
            set(field_descriptor2.args.iterkeys()))
        for name, t in field_descriptor1.args.iteritems():
            self.assertEqual(
                t.type_str(), field_descriptor2.args[name].type_str())

    def _assert_fields_equal(self, field1, field2):
        """Assert that the specified GraphQlFields are the same."""
        self._assert_field_descriptors_equal(
            field1.descriptor, field2.descriptor)
        self.assertEqual(field1.method_name, field2.method_name)
        self.assertEqual(field1.partial_args, field2.partial_args)
        self.assertEqual(field1.partial_kwargs, field2.partial_kwargs)
        if field1.context_args is None:
            self.assertIsNone(field2.context_args)
        else:
            self.assertEqual(
                set(field1.context_args), set(field2.context_args))
        self.assertEqual(field1.attr, field2.attr)

    def _assert_parent_types_equal(self, type1, type2):
        """Assert that type1.parent_types and type2.parent_types are the same.

        GraphQlBaseType type1 - The first type.
        GraphQlBaseType type2 - The second type.
        """
        parent_names1 = set([t.name for t in type1.parent_types])
        parent_names2 = set([t.name for t in type1.parent_types])
        self.assertEqual(parent_names1, parent_names2)

    def _assert_object_types_equal(self, type1, type2):
        """Assert that the specified GraphQlObjectTypes are the same."""
        self.assertEqual(type1.name, type2.name)
        self.assertEqual(type1.description, type2.description)
        self._assert_parent_types_equal(type1, type2)
        self.assertEqual(type1.class_descriptor, type2.class_descriptor)
        self.assertEqual(
            set(type1.fields.iterkeys()), set(type2.fields.iterkeys()))
        for name, field1 in type1.fields.iteritems():
            field2 = type2.fields[name]
            self._assert_fields_equal(field1, field2)

    def _assert_interface_types_equal(self, type1, type2):
        """Assert that the specified GraphQlInterfaceTypes are the same."""
        self.assertEqual(type1.name, type2.name)
        self.assertEqual(type1.description, type2.description)
        self._assert_parent_types_equal(type1, type2)
        self.assertEqual(
            set(type1.field_descriptors.iterkeys()),
            set(type2.field_descriptors.iterkeys()))
        for name, field_descriptor1 in type1.field_descriptors.iteritems():
            field_descriptor2 = type2.field_descriptors[name]
            self._assert_field_descriptors_equal(
                field_descriptor1, field_descriptor2)

    def _assert_union_types_equal(self, type1, type2):
        """Assert that the specified GraphQlUnionTypes are the same."""
        self.assertEqual(type1.name, type2.name)
        self.assertEqual(type1.description, type2.description)
        self._assert_parent_types_equal(type1, type2)

    def _assert_scalar_types_equal(self, type1, type2):
        """Assert that the specified GraphQlScalarTypes are the same."""
        self.assertEqual(type1.name, type2.name)
        self.assertEqual(type1.description, type2.description)
        self.assertEqual(
            type1.scalar_descriptor_class_descriptor,
            type2.scalar_descriptor_class_descriptor)

    def _assert_input_object_types_equal(self, type1, type2):
        """Assert that the specified GraphQlInputObjectTypes are the same."""
        self.assertEqual(type1.name, type2.name)
        self.assertEqual(type1.description, type2.description)
        self.assertEqual(
            set(type1.fields.iterkeys()), set(type2.fields.iterkeys()))
        for name, t in type1.fields.iteritems():
            self.assertEqual(t.type_str(), type2.fields[name].type_str())

    def _assert_enum_types_equal(self, type1, type2):
        """Assert that the specified GraphQlEnumTypes are the same."""
        self.assertEqual(type1.name, type2.name)
        self.assertEqual(type1.description, type2.description)
        self.assertEqual(type1.func_descriptor, type2.func_descriptor)

    def _assert_schemas_equal(self, schema1, schema2):
        """Assert that the specified GraphQlSchemas are the same."""
        self.assertEqual(
            set(schema1._base_types.iterkeys()),
            set(schema2._base_types.iterkeys()))
        for name, type1 in schema1._base_types.iteritems():
            type2 = schema2._base_types[name]
            if isinstance(type1, GraphQlObjectType):
                self.assertIsInstance(type2, GraphQlObjectType)
                self._assert_object_types_equal(type1, type2)
            elif isinstance(type1, GraphQlInterfaceType):
                self.assertIsInstance(type2, GraphQlInterfaceType)
                self._assert_interface_types_equal(type1, type2)
            elif isinstance(type1, GraphQlUnionType):
                self.assertIsInstance(type2, GraphQlUnionType)
                self._assert_union_types_equal(type1, type2)
            elif isinstance(type1, GraphQlScalarType):
                self.assertIsInstance(type2, GraphQlScalarType)
                self._assert_scalar_types_equal(type1, type2)
            elif isinstance(type1, GraphQlInputObjectType):
                self.assertIsInstance(type2, GraphQlInputObjectType)
                self._assert_input_object_types_equal(type1, type2)
            elif isinstance(type1, GraphQlEnumType):
                self.assertIsInstance(type2, GraphQlEnumType)
                self._assert_enum_types_equal(type1, type2)
            else:
                raise RuntimeError(
                    'Unhandled GraphQlType subclass {:s}'.format(
                        type1.__class__.__name__))

    def test_json(self):
        """Test to_json() and create_from_json."""
        schema1 = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.scalar_descriptors.strict'])
        schema2 = GraphQlSchema.create_from_json(schema1.to_json())
        self._assert_schemas_equal(schema1, schema2)
        schema1 = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.executor.test.star_wars_extra',
            'graphql.scalar_descriptors.strict'])
        schema2 = GraphQlSchema.create_from_json(schema1.to_json())
        self._assert_schemas_equal(schema1, schema2)
