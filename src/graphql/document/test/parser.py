import unittest

from graphql.document import GraphQlParser
from graphql.document import GraphQlFieldQuery
from graphql.document import GraphQlFragmentReference
from graphql.document import GraphQlParseError
from graphql.schema import GraphQlSchemaFactory


class GraphQlParserTest(unittest.TestCase):
    def _schema(self):
        """Return a GraphQlSchema for the "star_wars" module."""
        return GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.scalar_descriptors.strict'])

    def test_valid(self):
        """Test GraphQlParser.parse() on valid documents."""
        schema = GraphQlSchemaFactory.create_from_modules(
            [
                'graphql.executor.test.star_wars',
                'graphql.scalar_descriptors.strict'],
            'Query')
        document = GraphQlParser('{human(id: "1000"){id}}', schema).parse()
        self.assertEqual(schema, document.schema)
        self.assertEqual(1, len(document.operations))
        operation = document.operations[0]
        self.assertIsNone(operation.name)
        self.assertEqual({}, operation.variables)
        self.assertEqual([], operation.directives)
        self.assertEqual(
            1, len(operation.selection_set.field_queries_and_fragments))
        self.assertEqual('Query', operation.selection_set.base_type.name)
        human_field_query = (
            operation.selection_set.field_queries_and_fragments[0])
        self.assertIsInstance(human_field_query, GraphQlFieldQuery)
        self.assertEqual('human', human_field_query.response_key)
        self.assertEqual('human', human_field_query.field_descriptor.name)
        self.assertEqual(['id'], list(human_field_query.args.keys()))
        self.assertEqual('1000', human_field_query.args['id'])
        self.assertEqual([], human_field_query.directives)
        self.assertEqual(
            1,
            len(human_field_query.selection_set.field_queries_and_fragments))
        id_field_query = (
            human_field_query.selection_set.field_queries_and_fragments[0])
        self.assertIsInstance(id_field_query, GraphQlFieldQuery)
        self.assertEqual('id', id_field_query.response_key)
        self.assertEqual('id', id_field_query.field_descriptor.name)
        self.assertEqual({}, id_field_query.args)
        self.assertEqual([], id_field_query.directives)
        self.assertIsNone(id_field_query.selection_set)

        document = GraphQlParser(
            'query foo {human(id: "1000")'
            '{bar: id, ... on Human {homePlanet}}}',
            schema).parse()
        self.assertEqual(schema, document.schema)
        self.assertEqual(1, len(document.operations))
        operation = document.operations[0]
        self.assertEqual('foo', operation.name)
        self.assertEqual({}, operation.variables)
        self.assertEqual([], operation.directives)
        self.assertEqual(
            1, len(operation.selection_set.field_queries_and_fragments))
        self.assertEqual('Query', operation.selection_set.base_type.name)
        human_field_query = (
            operation.selection_set.field_queries_and_fragments[0])
        self.assertIsInstance(human_field_query, GraphQlFieldQuery)
        self.assertEqual('human', human_field_query.response_key)
        self.assertEqual('human', human_field_query.field_descriptor.name)
        self.assertEqual(['id'], list(human_field_query.args.keys()))
        self.assertEqual('1000', human_field_query.args['id'])
        self.assertEqual([], human_field_query.directives)
        self.assertEqual(
            2,
            len(human_field_query.selection_set.field_queries_and_fragments))
        id_field_query = (
            human_field_query.selection_set.field_queries_and_fragments[0])
        self.assertIsInstance(id_field_query, GraphQlFieldQuery)
        self.assertEqual('bar', id_field_query.response_key)
        self.assertEqual('id', id_field_query.field_descriptor.name)
        self.assertEqual({}, id_field_query.args)
        self.assertEqual([], id_field_query.directives)
        self.assertIsNone(id_field_query.selection_set)
        fragment_reference = (
            human_field_query.selection_set.field_queries_and_fragments[1])
        self.assertIsInstance(fragment_reference, GraphQlFragmentReference)
        self.assertEqual([], fragment_reference.directives)
        fragment = fragment_reference.fragment
        self.assertEqual(
            1, len(fragment.selection_set.field_queries_and_fragments))
        home_planet_field_query = (
            fragment.selection_set.field_queries_and_fragments[0])
        self.assertIsInstance(home_planet_field_query, GraphQlFieldQuery)
        self.assertEqual('homePlanet', home_planet_field_query.response_key)
        self.assertEqual(
            'homePlanet', home_planet_field_query.field_descriptor.name)
        self.assertEqual({}, home_planet_field_query.args)
        self.assertEqual([], home_planet_field_query.directives)
        self.assertIsNone(home_planet_field_query.selection_set)

    def test_no_errors(self):
        """Ensure that GraphQlParser doesn't raise on valid documents."""
        schema = self._schema()

        # Make sure none of the following raises a GraphQlParseError
        GraphQlParser('query {human(id: "1000"){id}}', schema).parse()
        GraphQlParser('{human(id: "1000"){__typename}}', schema).parse()
        GraphQlParser(
            "{human,   (,id,:, \"1000\\n\",)\t\n\r\n,{,id,},},",
            schema).parse()
        GraphQlParser(
            '{human(id: "1000"){id, ... on Human {homePlanet}}}',
            schema).parse()
        GraphQlParser(
            '{human(id: "1000"){id, ... on Human {id}}}', schema).parse()
        GraphQlParser(
            '{human(id: "1000"){id, ... on Character '
            '{... on Human {homePlanet}}}}',
            schema).parse()
        GraphQlParser(
            'query ($foo: String!) {human(id: $foo){id, ...HumanFields}} '
            'fragment HumanFields on Human {homePlanet}',
            schema).parse()
        GraphQlParser(
            'query ($foo: String!) {...rootFields} '
            'fragment rootFields on Query '
            '{human(id: $foo){...HumanFields}}'
            'fragment HumanFields on Human {homePlanet}',
            schema).parse()
        GraphQlParser(
            'query foo {human(id: "1000"){id}} '
            'query bar {human(id: "1001"){id}}',
            schema).parse()
        GraphQlParser(
            '{human(id: "1000"){id}, '
            'human(id: "1000"){... on Human{homePlanet}}}',
            schema).parse()
        GraphQlParser(
            'query($foo: Boolean!) '
            '{human(id: "1000"){id @include(if: $foo)}}',
            schema).parse()
        GraphQlParser(
            'query($foo: Boolean = true) '
            '{human(id: "1000"){id @include(if: $foo)}}',
            schema).parse()
        GraphQlParser(
            "{human(id: \"1000\") # The human\n"
            "{id # The ID\n"
            '}}',
            schema).parse()
        GraphQlParser('{human(id: "#1000"){id}}', schema).parse()

    def test_invalid_syntax(self):
        """Ensure that GraphQlParser raises on invalid syntax."""
        schema = self._schema()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000"){id}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000"){id}}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000"){}}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('query foo() {human(id: "1000"){}}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000"){id{}}}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000") # {id}}}', schema).parse()

    def test_invalid_operation_naming(self):
        """Ensure GraphQlParser raises on invalid operation naming."""
        schema = self._schema()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query foo {human(id: "1000"){id}} '
                'query foo {human(id: "1000"){id}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query foo {human(id: "1000"){id}} '
                'query {human(id: "1000"){id}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query {human(id: "1000"){id}} '
                'query foo {human(id: "1000"){id}}',
                schema).parse()

    def test_invalid_field_queries(self):
        """Ensure GraphQlParser raises on invalid field queries."""
        schema = self._schema()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000")'
                '{id, ... on Human{... on Character {homePlanet}}}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000"){homePlanet}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){... on Human {homePlanet}, '
                '... on Human {homePlanet: date}}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){id}, human(id: "1001"){id}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000")}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human(id: "1000"){id{foo}}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){id{__typename}}}', schema).parse()

    def test_invalid_args(self):
        """Ensure that GraphQlParser raises on invalid arguments."""
        schema = self._schema()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000", foo: "bar"){id}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000", id: "1000"){id}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('{human{id}}', schema).parse()

    def test_invalid_fragments(self):
        """Ensure that GraphQlParser raises on invalid fragments."""
        schema = self._schema()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){...CharacterFields}} '
                'fragment CharacterFields on Character {id} '
                'fragment CharacterFields on Character {id}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){...CharacterFields}} '
                'fragment CharacterFields on DoesNotExist {id}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){id{...idFields}}} '
                'fragment idFields on ID {foo}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){id}} '
                'fragment CharacterFields on Character {id}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){...CharacterFields}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){...CharacterFields}} '
                'fragment CharacterFields on Character {...CharacterFields}',
                schema).parse()

    def test_invalid_directives(self):
        """Ensure that GraphQlParser raises on invalid directives."""
        schema = self._schema()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '{human(id: "1000"){id @doesNotExist}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                '@include(if: true) {human("123"){id}}', schema).parse()

    def test_invalid_variables(self):
        """Ensure that GraphQlParser raises on invalid variables."""
        schema = self._schema()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query($foo: String!, $foo: String!) {human($foo){id}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query($foo: String! = 123) {human($foo){id}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query($foo: Boolean! = true) '
                '{human(id: "1000"){id @include(if: $foo)}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query($foo: Human) {human($foo){id}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser('query {human(id: $foo){id}}', schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query ($foo: String!) {...rootFields} '
                'fragment rootFields on Query '
                '{human1: human(id: $foo){id}, human2: human(id: $bar){id}}',
                schema).parse()
        with self.assertRaises(GraphQlParseError):
            GraphQlParser(
                'query($foo: ID!) {human(id: $foo){id}}', schema).parse()
