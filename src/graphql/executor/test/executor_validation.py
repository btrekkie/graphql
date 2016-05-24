import unittest

from graphql.document import GraphQlParser
from graphql.executor import GraphQlExecutor
from graphql.schema import GraphQlSchemaFactory
from graphql.executor.test.star_wars_extra import SwUsers
from silent_context import SilentGraphQlContext


class GraphQlExecutorValidationTest(unittest.TestCase):
    """Tests GraphQlExecutor concerning generation of errors."""

    def _schema(self):
        """Return a GraphQlSchema for the "star_wars" module."""
        return GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.scalar_descriptors.strict'])

    def _context(self):
        """Return a SilentGraphQlContext for the "star_wars" module."""
        return SilentGraphQlContext(self._schema())

    def _extra_context(self):
        """Return a SilentGraphQlContext for the "star_wars_extra" module."""
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.executor.test.star_wars_extra',
            'graphql.scalar_descriptors.strict'])
        return SilentGraphQlContext(schema)

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

    def _validate_parse_error_response(self, graphql_response):
        """Assert the specified value is a valid GraphQL parse error response.

        Assert the specified value is a valid GraphQL error response for
        a GraphQlParseError generated using a SilentGraphQlContext.
        This only performs basic validation.  For example, it does not
        verify that the entire response is a JSON value.
        """
        self.assertEqual(['errors'], list(graphql_response.iterkeys()))
        self.assertEqual(1, len(graphql_response['errors']))
        self.assertEqual(
            'GraphQlParseError', graphql_response['errors'][0]['type'])

    def _validate_non_error_response(self, graphql_response):
        """Assert the given value is a valid GraphQL response without errors.

        This only performs basic validation.  For example, it does not
        verify that the entire response is a JSON value.
        """
        self.assertTrue(
            set(graphql_response.iterkeys()).issubset(
                set(['data', 'extensions'])))
        self.assertTrue('data' in graphql_response)
        self.assertIsNotNone(graphql_response['data'])

    def test_validation(self):
        """Test GraphQlExecutor on document syntax validation."""
        context = self._context()
        result = GraphQlExecutor.execute(
            "query NestedQueryWithFragment {\n"
            "    hero {\n"
            "        ...NameAndAppearances\n"
            "        friends {\n"
            "            ...NameAndAppearances\n"
            "            friends {\n"
            "                ...NameAndAppearances\n"
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n"
            "\n"
            "fragment NameAndAppearances on Character {\n"
            "    name\n"
            "    appearsIn\n"
            "}\n",
            context)
        self._validate_non_error_response(result)

        result = GraphQlExecutor.execute(
            "query HeroSpaceshipQuery {\n"
            "    hero {\n"
            "        favoriteSpaceship\n"
            "    }\n"
            "}\n",
            context)
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlParseError', result['errors'][0]['type'])

        result = GraphQlExecutor.execute(
            "query HeroNoFieldsQuery {\n"
            "    hero\n"
            "}\n",
            context)
        self._validate_parse_error_response(result)

        result = GraphQlExecutor.execute(
            "query HeroFieldsOnScalarQuery {\n"
            "    hero {\n"
            "        name {\n"
            "            firstCharacterOfName\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self._validate_parse_error_response(result)

        result = GraphQlExecutor.execute(
            "query DroidFieldOnCharacter {\n"
            "    hero {\n"
            "        name\n"
            "        primaryFunction\n"
            "    }\n"
            "}\n",
            context)
        self._validate_parse_error_response(result)

        result = GraphQlExecutor.execute(
            "query DroidFieldInFragment {\n"
            "    hero {\n"
            "        name\n"
            "        ...DroidFields\n"
            "    }\n"
            "}\n"
            "\n"
            "fragment DroidFields on Droid {\n"
            "    primaryFunction\n"
            "}\n",
            context)
        self._validate_non_error_response(result)

        result = GraphQlExecutor.execute(
            "query DroidFieldInFragment {\n"
            "    hero {\n"
            "        name\n"
            "        ... on Droid {\n"
            "            primaryFunction\n"
            "        }\n"
            "    }\n"
            "}\n",
            context)
        self._validate_non_error_response(result)

        result = GraphQlExecutor.execute('', context)
        self._validate_parse_error_response(result)

        result = GraphQlExecutor.execute(
            '{human(id: "1000"){name}}', context, {'foo': '1000'})
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlVariablesError', result['errors'][0]['type'])

        result = GraphQlExecutor.execute(
            '($foo: String!) {human(id: $foo){name}}', context, {})
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlVariablesError', result['errors'][0]['type'])

        result = GraphQlExecutor.execute(
            '($foo: String!) {human(id: $foo){name}}', context, {'foo': 123})
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlVariablesError', result['errors'][0]['type'])

        result = GraphQlExecutor.execute(
            'query foo {human(id: "1000"){name}}'
            'query bar {human(id: "1000"){name}}',
            context, {})
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual(
            'GraphQlOperationNameError', result['errors'][0]['type'])

        result = GraphQlExecutor.execute(
            'query foo {human(id: "1000"){name}}'
            'query bar {human(id: "1000"){name}}',
            context, {}, 'baz')
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual(
            'GraphQlOperationNameError', result['errors'][0]['type'])

        result = GraphQlExecutor.execute(
            'query foo {human(id: "1000"){name}}', context, {}, 'bar')
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual(
            'GraphQlOperationNameError', result['errors'][0]['type'])

    def test_broken_fields(self):
        """Test GraphQlExecutor on fields that return the wrong type of object.

        Test GraphQlExecutor on fields that return the wrong type of
        object or raise an exception.
        """
        context = self._extra_context()
        result = GraphQlExecutor.execute('{fastestShip{name}}', context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlFieldTypeError', result['errors'][0]['type'])
        self.assertIsNone(result['data'])

        result = GraphQlExecutor.execute(
            '{slowestShip{name}, ship(id: "3000"){name}}', context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlFieldTypeError', result['errors'][0]['type'])
        self.assertIsNone(result['data'])

        result = GraphQlExecutor.execute('{allShips{name}}', context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlFieldTypeError', result['errors'][0]['type'])
        self.assertIsNone(result['data'])

        result = GraphQlExecutor.execute(
            '{largestShip{name}, ship(id: "3000"){name}}', context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('RuntimeError', result['errors'][0]['type'])
        self.assertEqual(
            {'largestShip': None, 'ship': {'name': 'Millennium Falcon'}},
            result['data'])

        result = GraphQlExecutor.execute(
            '{ship(id: "3000"){brokenId, name}}', context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('GraphQlFieldTypeError', result['errors'][0]['type'])
        self.assertIsNone(result['data'])

    def test_schema_mismatch(self):
        """Test the case where GraphQlDocument.schema != GraphQlContext.schema.
        """
        document = GraphQlParser('{hero{name}}', self._schema()).parse()
        context = self._extra_context()
        result = GraphQlExecutor.execute_document(document, context)
        self.assertEqual(['errors'], list(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual(
            'GraphQlSchemaMismatchError', result['errors'][0]['type'])

    def test_result_with_errors(self):
        """Test GraphQlResultWithErrors."""
        SwUsers.reset()
        context = self._extra_context()
        result = GraphQlExecutor.execute(
            'mutation {register(email: "foo@example.com", password: "abc", '
            'captchaToken: "def456")}',
            context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('ValueError', result['errors'][0]['type'])
        self.assertEqual({'register': False}, result['data'])

        result = GraphQlExecutor.execute(
            'mutation {register(email: "bar@example.com", password: "anikin", '
            'captchaToken: "def456")}',
            context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('ValueError', result['errors'][0]['type'])
        self.assertEqual({'register': True}, result['data'])

        result = GraphQlExecutor.execute(
            'mutation {register(email: "foo@example.com", password: "anikin", '
            'captchaToken: "abc123")}',
            context)
        self.assertEqual(set(['data', 'errors']), set(result.iterkeys()))
        self.assertEqual(1, len(result['errors']))
        self.assertEqual('ValueError', result['errors'][0]['type'])
        self.assertEqual({'register': True}, result['data'])

        result = GraphQlExecutor.execute(
            'mutation {register(email: "bar@example.com", password: "anikin", '
            'captchaToken: "abc123")}',
            context)
        self.assertEqual(['data'], list(result.iterkeys()))
        self.assertEqual({'register': True}, result['data'])
