import unittest

from graphql.executor import GraphQlContext
from graphql.executor import GraphQlExecutor
from graphql.schema import GraphQlSchemaFactory


class GraphQlIntrospectionTest(unittest.TestCase):
    """Tests GraphQlExecutor on introspection queries."""

    def _context(self):
        """Return a GraphQlContext for the "star_wars" module."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.scalar_descriptors.strict'])
        return GraphQlContext(schema)

    def _extra_context(self):
        """Return a GraphQlContext for the "star_wars_extra" module."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.executor.test.star_wars_extra',
            'graphql.scalar_descriptors.strict'])
        return GraphQlContext(schema)

    def test_schema(self):
        """Test GraphQlExecutor on queries for __Schema."""
        schema = GraphQlSchemaFactory.create_from_modules(
            [
                'graphql.executor.test.star_wars',
                'graphql.scalar_descriptors.strict'],
            'Query', None)
        context = GraphQlContext(schema)
        result = GraphQlExecutor.execute(
            "query IntrospectionTypeQuery {\n"
            "    __schema {\n"
            "        types {\n"
            "            name\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__schema'], list(result['data'].iterkeys()))
        self.assertEqual(
            ['types'], list(result['data']['__schema'].iterkeys()))
        expected_names = set([
            'Boolean', 'Character', 'Droid', 'Episode', 'Float', 'Human', 'ID',
            'Int', 'Query', 'String', '__Directive', '__DirectiveLocation',
            '__EnumValue', '__Field', '__InputValue', '__Schema', '__Type',
            '__TypeKind'])
        actual_names = set(
            [t['name'] for t in result['data']['__schema']['types']])
        self.assertEqual(expected_names, actual_names)

        result = GraphQlExecutor.execute(
            "query IntrospectionQueryTypeQuery {\n"
            "    __schema {\n"
            "        queryType {\n"
            "            name\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {'data': {'__schema': {'queryType': {'name': 'Query'}}}}, result)

        result = GraphQlExecutor.execute(
            "query IntrospectionQueryTypeQuery {\n"
            "    __schema {\n"
            "        queryType {\n"
            "            fields {\n"
            "                name\n"
            "                args {\n"
            "                    name\n"
            "                    description\n"
            "                    type {\n"
            "                        name\n"
            "                        kind\n"
            "                        ofType {\n"
            "                            name\n"
            "                            kind\n"
            "                        }\n"
            "                    }\n"
            "                    defaultValue\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__schema'], list(result['data'].iterkeys()))
        self.assertEqual(
            ['queryType'], list(result['data']['__schema'].iterkeys()))
        self.assertEqual(
            ['fields'],
            list(result['data']['__schema']['queryType'].iterkeys()))
        expected_fields = {
            'droid': {
                'args': [{
                    'defaultValue': None,
                    'description': None,
                    'name': 'id',
                    'type': {
                        'kind': 'NON_NULL',
                        'name': None,
                        'ofType': {
                            'kind': 'SCALAR',
                            'name': 'String',
                        },
                    },
                }],
                'name': 'droid',
            },
            'hero': {
                'args': [{
                    'defaultValue': None,
                    'description': None,
                    'name': 'episode',
                    'type': {
                        'kind': 'ENUM',
                        'name': 'Episode',
                        'ofType': None,
                    }
                }],
                'name': 'hero',
            },
            'human': {
                'args': [{
                    'defaultValue': None,
                    'description': None,
                    'name': 'id',
                    'type': {
                        'kind': 'NON_NULL',
                        'name': None,
                        'ofType': {
                            'kind': 'SCALAR',
                            'name': 'String',
                        },
                    },
                }],
                'name': 'human',
            },
        }
        actual_fields = {}
        for field in result['data']['__schema']['queryType']['fields']:
            actual_fields[field['name']] = field
        self.assertEqual(expected_fields, actual_fields)

    def test_type(self):
        """Test GraphQlExecutor on queries for __type."""
        context = self._context()
        result = GraphQlExecutor.execute(
            "query IntrospectionDroidTypeQuery {\n"
            "    __type(name: \"Droid\") {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual({'data': {'__type': {'name': 'Droid'}}}, result)

        result = GraphQlExecutor.execute(
            "query IntrospectionDroidKindQuery {\n"
            "    __type(name: \"Droid\") {\n"
            "        name\n"
            "        kind\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {'data': {'__type': {'kind': 'OBJECT', 'name': 'Droid'}}}, result)

        result = GraphQlExecutor.execute(
            "query IntrospectionCharacterKindQuery {\n"
            "    __type(name: \"Character\") {\n"
            "        name\n"
            "        kind\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {'data': {'__type': {'kind': 'INTERFACE', 'name': 'Character'}}},
            result)

        result = GraphQlExecutor.execute(
            "query IntrospectionDroidDescriptionQuery {\n"
            "    __type(name: \"Droid\") {\n"
            "        name\n"
            "        description\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {
                'data': {
                    '__type': {
                        'description':
                            'A mechanical creature in the Star Wars universe.',
                        'name': 'Droid',
                    },
                },
            }, result)

    def test_type_fields(self):
        """Test GraphQlExecutor on queries for __Type{fields}."""
        context = self._context()
        result = GraphQlExecutor.execute(
            "query IntrospectionDroidFieldsQuery {\n"
            "    __type(name: \"Droid\") {\n"
            "        name\n"
            "        fields {\n"
            "            name\n"
            "            type {\n"
            "                name\n"
            "                kind\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__type'], list(result['data'].iterkeys()))
        self.assertEqual(
            set(['fields', 'name']), set(result['data']['__type'].iterkeys()))
        self.assertEqual('Droid', result['data']['__type']['name'])
        expected_fields = {
            'appearsIn': {
                'name': 'appearsIn',
                'type': {
                    'kind': 'LIST',
                    'name': None,
                },
            },
            'friends': {
                'name': 'friends',
                'type': {
                    'kind': 'LIST',
                    'name': None,
                },
            },
            'id': {
                'name': 'id',
                'type': {
                    'kind': 'NON_NULL',
                    'name': None,
                },
            },
            'name': {
                'name': 'name',
                'type': {
                    'kind': 'SCALAR',
                    'name': 'String',
                },
            },
            'primaryFunction': {
                'name': 'primaryFunction',
                'type': {
                    'kind': 'SCALAR',
                    'name': 'String',
                },
            },
        }
        actual_fields = {}
        for field in result['data']['__type']['fields']:
            actual_fields[field['name']] = field
        self.assertEqual(expected_fields, actual_fields)

        result = GraphQlExecutor.execute(
            "query IntrospectionDroidNestedFieldsQuery {\n"
            "    __type(name: \"Droid\") {\n"
            "        name\n"
            "        fields {\n"
            "            name\n"
            "            type {\n"
            "                name\n"
            "                kind\n"
            "                ofType {\n"
            "                    name\n"
            "                    kind\n"
            "                }\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__type'], list(result['data'].iterkeys()))
        self.assertEqual(
            set(['fields', 'name']), set(result['data']['__type'].iterkeys()))
        self.assertEqual('Droid', result['data']['__type']['name'])
        expected_fields = {
            'appearsIn': {
                'name': 'appearsIn',
                'type': {
                    'kind': 'LIST',
                    'name': None,
                    'ofType': {
                        'kind': 'ENUM',
                        'name': 'Episode',
                    },
                },
            },
            'friends': {
                'name': 'friends',
                'type': {
                    'kind': 'LIST',
                    'name': None,
                    'ofType': {
                        'kind': 'INTERFACE',
                        'name': 'Character',
                    },
                },
            },
            'id': {
                'name': 'id',
                'type': {
                    'kind': 'NON_NULL',
                    'name': None,
                    'ofType': {
                        'kind': 'SCALAR',
                        'name': 'String',
                    },
                },
            },
            'name': {
                'name': 'name',
                'type': {
                    'kind': 'SCALAR',
                    'name': 'String',
                    'ofType': None,
                },
            },
            'primaryFunction': {
                'name': 'primaryFunction',
                'type': {
                    'kind': 'SCALAR',
                    'name': 'String',
                    'ofType': None,
                },
            },
        }
        actual_fields = {}
        for field in result['data']['__type']['fields']:
            actual_fields[field['name']] = field
        self.assertEqual(expected_fields, actual_fields)

    def test_field_descriptions(self):
        """Test GraphQlExecutor on __Type{fields{description, ...}}."""
        context = self._extra_context()
        result = GraphQlExecutor.execute(
            'query {__type(name: "Faction") {fields {name, description}}}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__type'], list(result['data'].iterkeys()))
        self.assertEqual(['fields'], list(result['data']['__type'].iterkeys()))
        expected_fields = {
            'longName': {
                'description': 'The long form of the name of the faction',
                'name': 'longName',
            },
            'mostPowerfulShip': {
                'description': "The most powerful ship in the faction's fleet",
                'name': 'mostPowerfulShip',
            },
            'shortName': {
                'description': 'The short form of the name of the faction',
                'name': 'shortName',
            },
        }
        actual_fields = {}
        for field in result['data']['__type']['fields']:
            actual_fields[field['name']] = field
        self.assertEqual(expected_fields, actual_fields)

        result = GraphQlExecutor.execute(
            'query {__type(name: "Faction") {fields(includeDeprecated: true) {'
            'name, description, isDeprecated, deprecationReason}}}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__type'], list(result['data'].iterkeys()))
        self.assertEqual(['fields'], list(result['data']['__type'].iterkeys()))
        expected_fields = {
            'bestShip': {
                'deprecationReason': None,
                'description': "The most powerful ship in the faction's fleet",
                'isDeprecated': True,
                'name': 'bestShip',
            },
            'longName': {
                'deprecationReason': None,
                'description': 'The long form of the name of the faction',
                'isDeprecated': False,
                'name': 'longName',
            },
            'mostPowerfulShip': {
                'deprecationReason': None,
                'description': "The most powerful ship in the faction's fleet",
                'isDeprecated': False,
                'name': 'mostPowerfulShip',
            },
            'name': {
                'deprecationReason': 'Replaced with shortName and longName',
                'description': 'The name of the faction',
                'isDeprecated': True,
                'name': 'name',
            },
            'shortName': {
                'deprecationReason': None,
                'description': 'The short form of the name of the faction',
                'isDeprecated': False,
                'name': 'shortName',
            },
        }
        actual_fields = {}
        for field in result['data']['__type']['fields']:
            actual_fields[field['name']] = field
        self.assertEqual(expected_fields, actual_fields)

    def test_root_field_descriptions(self):
        """Test GraphQlExecutor on __Type{fields{description}} on root objects.

        Test GraphQlExecutor on __Type{fields{description}} and similar
        fields on the root query and mutation objects.
        """
        context = self._extra_context()
        result = GraphQlExecutor.execute(
            'query {__schema {queryType {fields(includeDeprecated: true) {'
            'name, description, isDeprecated, deprecationReason}}}}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__schema'], list(result['data'].iterkeys()))
        self.assertEqual(
            ['queryType'], list(result['data']['__schema'].iterkeys()))
        self.assertEqual(
            ['fields'],
            list(result['data']['__schema']['queryType'].iterkeys()))
        self.assertIn(
            {
                'deprecationReason': None,
                'description':
                    'The ship with the specified ID.  Emits an error if there '
                    'is no such ship.',
                'isDeprecated': False,
                'name': 'ship',
            }, result['data']['__schema']['queryType']['fields'])
        self.assertIn(
            {
                'deprecationReason': 'Use Query{search} instead',
                'description':
                    'The ship with the specified name, or null if there is no '
                    'such ship.',
                'isDeprecated': True,
                'name': 'shipFromName',
            }, result['data']['__schema']['queryType']['fields'])

        result = GraphQlExecutor.execute(
            'query {__schema {mutationType {fields(includeDeprecated: true) {'
            'name, description, isDeprecated, deprecationReason}}}}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['__schema'], list(result['data'].iterkeys()))
        self.assertEqual(
            ['mutationType'], list(result['data']['__schema'].iterkeys()))
        self.assertEqual(
            ['fields'],
            list(result['data']['__schema']['mutationType'].iterkeys()))
        self.assertIn(
            {
                'deprecationReason': None,
                'description':
                    'Adds a ship with the specified name to our records',
                'isDeprecated': False,
                'name': 'introduceShip',
            }, result['data']['__schema']['mutationType']['fields'])
        self.assertIn(
            {
                'deprecationReason': None,
                'description':
                    'Adds a ship with the specified name to our records',
                'isDeprecated': True,
                'name': 'introduceShipWithName',
            }, result['data']['__schema']['mutationType']['fields'])
