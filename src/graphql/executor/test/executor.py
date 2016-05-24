import unittest

from context_with_email import GraphQlContextWithEmail
from graphql.document import GraphQlParser
from graphql.executor import GraphQlContext
from graphql.executor import GraphQlExecutor
from graphql.executor.test.star_wars_extra import get_sw_ship
from graphql.executor.test.star_wars_extra import SwShip
from graphql.executor.test.star_wars_extra import SwUsers
from graphql.schema import GraphQlSchemaFactory
from silent_context import SilentGraphQlContext
from tracking_context import TrackingGraphQlContext


class GraphQlExecutorTest(unittest.TestCase):
    def _context(self):
        """Return a GraphQlContext for the "star_wars" module."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.scalar_descriptors.strict'])
        return GraphQlContext(schema)

    def _extra_schema(self):
        """Return a GraphQlSchema for the "star_wars_extra" module."""
        return GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.executor.test.star_wars_extra',
            'graphql.scalar_descriptors.strict'])

    def _extra_context(self):
        """Return a GraphQlContext for the "star_wars_extra" module."""
        return GraphQlContext(self._extra_schema())

    def test_friend_queries(self):
        """Test GraphQlExecutor on the field Character{friend}."""
        context = self._context()
        result = GraphQlExecutor.execute(
            "query HeroNameQuery {\n"
            "    hero {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual({'data': {'hero': {'name': 'R2-D2'}}}, result)

        result = GraphQlExecutor.execute(
            "query HeroNameAndFriendsQuery {\n"
            "    hero {\n"
            "        id\n"
            "        name\n"
            "        friends {\n"
            "            name\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {
                'data': {
                    'hero': {
                        'friends': [
                            {'name': 'Luke Skywalker'},
                            {'name': 'Han Solo'},
                            {'name': 'Leia Organa'},
                        ],
                        'id': '2001',
                        'name': 'R2-D2',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            "query NestedQuery {\n"
            "    hero {\n"
            "        name\n"
            "        friends {\n"
            "            name\n"
            "            appearsIn\n"
            "            friends {\n"
            "                name\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {
                'data': {
                    'hero': {
                        'friends': [
                            {
                                'appearsIn': ['NEWHOPE', 'EMPIRE', 'JEDI'],
                                'friends': [
                                    {'name': 'Han Solo'},
                                    {'name': 'Leia Organa'},
                                    {'name': 'C-3PO'},
                                    {'name': 'R2-D2'},
                                ],
                                'name': 'Luke Skywalker',
                            },
                            {
                                'appearsIn': ['NEWHOPE', 'EMPIRE', 'JEDI'],
                                'friends': [
                                    {'name': 'Luke Skywalker'},
                                    {'name': 'Leia Organa'},
                                    {'name': 'R2-D2'},
                                ],
                                'name': 'Han Solo',
                            },
                            {
                                'appearsIn': ['NEWHOPE', 'EMPIRE', 'JEDI'],
                                'friends': [
                                    {'name': 'Luke Skywalker'},
                                    {'name': 'Han Solo'},
                                    {'name': 'C-3PO'},
                                    {'name': 'R2-D2'},
                                ],
                                'name': 'Leia Organa',
                            },
                        ],
                        'name': 'R2-D2',
                    },
                },
            }, result)

    def test_id_queries(self):
        """Test GraphQlExecutor on queries for Star Wars characters by ID."""
        context = self._context()
        result = GraphQlExecutor.execute(
            "query FetchLukeQuery {\n"
            "    human(id: \"1000\") {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            "query FetchSomeIDQuery($someId: String!) {\n"
            "    human(id: $someId) {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context, {'someId': '1000'})
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            "query FetchSomeIDQuery($someId: String!) {\n"
            "    human(id: $someId) {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context, {'someId': '1002'})
        self.assertEqual({'data': {'human': {'name': 'Han Solo'}}}, result)

        result = GraphQlExecutor.execute(
            "query FetchSomeIDQuery($someId: String!) {\n"
            "    human(id: $someId) {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context, {'someId': 'not a valid id'})
        self.assertEqual({'data': {'human': None}}, result)

    def test_alias_queries(self):
        """Test GraphQlExecutor on queries that use aliases."""
        context = self._context()
        result = GraphQlExecutor.execute(
            "query FetchLukeAliased {\n"
            "    luke: human(id: \"1000\") {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {'data': {'luke': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            "query FetchLukeAndLeiaAliased {\n"
            "    luke: human(id: \"1000\") {\n"
            "        name\n"
            "    }\n"
            "    leia: human(id: \"1003\") {\n"
            "        name\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {
                'data': {
                    'luke': {'name': 'Luke Skywalker'},
                    'leia': {'name': 'Leia Organa'},
                },
            }, result)

        result = GraphQlExecutor.execute(
            "query DuplicateFields {\n"
            "    luke: human(id: \"1000\") {\n"
            "        name\n"
            "        homePlanet\n"
            "    }\n"
            "    leia: human(id: \"1003\") {\n"
            "        name\n"
            "        homePlanet\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {
                'data': {
                    'luke': {
                        'homePlanet': 'Tatooine',
                        'name': 'Luke Skywalker',
                    },
                    'leia': {
                        'homePlanet': 'Alderaan',
                        'name': 'Leia Organa',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            "query UseFragment {\n"
            "    luke: human(id: \"1000\") {\n"
            "        ...HumanFragment\n"
            "    }\n"
            "    leia: human(id: \"1003\") {\n"
            "        ...HumanFragment\n"
            "    }\n"
            "}\n"
            "\n"
            "fragment HumanFragment on Human {\n"
            "    name\n"
            "    homePlanet\n"
            "}\n",
            context)
        self.assertEqual(
            {
                'data': {
                    'luke': {
                        'homePlanet': 'Tatooine',
                        'name': 'Luke Skywalker',
                    },
                    'leia': {
                        'homePlanet': 'Alderaan',
                        'name': 'Leia Organa',
                    },
                },
            }, result)

    def test_typename_queries(self):
        """Test GraphQlExecutor on queries that request the __typename field.
        """
        context = self._context()
        result = GraphQlExecutor.execute(
            "query CheckTypeOfR2 {\n"
            "    hero {\n"
            "        __typename\n"
            "        name\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {'data': {'hero': {'name': 'R2-D2', '__typename': 'Droid'}}},
            result)

        result = GraphQlExecutor.execute(
            "query CheckTypeOfLuke {\n"
            "    hero(episode: EMPIRE) {\n"
            "        __typename\n"
            "        name\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(
            {
                'data': {
                    'hero': {
                        'name': 'Luke Skywalker',
                        '__typename': 'Human',
                    },
                },
            }, result)

    def test_directives(self):
        """Test GraphQlExecutor on documents with directives."""
        context = self._context()
        result = GraphQlExecutor.execute(
            '{human(id: "1000"){name @include(if: true)}}', context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){name @include(if: false)}}', context)
        self.assertEqual({'data': {'human': {}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){name @skip(if: true)}}', context)
        self.assertEqual({'data': {'human': {}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){name @skip(if: false)}}', context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000") @include(if: true){name}}', context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000") @include(if: false){name}}', context)
        self.assertEqual({'data': {}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){...HumanFields}} '
            'fragment HumanFields on Human @include(if: true){name}',
            context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){...HumanFields}} '
            'fragment HumanFields on Human @include(if: false){name}',
            context)
        self.assertEqual({'data': {'human': {}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){...HumanFields}} '
            'fragment HumanFields on Human{name @include(if: true)}',
            context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){...HumanFields}} '
            'fragment HumanFields on Human{name @include(if: false)}',
            context)
        self.assertEqual({'data': {'human': {}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){...HumanFields @include(if: true)}} '
            'fragment HumanFields on Human{name}',
            context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){...HumanFields @include(if: false)}} '
            'fragment HumanFields on Human{name}',
            context)
        self.assertEqual({'data': {'human': {}}}, result)

        result = GraphQlExecutor.execute(
            '($if: Boolean!) {human(id: "1000"){name @include(if: $if)}}',
            context, {'if': True})
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute(
            '($if: Boolean!) {human(id: "1000"){name @include(if: $if)}}',
            context, {'if': False})
        self.assertEqual({'data': {'human': {}}}, result)

    def test_gexecute_document(self):
        """Test GraphQlExecutor.execute_document."""
        context = self._context()
        document = GraphQlParser(
            '{human(id: "1000"){name}}', context.schema).parse()
        result = GraphQlExecutor.execute_document(document, context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

        result = GraphQlExecutor.execute_document(document, context)
        self.assertEqual(
            {'data': {'human': {'name': 'Luke Skywalker'}}}, result)

    def test_mutations(self):
        """Test GraphQlExecutor on documents with mutations."""
        SwShip.reset()
        context = self._extra_context()
        result = GraphQlExecutor.execute(
            'mutation{introduceShip(input: '
            '{clientMutationId: "foo", name: "Y-wing"})'
            '{clientMutationId, ship{id, name}}}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual(['introduceShip'], list(result['data'].iterkeys()))
        self.assertEqual(
            set(['clientMutationId', 'ship']),
            set(result['data']['introduceShip'].iterkeys()))
        self.assertEqual(
            'foo', result['data']['introduceShip']['clientMutationId'])
        self.assertEqual(
            set(['id', 'name']),
            set(result['data']['introduceShip']['ship'].iterkeys()))
        self.assertEqual(
            'Y-wing', result['data']['introduceShip']['ship']['name'])
        ship_id = result['data']['introduceShip']['ship']['id']
        self.assertEqual('Y-wing', get_sw_ship(ship_id).name)

        result = GraphQlExecutor.execute(
            'mutation{ship1: setFavoriteShip(id: "3000"){name}, '
            'ship2: setFavoriteShip(id: "does not exist"){name}, '
            'ship3: setFavoriteShip(id: "3001"){name}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'ship1': {'name': 'Millennium Falcon'},
                    'ship2': None,
                    'ship3': {'name': 'X-wing'},
                },
            }, result)
        self.assertEqual('X-wing', SwShip.favorite_ship().name)

    def test_unions(self):
        """Test GraphQlExecutor on documents with union fields."""
        context = self._extra_context()
        result = GraphQlExecutor.execute(
            '{search(name: "X-wing") {'
            '... on Character {appearsIn}, ... on Ship {id}}}',
            context)
        self.assertEqual({'data': {'search': {'id': '3001'}}}, result)

        result = GraphQlExecutor.execute(
            '{search(name: "Luke Skywalker") {'
            '... on Character {appearsIn}, ... on Ship {id}}}',
            context)
        self.assertEqual(
            {'data': {'search': {'appearsIn': ['NEWHOPE', 'EMPIRE', 'JEDI']}}},
            result)

        result = GraphQlExecutor.execute(
            '{search(name: "Dark Helmet") {'
            '... on Character {appearsIn}, ... on Ship {id}}}',
            context)
        self.assertEqual({'data': {'search': None}}, result)

    def test_context_args(self):
        """Test context arguments, as in GraphQlContext.context_arg."""
        context = GraphQlContextWithEmail('foo@example.com')
        result = GraphQlExecutor.execute('{favoriteCharacter {name}}', context)
        self.assertEqual(
            {'data': {'favoriteCharacter': {'name': 'Darth Vader'}}}, result)

        context = GraphQlContextWithEmail('bar@example.com')
        result = GraphQlExecutor.execute('{favoriteCharacter {name}}', context)
        self.assertEqual(
            {'data': {'favoriteCharacter': {'name': 'R2-D2'}}}, result)

    def test_multiple_inheritance(self):
        """Test GraphQlExecutor with multiple inheritance."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.multiple_inheritance',
            'graphql.scalar_descriptors.strict'])
        context = SilentGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            '{getA{__typename}, getB{__typename}, getC{__typename}}', context)
        self.assertEqual(
            {
                'data': {
                    'getA': {'__typename': 'MultipleInheritanceD'},
                    'getB': {'__typename': 'MultipleInheritanceD'},
                    'getC': {'__typename': 'MultipleInheritanceD'},
                },
            }, result)

        result = GraphQlExecutor.execute('{getAAsF{__typename}}', context)
        self.assertTrue(
            set(result.iterkeys()).issubset(set(['data', 'errors'])))
        self.assertTrue('errors' in result)
        self.assertGreater(len(result['errors']), 0)
        self.assertTrue('data' in result)
        self.assertEqual({'getAAsF': None}, result['data'])

    def _validate_error_response(self, graphql_response):
        """Assert the specified value is a valid GraphQL error response.

        This only performs basic validation.  For example, it does not
        verify that the entire response is a JSON value.
        """
        self.assertTrue(
            set(graphql_response.iterkeys()).issubset(
                set(['errors', 'extensions'])))
        self.assertTrue('errors' in graphql_response)
        self.assertGreater(len(graphql_response['errors']), 0)

    def test_overriding(self):
        """Test GraphQlExecutor with field overriding."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.overriding',
            'graphql.scalar_descriptors.strict'])
        context = SilentGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            'manipulate(base: "foo", prefix: "bar", suffix: "baz")}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorDerived': {
                        'manipulate': 'barfoobaz',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            'manipulate(base: "foo", prefix: "bar")}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorDerived': {
                        'manipulate': 'barfoo',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            '... on StringManipulatorMiddleInterface {'
            'manipulate(base: "foo", prefix: "bar")}}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorDerived': {
                        'manipulate': 'barfoo',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            '... on StringManipulatorMiddle {'
            'manipulate(base: "foo", prefix: "bar")}}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorDerived': {},
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            '... on StringManipulatorBaseInterface {__typename}}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorDerived': {
                        '__typename': 'StringManipulatorDerived',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            '... on StringManipulatorMiddleInterface {__typename}}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorDerived': {
                        '__typename': 'StringManipulatorDerived',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            '... on StringManipulatorMiddleInterface {'
            'manipulate(base: "foo", prefix: "bar", suffix: "baz")}}}',
            context)
        self._validate_error_response(result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorMiddle {'
            'manipulate(base: "foo", prefix: "bar")}}',
            context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorMiddle': {
                        'manipulate': 'barfoo',
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorMiddle {manipulate(base: "foo")}}', context)
        self.assertEqual(
            {
                'data': {
                    'stringManipulatorMiddle': {
                        'manipulate': None,
                    },
                },
            }, result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorMiddle {'
            'manipulate(base: "foo", prefix: "bar", suffix: "baz")}}',
            context)
        self._validate_error_response(result)

        result = GraphQlExecutor.execute(
            '{stringManipulatorDerived {'
            'brokenManipulate(base: "foo", prefix: "bar", suffix: "baz")}}',
            context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertGreater(len(result['errors']), 0)
        self.assertIsNone(result['data'])

    def test_context_calls(self):
        """Test that GraphQlExecutor makes the proper calls to GraphQlContext.
        """
        SwUsers.reset()
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.executor.test.star_wars_extra',
            'graphql.scalar_descriptors.strict'])
        context = TrackingGraphQlContext(schema)
        result = GraphQlExecutor.execute('{hero{name}}', context)
        self.assertEqual(
            {
                'data': {'hero': {'name': 'R2-D2'}},
                'extensions': {'mutationCount': 0},
            }, result)
        self.assertEqual(
            [
                'execute_document_str_start',
                'parsed_document',
                'execute_document_str_end',
                'extensions'],
            context.calls)

        context = TrackingGraphQlContext(schema)
        document = GraphQlParser('{hero{name}}', schema).parse()
        result = GraphQlExecutor.execute_document(document, context)
        self.assertEqual(
            {
                'data': {'hero': {'name': 'R2-D2'}},
                'extensions': {'mutationCount': 0},
            }, result)
        self.assertEqual(
            [
                'execute_document_start',
                'execute_document_end',
                'extensions'],
            context.calls)

        context = TrackingGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            'mutation {register1: register('
            'email: "bar@example.com", password: "anikin", '
            'captchaToken: "abc123"),'
            'register2: register('
            'email: "baz@example.com", password: "abc", '
            'captchaToken: "abc123")}',
            context)
        self.assertEqual(
            set(['data', 'errors', 'extensions']), set(result.iterkeys()))
        self.assertGreater(len(result['errors']), 0)
        self.assertEqual(
            {'register1': True, 'register2': False}, result['data'])
        self.assertEqual({'mutationCount': 2}, result['extensions'])
        self.assertEqual(
            [
                'execute_document_str_start',
                'parsed_document',
                'mutation_start',
                'mutation_end',
                'mutation_start',
                'exception_errors',
                'mutation_end',
                'execute_document_str_end',
                'extensions'],
            context.calls)

    def test_numbers(self):
        """Test GraphQlExecutor with numbers."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.numbers',
            'graphql.scalar_descriptors.strict'])
        context = SilentGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            '{math {sum('
            'numbers: [1, 2.3, -15.61, -0.00, 1E2, 2e+1, -2e-1, 0, 0.5])}}',
            context)
        self.assertEqual({'data': {'math': {'sum': 107.99}}}, result)

        result = GraphQlExecutor.execute(
            '{math {sum(numbers: [1e50, 2e51])}}', context)
        self.assertEqual({'data': {'math': {'sum': 21e50}}}, result)

        result = GraphQlExecutor.execute(
            '{math {intSum(numbers: [1, 13, -5, 0, -0, 42, 1234567890])}}',
            context)
        self.assertEqual({'data': {'math': {'intSum': 1234567941}}}, result)

        result = GraphQlExecutor.execute(
            '{math {intSum(numbers: [1e1, 5])}}', context)
        self._validate_error_response(result)

        result = GraphQlExecutor.execute(
            '{math {sum(numbers: [00, 1])}}', context)
        self._validate_error_response(result)

        result = GraphQlExecutor.execute(
            '{math {sum(numbers: [.3, 12])}}', context)
        self._validate_error_response(result)

    def test_scalar_coercion(self):
        """Test GraphQlExecutor on coercing scalar values."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.scalar_descriptors.time_span',
            'graphql.executor.test.scalar_descriptors.time_span_descriptor',
            'graphql.scalar_descriptors.strict'])
        context = SilentGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            '{testTimeSpan {timeSum(intervals: '
            '[{number: 1.5, unit: SECONDS}, {number: 2, unit: DAYS}],'
            'times: [123, 456.7])}}',
            context)
        self.assertEqual(
            {'data': {'testTimeSpan': {'timeSum': 173381.2}}}, result)

        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.scalar_descriptors.time_span',
            'graphql.executor.test.scalar_descriptors.'
            'broken_time_span_descriptor',
            'graphql.scalar_descriptors.strict'])
        context = SilentGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            '{testTimeSpan {timeSum(times: [123])}}', context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual(
            'GraphQlBadScalarDescriptorError', result['errors'][0]['type'])
        self.assertIsNone(result['data'])

        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.numbers',
            'graphql.executor.test.scalar_descriptors.float_descriptor',
            'graphql.scalar_descriptors.strict.boolean',
            'graphql.scalar_descriptors.strict.id',
            'graphql.scalar_descriptors.strict.int',
            'graphql.scalar_descriptors.strict.string'])
        context = SilentGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            '{math {sum(numbers: ["1", 2.5])}}', context)
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlParseError', result['errors'][0]['type'])

        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.numbers',
            'graphql.executor.test.scalar_descriptors.int_descriptor',
            'graphql.scalar_descriptors.strict.boolean',
            'graphql.scalar_descriptors.strict.float',
            'graphql.scalar_descriptors.strict.id',
            'graphql.scalar_descriptors.strict.string'])
        context = SilentGraphQlContext(schema)
        result = GraphQlExecutor.execute(
            '{math {intSum(numbers: [1, 2])}}', context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual(
            'GraphQlBadScalarDescriptorError', result['errors'][0]['type'])
        self.assertEqual({'math': {'intSum': None}}, result['data'])

        context = self._extra_context()
        result = GraphQlExecutor.execute('{ship(id: 3000) {name}}', context)
        self.assertEqual(
            {'data': {'ship': {'name': 'Millennium Falcon'}}}, result)

        context = SilentGraphQlContext(self._extra_schema())
        result = GraphQlExecutor.execute('{ship(id: 3000.0) {name}}', context)
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlParseError', result['errors'][0]['type'])
