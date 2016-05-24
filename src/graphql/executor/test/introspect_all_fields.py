import unittest

from graphql.executor import GraphQlContext
from graphql.executor import GraphQlExecutor
from graphql.schema import GraphQlSchemaFactory


class GraphQlIntrospectAllFieldsTest(unittest.TestCase):
    """Tests GraphQlExecutor on an introspection query for most everything.

    Tests GraphQlExecutor on an introspection query for most every piece
    of information about each of the types and directives.
    """

    def _convert_lists_to_sets(self, value):
        """Convert lists to sets and non-hashable values to hashable values.

        Return a value that is the same as "value", but with lists
        changed to frozensets and dictionaries changed to hashable
        representations of themselves.  The representation is
        many-to-one, though our goal is that different values will
        typically have different representations.

        obj value - The JSON value to convert.
        return obj - The representation.
        """
        if isinstance(value, list):
            result = []
            for element in value:
                result.append(self._convert_lists_to_sets(element))
            return frozenset(result)
        elif isinstance(value, dict):
            items = []
            for key in list(sorted(value.iterkeys())):
                items.append((key, self._convert_lists_to_sets(value[key])))
            return tuple(items)
        else:
            return value

    def test_introspection(self):
        """Test GraphQlExecutor on an introspection query for most everything.

        Test GraphQlExecutor on an introspection query for most every
        piece of information about each of the types.
        """
        schema = GraphQlSchemaFactory.create_from_modules(
            [
                'graphql.executor.test.star_wars',
                'graphql.scalar_descriptors.strict'],
            'Query', None)
        context = GraphQlContext(schema)
        result = GraphQlExecutor.execute(
            'query {__schema {types {'
            'kind, name, fields {'
            'name, args {name, type {...TypeFields}}, isDeprecated, '
            'deprecationReason, type {...TypeFields}},'
            'interfaces {name}, possibleTypes {name},'
            'enumValues {name, isDeprecated, deprecationReason}, '
            'inputFields {name}, ofType {name}}}}'
            'fragment TypeFields on __Type {'
            'name, kind, ofType {name, kind, ofType {'
            'name, kind, ofType {name, kind, ofType {name}}}}}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__schema'], list(result['data'].iterkeys()))
        self.assertEqual(
            ['types'], list(result['data']['__schema'].iterkeys()))
        expected_types = [
            {
                'enumValues': None,
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'SCALAR',
                'name': 'Boolean',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'appearsIn',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'ENUM',
                                'name': 'Episode',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'friends',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'INTERFACE',
                                'name': 'Character',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'id',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'String',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': None,
                'kind': 'INTERFACE',
                'name': 'Character',
                'ofType': None,
                'possibleTypes': [
                    {'name': 'Droid'},
                    {'name': 'Human'},
                ],
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'appearsIn',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'ENUM',
                                'name': 'Episode',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'friends',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'INTERFACE',
                                'name': 'Character',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'id',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'String',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'primaryFunction',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [{'name': 'Character'}],
                'kind': 'OBJECT',
                'name': 'Droid',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': [
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'NEWHOPE',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'EMPIRE',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'JEDI',
                    },
                ],
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'ENUM',
                'name': 'Episode',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'SCALAR',
                'name': 'Float',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'appearsIn',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'ENUM',
                                'name': 'Episode',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'friends',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'INTERFACE',
                                'name': 'Character',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'homePlanet',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'id',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'String',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [{'name': 'Character'}],
                'kind': 'OBJECT',
                'name': 'Human',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'SCALAR',
                'name': 'ID',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'SCALAR',
                'name': 'Int',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [
                            {
                                'name': 'id',
                                'type': {
                                    'kind': 'NON_NULL',
                                    'name': None,
                                    'ofType': {
                                        'kind': 'SCALAR',
                                        'name': 'String',
                                        'ofType': None,
                                    },
                                },
                            },
                        ],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'droid',
                        'type': {
                            'kind': 'OBJECT',
                            'name': 'Droid',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [
                            {
                                'name': 'episode',
                                'type': {
                                    'kind': 'ENUM',
                                    'name': 'Episode',
                                    'ofType': None,
                                },
                            },
                        ],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'hero',
                        'type': {
                            'kind': 'INTERFACE',
                            'name': 'Character',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [
                            {
                                'name': 'id',
                                'type': {
                                    'kind': 'NON_NULL',
                                    'name': None,
                                    'ofType': {
                                        'kind': 'SCALAR',
                                        'name': 'String',
                                        'ofType': None,
                                    },
                                },
                            },
                        ],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'human',
                        'type': {
                            'kind': 'OBJECT',
                            'name': 'Human',
                            'ofType': None,
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [],
                'kind': 'OBJECT',
                'name': 'Query',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'SCALAR',
                'name': 'String',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'args',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'LIST',
                                'name': None,
                                'ofType': {
                                    'kind': 'NON_NULL',
                                    'name': None,
                                    'ofType': {
                                        'kind': 'OBJECT',
                                        'name': '__InputValue',
                                        'ofType': None,
                                    },
                                },
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'description',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'locations',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'LIST',
                                'name': None,
                                'ofType': {
                                    'kind': 'NON_NULL',
                                    'name': None,
                                    'ofType': {
                                        'kind': 'ENUM',
                                        'name': '__DirectiveLocation',
                                        'ofType': None,
                                    },
                                },
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'String',
                                'ofType': None,
                            },
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [],
                'kind': 'OBJECT',
                'name': '__Directive',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': [
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'FIELD',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'FRAGMENT_DEFINITION',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'FRAGMENT_SPREAD',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'INLINE_FRAGMENT',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'MUTATION',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'QUERY',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'SUBSCRIPTION',
                    },
                ],
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'ENUM',
                'name': '__DirectiveLocation',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'deprecationReason',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'description',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'isDeprecated',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'Boolean',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'String',
                                'ofType': None,
                            },
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [],
                'kind': 'OBJECT',
                'name': '__EnumValue',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'args',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'LIST',
                                'name': None,
                                'ofType': {
                                    'kind': 'NON_NULL',
                                    'name': None,
                                    'ofType': {
                                        'kind': 'OBJECT',
                                        'name': '__InputValue',
                                        'ofType': None,
                                    },
                                },
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'deprecationReason',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'description',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'isDeprecated',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'Boolean',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'String',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'type',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'OBJECT',
                                'name': '__Type',
                                'ofType': None,
                            },
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [],
                'kind': 'OBJECT',
                'name': '__Field',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'defaultValue',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'description',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'String',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'type',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'OBJECT',
                                'name': '__Type',
                                'ofType': None,
                            },
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [],
                'kind': 'OBJECT',
                'name': '__InputValue',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'directives',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'LIST',
                                'name': None,
                                'ofType': {
                                    'kind': 'NON_NULL',
                                    'name': None,
                                    'ofType': {
                                        'kind': 'OBJECT',
                                        'name': '__Directive',
                                        'ofType': None,
                                    },
                                },
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'mutationType',
                        'type': {
                            'kind': 'OBJECT',
                            'name': '__Type',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'queryType',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'OBJECT',
                                'name': '__Type',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'subscriptionType',
                        'type': {
                            'kind': 'OBJECT',
                            'name': '__Type',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'types',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'LIST',
                                'name': None,
                                'ofType': {
                                    'kind': 'NON_NULL',
                                    'name': None,
                                    'ofType': {
                                        'kind': 'OBJECT',
                                        'name': '__Type',
                                        'ofType': None,
                                    },
                                },
                            },
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [],
                'kind': 'OBJECT',
                'name': '__Schema',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': None,
                'fields': [
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'description',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [
                            {
                                'name': 'includeDeprecated',
                                'type': {
                                    'kind': 'SCALAR',
                                    'name': 'Boolean',
                                    'ofType': None,
                                },
                            },
                        ],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'enumValues',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'NON_NULL',
                                'name': None,
                                'ofType': {
                                    'kind': 'OBJECT',
                                    'name': '__EnumValue',
                                    'ofType': None,
                                },
                            },
                        },
                    },
                    {
                        'args': [
                            {
                                'name': 'includeDeprecated',
                                'type': {
                                    'kind': 'SCALAR',
                                    'name': 'Boolean',
                                    'ofType': None,
                                },
                            },
                        ],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'fields',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'NON_NULL',
                                'name': None,
                                'ofType': {
                                    'kind': 'OBJECT',
                                    'name': '__Field',
                                    'ofType': None,
                                },
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'inputFields',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'NON_NULL',
                                'name': None,
                                'ofType': {
                                    'kind': 'OBJECT',
                                    'name': '__InputValue',
                                    'ofType': None,
                                },
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'interfaces',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'NON_NULL',
                                'name': None,
                                'ofType': {
                                    'kind': 'OBJECT',
                                    'name': '__Type',
                                    'ofType': None,
                                },
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'kind',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'ENUM',
                                'name': '__TypeKind',
                                'ofType': None,
                            },
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'name',
                        'type': {
                            'kind': 'SCALAR',
                            'name': 'String',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'ofType',
                        'type': {
                            'kind': 'OBJECT',
                            'name': '__Type',
                            'ofType': None,
                        },
                    },
                    {
                        'args': [],
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'possibleTypes',
                        'type': {
                            'kind': 'LIST',
                            'name': None,
                            'ofType': {
                                'kind': 'NON_NULL',
                                'name': None,
                                'ofType': {
                                    'kind': 'OBJECT',
                                    'name': '__Type',
                                    'ofType': None,
                                },
                            },
                        },
                    },
                ],
                'inputFields': None,
                'interfaces': [],
                'kind': 'OBJECT',
                'name': '__Type',
                'ofType': None,
                'possibleTypes': None,
            },
            {
                'enumValues': [
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'ENUM',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'INPUT_OBJECT',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'INTERFACE',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'LIST',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'NON_NULL',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'OBJECT',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'SCALAR',
                    },
                    {
                        'deprecationReason': None,
                        'isDeprecated': False,
                        'name': 'UNION',
                    },
                ],
                'fields': None,
                'inputFields': None,
                'interfaces': None,
                'kind': 'ENUM',
                'name': '__TypeKind',
                'ofType': None,
                'possibleTypes': None,
            },
        ]
        self.assertEqual(
            self._convert_lists_to_sets(expected_types),
            self._convert_lists_to_sets(result['data']['__schema']['types']))

    def test_directive_introspection(self):
        """Test GraphQlExecutor on an introspection query for directives.

        Test GraphQlExecutor on an introspection query for most every
        piece of information about each of the directives.
        """
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.scalar_descriptors.strict'])
        context = GraphQlContext(schema)
        result = GraphQlExecutor.execute(
            'query {__schema {directives {'
            'name, locations, args {'
            'name, type {name, kind, ofType {name, kind, ofType {'
            'name, kind, ofType {name, kind}}}}}}}}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__schema'], list(result['data'].iterkeys()))
        self.assertEqual(
            ['directives'], list(result['data']['__schema'].iterkeys()))
        expected_directives = [
            {
                'args': [
                    {
                        'name': 'if',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'Boolean',
                                'ofType': None,
                            },
                        },
                    },
                ],
                'locations': [
                    'FIELD',
                    'FRAGMENT_DEFINITION',
                    'FRAGMENT_SPREAD',
                    'INLINE_FRAGMENT',
                ],
                'name': 'include',
            },
            {
                'args': [
                    {
                        'name': 'if',
                        'type': {
                            'kind': 'NON_NULL',
                            'name': None,
                            'ofType': {
                                'kind': 'SCALAR',
                                'name': 'Boolean',
                                'ofType': None,
                            },
                        },
                    },
                ],
                'locations': [
                    'FIELD',
                    'FRAGMENT_DEFINITION',
                    'FRAGMENT_SPREAD',
                    'INLINE_FRAGMENT',
                ],
                'name': 'skip',
            },
        ]
        self.assertEqual(
            self._convert_lists_to_sets(expected_directives),
            self._convert_lists_to_sets(
                result['data']['__schema']['directives']))
