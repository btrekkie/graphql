import inspect
import re

from class_descriptor import GraphQlClassDescriptor
from directive_location import GraphQlDirectiveLocation
from directive_type import GraphQlDirectiveType
from enum_type import GraphQlEnumType
from field import GraphQlField
from field_descriptor import GraphQlFieldDescriptor
from func_descriptor import GraphQlFuncDescriptor
from graphql import graphql_field
from graphql import graphql_object
from input_object_type import GraphQlInputObjectType
from interface_type import GraphQlInterfaceType
from list_type import GraphQlListType
from non_null_type import GraphQlNonNullType
from object_type import GraphQlObjectType
from scalar_type import GraphQlScalarType
from union_type import GraphQlUnionType


@graphql_object(
    '__Schema',
    'A GraphQL schema, describing all GraphQL types, fields, etc. that a '
    'GraphQL document may reference')
class GraphQlSchema(object):
    """A GraphQL schema: all GraphQL types, fields, etc.

    A GraphQL schema, describing all GraphQL types, fields, etc. that a
    GraphQL document may reference.  See GraphQlSchemaFactory.
    """

    # The default name of the GraphQL type of the root mutation object.
    _DEFAULT_MUTATION_TYPE_NAME = 'Mutation'

    # The default name of the GraphQL type of the root query object.
    _DEFAULT_QUERY_TYPE_NAME = 'Query'

    # An integer indicating the current version of the format used in to_json()
    # and create_from_json.  If we change the format, we should increment
    # _VERSION, so that we know to ignore any serializations created with an
    # older _VERSION value.
    _VERSION = 11

    # Private attributes:
    # dict<basestring, GraphQlBaseType> _base_types - A map from the name of
    #     each base type to the type.
    # dict<GraphQlClassDescriptor, GraphQlObjectType>
    #     _class_descriptor_to_object_types - A map from the class descriptor
    #     of each object type to the type.
    # dict<basestring, GraphQlFieldDescriptor> _common_field_descriptors - A
    #     map from the name of each field common to all objects to its
    #     GraphQlFieldDescriptor.  For example, the "__typename" field is
    #     common to all objects.
    # dict<basestring, GraphQlDirectiveType> _directives - A map from the name
    #     of each directive type to the type.
    # dict<basestring, GraphQlFieldDescriptor> _implicit_root_field_descriptors
    #     - A map from the name of each field in the root query object that
    #     does not appear in __Type{fields} to its GraphQlFieldDescriptor.  For
    #     example, the "__schema" field is implicit.
    # basestring _mutation_type_name - The name of the GraphQL type of the root
    #     mutation object, if any.
    # basestring _query_type_name - The name of the GraphQL type of the root
    #     query object.

    def __init__(
            self, base_types, query_type_name=_DEFAULT_QUERY_TYPE_NAME,
            mutation_type_name=_DEFAULT_MUTATION_TYPE_NAME):
        self._base_types = base_types
        self._query_type_name = query_type_name
        self._mutation_type_name = mutation_type_name

        # Check for the root query and mutation types
        if query_type_name not in self._base_types:
            raise ValueError(
                'The root query type {:s} is not defined'.format(
                    query_type_name))
        if (not isinstance(
                self._base_types[query_type_name], GraphQlObjectType)):
            raise ValueError(
                'The root query type {:s} is not an object type'.format(
                    query_type_name))
        if mutation_type_name is not None:
            if mutation_type_name not in self._base_types:
                raise ValueError(
                    'The root mutation type {:s} is not defined'.format(
                        mutation_type_name))
            if (not isinstance(
                    self._base_types[mutation_type_name], GraphQlObjectType)):
                raise ValueError(
                    'The root mutation type {:s} is not an object type'.format(
                        mutation_type_name))

        # Check for built-in scalar types
        for name in ['Boolean', 'Float', 'ID', 'Int', 'String']:
            if name not in base_types:
                raise ValueError(
                    'Missing the built-in scalar type {:s}.  To use the '
                    'standard implementations of the built-in scalar types, '
                    "pass 'graphql.scalar_descriptors.strict' or "
                    "'graphql.scalar_descriptors.lax' to "
                    'GraphQLSchemaFactory.create_from_modules when creating '
                    'the schema.'.format(name))
            if not isinstance(base_types[name], GraphQlScalarType):
                raise ValueError('{:s} must be a scalar type'.format(name))

        # Compute _common_field_descriptors
        non_null_str_type = GraphQlNonNullType(base_types['String'])
        self._common_field_descriptors = {
            '__typename': GraphQlFieldDescriptor(
                '__typename', non_null_str_type, {},
                'The GraphQL type name of the object', False, None),
        }

        # Compute _implicit_root_field_descriptors
        if '__Schema' not in base_types or '__Type' not in base_types:
            raise ValueError(
                'The built-in types __Schema and / or __Type are not defined')
        implicit_root_field_descriptors = [
            GraphQlFieldDescriptor(
                '__schema', GraphQlNonNullType(base_types['__Schema']), {},
                'The GraphQL schema for the document', False, None),
            GraphQlFieldDescriptor(
                '__type', base_types['__Type'], {'name': non_null_str_type},
                'The GraphQL type with the specified name, if any', False,
                None)]
        self._implicit_root_field_descriptors = {}
        for field_descriptor in implicit_root_field_descriptors:
            self._implicit_root_field_descriptors[field_descriptor.name] = (
                field_descriptor)

        # Make sure no type declares a common field
        for t in base_types.itervalues():
            if isinstance(t, GraphQlInterfaceType):
                field_names = set(t.field_descriptors.keys())
            elif isinstance(t, GraphQlObjectType):
                field_names = set(t.fields.keys())
            else:
                continue
            for common_field_name in self._common_field_descriptors.iterkeys():
                if common_field_name in field_names:
                    raise ValueError(
                        'The {:s} type may not declare a field named {:s}, '
                        'because this is a reserved field common to all '
                        'object types.'.format(t.name, common_field_name))

        # Compute _class_descriptor_to_object_type
        self._class_descriptor_to_object_type = {}
        for t in base_types.itervalues():
            if isinstance(t, GraphQlObjectType):
                self._class_descriptor_to_object_type[t.class_descriptor] = t

        # Compute _directives
        non_null_bool_type = GraphQlNonNullType(base_types['Boolean'])
        directives = []
        directives.append(
            GraphQlDirectiveType(
                'include', {'if': non_null_bool_type}, set([
                    GraphQlDirectiveLocation.field,
                    GraphQlDirectiveLocation.fragment_definition,
                    GraphQlDirectiveLocation.fragment_spread,
                    GraphQlDirectiveLocation.inline_fragment]),
                'Causes us to only include the associated fields if the '
                'condition is true'))
        directives.append(
            GraphQlDirectiveType(
                'skip', {'if': non_null_bool_type}, set([
                    GraphQlDirectiveLocation.field,
                    GraphQlDirectiveLocation.fragment_definition,
                    GraphQlDirectiveLocation.fragment_spread,
                    GraphQlDirectiveLocation.inline_fragment]),
                'Causes us to omit the associated fields if the condition is '
                'true'))
        self._directives = {}
        for directive in directives:
            self._directives[directive.name] = directive

    @staticmethod
    def is_valid_identifier(identifier):
        """Return whether the specified string is a valid GraphQL identifier.

        Return whether the specified string is a valid identifier for a
        GraphQL type, field name, etc.
        """
        return re.search('^[_A-Za-z][_0-9A-Za-z]*$', identifier) is not None

    def _field_descriptor_json(self, field_descriptor):
        """Return the JSON representation of the specified field descriptor.

        Return the JSON representation that to_json() uses for the
        specified GraphQlFieldDescriptor.
        """
        arg_types_json = {}
        for arg_name, arg_type in field_descriptor.args.iteritems():
            arg_types_json[arg_name] = arg_type.type_str()
        return {
            'argTypes': arg_types_json,
            'deprecationReason': field_descriptor.deprecation_reason,
            'description': field_descriptor.description,
            'fieldType': field_descriptor.field_type.type_str(),
            'isDeprecated': field_descriptor.is_deprecated,
            'name': field_descriptor.name,
        }

    def _field_json(self, field):
        """Return the JSON representation of the specified field.

        Return the JSON representation that to_json() uses for the
        specified GraphQlField.
        """
        field_json = {}
        field_json.update(self._field_descriptor_json(field.descriptor))
        if field.attr is not None:
            field_json['attr'] = field.attr
        else:
            field_json['contextArgs'] = list(sorted(field.context_args))
            field_json['method'] = field.method_name
            if field.partial_args or field.partial_kwargs:
                field_json['partialArgs'] = field.partial_args
                field_json['partialKwargs'] = field.partial_kwargs
        return field_json

    def to_json(self):
        """Return a JSON value representation of this.

        We may reconstruct the GraphQlSchema later using
        create_from_json, provided we call it before the serialization
        format changes.
        """
        # Compute types JSON
        objects_json = []
        interfaces_json = []
        unions_json = []
        enums_json = []
        scalars_json = []
        input_objects_json = []
        for t in self._base_types.itervalues():
            parents_json = []
            for parent in t.parent_types:
                parents_json.append(parent.name)
            parents_json = sorted(parents_json)

            if isinstance(t, GraphQlObjectType):
                fields_json = []
                field_names = sorted(t.fields.keys())
                for field_name in field_names:
                    fields_json.append(self._field_json(t.fields[field_name]))
                objects_json.append({
                    'class': t.class_descriptor.class_name,
                    'description': t.description,
                    'fields': fields_json,
                    'module': t.class_descriptor.module_name,
                    'name': t.name,
                    'parents': parents_json,
                })
            elif isinstance(t, GraphQlInterfaceType):
                field_descriptors_json = []
                field_names = sorted(t.field_descriptors.keys())
                for field_name in field_names:
                    field_descriptors_json.append(
                        self._field_descriptor_json(
                            t.field_descriptors[field_name]))
                interfaces_json.append({
                    'description': t.description,
                    'fields': field_descriptors_json,
                    'name': t.name,
                    'parents': parents_json,
                })
            elif isinstance(t, GraphQlUnionType):
                unions_json.append({
                    'description': t.description,
                    'name': t.name,
                    'parents': parents_json,
                })
            elif isinstance(t, GraphQlEnumType):
                enums_json.append({
                    'class': t.func_descriptor.class_name,
                    'description': t.description,
                    'func': t.func_descriptor.func_name,
                    'module': t.func_descriptor.module_name,
                    'name': t.name,
                })
            elif isinstance(t, GraphQlScalarType):
                scalars_json.append({
                    'class': t.scalar_descriptor_class_descriptor.class_name,
                    'description': t.description,
                    'module': t.scalar_descriptor_class_descriptor.module_name,
                    'name': t.name,
                })
            elif isinstance(t, GraphQlInputObjectType):
                fields = {}
                for field_name, field_type in t.fields.iteritems():
                    fields[field_name] = field_type.type_str()
                input_objects_json.append({
                    'description': t.description,
                    'fields': fields,
                    'name': t.name,
                })
            else:
                raise RuntimeError(
                    'Unknown type {:s}'.format(t.__class__.__name__))

        # Compute result JSON.  Sort the types so that the resulting JSON looks
        # nicer.
        objects_json = sorted(
            objects_json, key=lambda object_type: object_type['name'])
        interfaces_json = sorted(
            interfaces_json, key=lambda interface_json: interface_json['name'])
        unions_json = sorted(
            unions_json, key=lambda union_type: union_type['name'])
        enums_json = sorted(
            enums_json, key=lambda enum_json: enum_json['name'])
        scalars_json = sorted(
            scalars_json, key=lambda scalar_json: scalar_json['name'])
        input_objects_json = sorted(
            input_objects_json,
            key=lambda input_object_json: input_object_json['name'])
        return {
            'enums': enums_json,
            'inputObjects': input_objects_json,
            'interfaces': interfaces_json,
            'mutationType': self._mutation_type_name,
            'objects': objects_json,
            'queryType': self._query_type_name,
            'scalars': scalars_json,
            'unions': unions_json,
            'version': GraphQlSchema._VERSION,
        }

    @staticmethod
    def parse_type(
            type_str, base_types, require_input_type, require_output_type,
            source):
        """Return the GraphQlType for the specified GraphQL type string.

        Raise a ValueError if it is not a valid type string.

        basestring type_str - The GraphQL type string.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        bool require_input_type - Whether to raise a ValueError if the
            type is not an input type.
        bool require_output_type - Whether to raise a ValueError if the
            type is not an output type, i.e. the base type is
            GraphQlInputObjectType.
        basestring source - A string indicating what this is the type
            of, e.g. 'the foo argument to Bar{baz}'.  We only use this
            for exception messages.
        return GraphQlType - The type.
        """
        # Parse the list and non-null modifiers
        start = 0
        end = len(type_str) - 1
        modifiers = []
        while start <= end and (type_str[end] == '!' or type_str[end] == ']'):
            if type_str[end] == '!':
                modifiers.append('!')
                end -= 1
                if start <= end and type_str[end] == '!':
                    raise ValueError(
                        'The type of {:s} is invalid, because it has multiple '
                        'consecutive exclamation marks'.format(source))
            elif not type_str[start] == '[':
                raise ValueError(
                    'The type of {:s} is invalid, because it has mismatched '
                    'brackets'.format(source))
            else:
                modifiers.append('[]')
                start += 1
                end -= 1

        # Validate the base type
        base_type_str = type_str[start:end + 1]
        if (not base_type_str or '!' in base_type_str or
                '[' in base_type_str or ']' in base_type_str):
            raise ValueError(
                'Parse error in the type of {:s}'.format(source))
        if base_type_str not in base_types:
            raise ValueError(
                'The base type {:s} of {:s} is invalid, because it not a real '
                'type'.format(base_type_str, source))
        t = base_types[base_type_str]
        if (require_input_type and
                not isinstance(
                    t, (
                        GraphQlEnumType,
                        GraphQlInputObjectType,
                        GraphQlScalarType))):
            raise ValueError('{:s} is not an input type'.format(source))
        if (require_output_type and isinstance(t, GraphQlInputObjectType)):
            raise ValueError(
                '{:s} may not be an input object type'.format(source))

        # Compute the type
        for modifier in reversed(modifiers):
            if modifier == '[]':
                t = GraphQlListType(t)
            else:
                t = GraphQlNonNullType(t)
        return t

    @staticmethod
    def _field_descriptor_from_json(
            field_or_field_descriptor_json, type_name, base_types):
        """Return the GraphQlFieldDescriptor represented by the specified JSON.

        Return the GraphQlFieldDescriptor object for the specified JSON value
        representation produced in _field_json or _field_descriptor_json.

        object field_or_field_descriptor_json - The JSON value.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        return GraphQlFieldDescriptor - The field descriptor.
        """
        field_name = field_or_field_descriptor_json['name']
        field_type = GraphQlSchema.parse_type(
            field_or_field_descriptor_json['fieldType'], base_types, False,
            True, 'the field {:s}{{{:s}}}'.format(type_name, field_name))
        arg_types = {}
        for arg_name, arg_type_str in (
                field_or_field_descriptor_json['argTypes'].iteritems()):
            arg_types[arg_name] = GraphQlSchema.parse_type(
                arg_type_str, base_types, True, False,
                'the {:s} argument to the field {:s}{{{:s}}}'.format(
                    arg_name, type_name, field_name))
        return GraphQlFieldDescriptor(
            field_name, field_type, arg_types,
            field_or_field_descriptor_json['description'],
            field_or_field_descriptor_json['isDeprecated'],
            field_or_field_descriptor_json['deprecationReason'])

    @staticmethod
    def _field_from_json(field_json, type_name, base_types):
        """Return the GraphQlField represented by the specified JSON.

        Return the GraphQlField object for the specified JSON value
        representation produced in _field_json.

        object field_json - The JSON value.
        dict<basestring, GraphQlBaseType> base_types - A map from the
            name of each base type to the type.
        return GraphQlField - The field.
        """
        field_descriptor = GraphQlSchema._field_descriptor_from_json(
            field_json, type_name, base_types)
        if 'attr' in field_json:
            return GraphQlField.create_from_attr(
                field_descriptor, field_json['attr'])
        else:
            if 'partialArgs' in field_json:
                partial_args = tuple(field_json['partialArgs'])
                partial_kwargs = field_json['partialKwargs']
            else:
                partial_args = ()
                partial_kwargs = {}
            return GraphQlField.create_from_method(
                field_descriptor, field_json['method'],
                partial_args, partial_kwargs, field_json['contextArgs'])

    @staticmethod
    def create_from_json(json):
        """Return the GraphQlSchema represented by the specified JSON value.

        Return the GraphQlSchema object for the specified JSON value
        representation produced in to_json().  Raise a ValueError if we
        determine that "json" is not a return value of to_json() or is a
        return value from a previous serialization format.

        object json - The JSON value.
        return GraphQlSchema - The schema.
        """
        if json['version'] != GraphQlSchema._VERSION:
            raise ValueError(
                'The JSON value is not from a compatible implementation of '
                'GraphQlSchema.  Try generating the GraphQL schema again.')

        # Create the GraphQlBaseType objects
        base_types = {}
        interface_types = {}
        for scalar_json in json['scalars']:
            name = scalar_json['name']
            if name in base_types:
                raise ValueError('Duplicate type {:s}'.format(name))
            scalar_descriptor_class_descriptor = GraphQlClassDescriptor(
                scalar_json['module'], scalar_json['class'])
            scalar_type = GraphQlScalarType(
                name, scalar_json['description'],
                scalar_descriptor_class_descriptor)
            base_types[name] = scalar_type
        for object_json in json['objects']:
            name = object_json['name']
            if name in base_types:
                raise ValueError('Duplicate type {:s}'.format(name))
            class_descriptor = GraphQlClassDescriptor(
                object_json['module'], object_json['class'])
            base_types[name] = GraphQlObjectType(
                name, object_json['description'], class_descriptor)
        for interface_json in json['interfaces']:
            name = interface_json['name']
            if name in base_types:
                raise ValueError('Duplicate type {:s}'.format(name))
            interface_type = GraphQlInterfaceType(
                name, interface_json['description'])
            base_types[name] = interface_type
            interface_types[name] = interface_type
        for union_json in json['unions']:
            name = union_json['name']
            if name in base_types:
                raise ValueError('Duplicate type {:s}'.format(name))
            base_types[name] = GraphQlUnionType(
                name, union_json['description'])
        for enum_json in json['enums']:
            name = enum_json['name']
            if name in base_types:
                raise ValueError('Duplicate type {:s}'.format(name))
            base_types[name] = GraphQlEnumType(
                name, enum_json['description'], GraphQlFuncDescriptor(
                    enum_json['module'], enum_json['class'],
                    enum_json['func']))
        for input_object_json in json['inputObjects']:
            name = input_object_json['name']
            if name in base_types:
                raise ValueError('Duplicate type {:s}'.format(name))
            base_types[name] = GraphQlInputObjectType(
                name, input_object_json['description'])

        # Compute parent-child relationships
        for type_json in json['objects'] + json['interfaces'] + json['unions']:
            t = base_types[type_json['name']]
            for parent in type_json['parents']:
                t.add_parent_type(base_types[parent])
                base_types[parent].add_child_type(t)

        # Create the GraphQlFieldDescriptors and GraphQlFields, and reference
        # them in the appropriate type objects
        for object_json in json['objects']:
            t = base_types[object_json['name']]
            for field_json in object_json['fields']:
                field = GraphQlSchema._field_from_json(
                    field_json, t.name, base_types)
                t.add_field(field)
        for interface_json in json['interfaces']:
            t = base_types[interface_json['name']]
            for field_descriptor_json in interface_json['fields']:
                field_descriptor = GraphQlSchema._field_descriptor_from_json(
                    field_descriptor_json, t.name, base_types)
                t.add_field_descriptor(field_descriptor)

        # Add the GraphQlInputObject fields
        for input_object_json in json['inputObjects']:
            name = input_object_json['name']
            input_object_type = base_types[name]
            for field_name, field_type_str in (
                    input_object_json['fields'].iteritems()):
                field_type = GraphQlSchema.parse_type(
                    field_type_str, base_types, True, False,
                    'the field {:s}.{:s}'.format(name, field_name))
                input_object_type.add_field(field_name, field_type)

        return GraphQlSchema(
            base_types, json['queryType'], json['mutationType'])

    def get_type(self, type_str):
        """Return the GraphQlType for the specified GraphQL type string.

        Raise a ValueError if it is not a valid type string.
        """
        return GraphQlSchema.parse_type(
            type_str, self._base_types, False, False, 'a document element')

    def do_base_types_intersect(self, type1, type2):
        """Return whether the specified GraphQlBaseTypes intersect.

        They intersect if there is at least one object type that is a
        subtype of both, as in GraphQlType.is_subtype.
        """
        if not isinstance(type1, (GraphQlInterfaceType, GraphQlUnionType)):
            return type1.is_subtype(type2)
        elif not isinstance(type2, (GraphQlInterfaceType, GraphQlUnionType)):
            return type2.is_subtype(type1)
        else:
            concrete_types1 = list([
                leaf_type for leaf_type in type1.leaf_types()
                if isinstance(leaf_type, GraphQlObjectType)])
            concrete_types2 = list([
                leaf_type for leaf_type in type2.leaf_types()
                if isinstance(leaf_type, GraphQlObjectType)])
            return not set(concrete_types1).isdisjoint(set(concrete_types2))

    @graphql_field(
        'queryType', '__Type!', {}, [], 'The type for the root query object')
    def root_query_type(self):
        """Return the GraphQlObjectType for the root query object."""
        return self._base_types[self._query_type_name]

    @graphql_field(
        'mutationType', '__Type', {}, [],
        'The type for the root mutation object, if any')
    def root_mutation_type(self):
        """Return the GraphQlObjectType for the root mutation object, if any.
        """
        if self._mutation_type_name is not None:
            return self._base_types[self._mutation_type_name]
        else:
            return None

    def directive(self, name):
        """Return the GraphQlDirectiveType with the specified name.

        Return None if there is no such directive.
        """
        if name in self._directives:
            return self._directives[name]
        else:
            return None

    def class_type(self, cls):
        """Return the GraphQlObjectType of the specified Python class, if any.

        Return the GraphQlObjectType of instances of the specified
        Python class, if any.
        """
        for cls in inspect.getmro(cls):
            descriptor = GraphQlClassDescriptor.create_from_class(cls)
            if descriptor in self._class_descriptor_to_object_type:
                return self._class_descriptor_to_object_type[descriptor]
        return None

    def object_type(self, value):
        """Return the GraphQlObjectType of the specified Python object, if any.
        """
        return self.class_type(value.__class__)

    def common_field_descriptor(self, name):
        """Return the GraphQlFieldDescriptor for the specified common field.

        Return the GraphQlFieldDescriptor for the specified field common
        to all objects, or None if there is no common field with the
        specified name.  For example, the "__typename" field is common
        to all objects.

        basestring name - The field name.
        return GraphQlFieldDescriptor - A description of the field.
        """
        return self._common_field_descriptors.get(name)

    def implicit_root_field_descriptor(self, name):
        """Return the GraphQlFieldDescriptor for the given implicit root field.

        Return the GraphQlFieldDescriptor for the specified field in the
        root query object that does not appear in __Type{fields}, or
        None if there is no such field.  For example, the "__schema"
        field is implicit.

        basestring name - The field name.
        return GraphQlFieldDescriptor - A description of the field.
        """
        return self._implicit_root_field_descriptors.get(name)

    @graphql_field('types', '[__Type!]!', {}, [], 'A list of the base types')
    def _get_base_types(self):
        """Return a list of the GraphQlBaseTypes."""
        return list(self._base_types.values())

    @graphql_field(
        'subscriptionType', '__Type', {}, [],
        'The type of the root subscription object, if any')
    def _root_subscription_type(self):
        """Return the GraphQlObjectType for the subscription object, if any.
        """
        return None

    @graphql_field(
        'directives', '[__Directive!]!', {}, [], 'A list of the directives')
    def _get_directives(self):
        """Return a list of the GraphQlDirectiveTypes."""
        return list(self._directives.itervalues())
