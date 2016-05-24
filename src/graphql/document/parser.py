from directive import GraphQlDirective
from document import GraphQlDocument
from errors import GraphQlParseError
from field_query import GraphQlFieldQuery
from fragment import GraphQlFragment
from fragment_reference import GraphQlFragmentReference
from graphql.schema import GraphQlDirectiveLocation
from graphql.schema import GraphQlEnumType
from graphql.schema import GraphQlInputObjectType
from graphql.schema import GraphQlInterfaceType
from graphql.schema import GraphQlListType
from graphql.schema import GraphQlNonNullType
from graphql.schema import GraphQlObjectType
from graphql.schema import GraphQlScalarType
from graphql.schema import GraphQlSchema
from mutation import GraphQlMutation
from query import GraphQlQuery
from selection_set import GraphQlSelectionSet
from variable import GraphQlVariable
from variable_reference import GraphQlVariableReference


class GraphQlParser(object):
    """A parser for computing the GraphQlDocument for a document string."""

    # In the context of this class, the term "read" refers to taking characters
    # from _document_str starting at _offset, incrementing _offset to the first
    # character after the end of the read portion, and raising an exception if
    # the desired entity was not present.  As a rule, reading should skip any
    # tokens ignored in the GraphQL syntax preceding the desired entity.

    # The number of characters after the problematic portion of the query to
    # include in an error message describing an invalid query.
    _NUM_CONTEXT_CHARS = 50

    # Private attributes:
    # basestring _document_str - The document we are parsing.
    # dict<GraphQlFieldQuery, int> _field_query_offsets - A map from each field
    #     query we have read to the index in _document_str of the start of the
    #     query.
    # dict<basestring, GraphQlFragment> _fragments - A map from the names of
    #     the named fragments we have read to the fragments.
    # dict<GraphQlFragment, int> _fragment_offsets - A map from each named
    #     fragment we have read to the index in _document_str of the start of
    #     its definition.
    # dict<GraphQlFragmentReference, int> _fragment_reference_offsets - A map
    #     from each fragment reference we have read to the index in
    #     _document_str of the start the relevant spread operator.
    # dict<GraphQlFragmentReference, GraphQlBaseType>
    #     _fragment_reference_to_base_type - A map from each fragment reference
    #     we have read to the base type whose fields we are requesting.
    # dict<basestring, list<GraphQlFragmentReference>> _fragment_to_references
    #     - A map from the names of named fragments to the references to those
    #     fragments that we have read.
    # int _offset - The index in _schema of the next character to read.
    # GraphQlSchema _schema - The schema the document is using.
    # dict<GraphQlVariable, int> _variable_offsets - A map from each variable
    #     definition we have read to the index in _document_str of the start of
    #     the definition.
    # dict<GraphQlVariableReference, int> _variable_reference_offsets - A map
    #     from each variable reference we have read to the index in
    #     _document_str of the start of the reference.

    def __init__(self, document_str, schema):
        self._document_str = document_str
        self._schema = schema
        self._offset = 0
        self._fragments = {}
        self._fragment_to_references = {}
        self._fragment_reference_to_base_type = {}
        self._fragment_offsets = {}
        self._fragment_reference_offsets = {}
        self._field_query_offsets = {}
        self._variable_offsets = {}
        self._variable_reference_offsets = {}

    def _raise_exception(self, message, offset):
        """Raise a GraphQlParseError indicating failure to parse the document.

        basestring message - A message indicating what is wrong.
        int offset - The index in _document_str of the start of the
            problematic portion of the query.  This is
            len(_document_str) if the problem was that when we reached
            the end of _document_str, we expected to find additional
            characters.
        """
        lines = '{:s}.'.format(self._document_str[:offset]).splitlines()
        line = len(lines)
        column = len(lines[-1])
        context_str = self._document_str[
            offset:offset + GraphQlParser._NUM_CONTEXT_CHARS]
        raise GraphQlParseError(
            'Error parsing GraphQL query at line {:d}, column {:d}, near '
            '"{:s}": {:s}'.format(line, column, context_str, message),
            self._document_str, line, column)

    def _read_ignored_tokens(self, allow_end_of_string):
        """Read all available ignored tokens starting at _offset.

        Read all ignored tokens (e.g. whitespace and commas) until we
        reach a token that is not an ignored token.

        bool allow_end_of_string - If False, we raise a
            GraphQlParseError if we reach the end of the string.
        """
        is_in_comment = False
        while self._offset < len(self._document_str):
            char = self._document_str[self._offset]
            if char in u"\ufeff \t,":
                pass
            elif char == '#':
                is_in_comment = True
            elif char in "\n\r":
                is_in_comment = False
            elif not is_in_comment:
                break
            self._offset += 1
        if self._offset == len(self._document_str) and not allow_end_of_string:
            self._raise_exception('Unexpected end of document', self._offset)

    def _read_identifier(self):
        """Read a GraphQL identifier, or a keyword such as "on" or "true".

        return basestring - The identifier.
        """
        self._read_ignored_tokens(False)
        prev_offset = self._offset
        while (self._offset < len(self._document_str) and
                self._document_str[self._offset] not in
                u"!$().:=@[]{}\"\ufeff \t,#\n\r"):
            self._offset += 1
        identifier = self._document_str[prev_offset:self._offset]
        if identifier == '':
            self._raise_exception(
                'Expected identifier or keyword', prev_offset)
        elif not GraphQlSchema.is_valid_identifier(identifier):
            self._raise_exception(
                'Invalid GraphQL identifier or keyword.  Identifiers must '
                'consist of letters, digits, and underscores, and may not '
                'begin with a digit.',
                prev_offset)
        else:
            return identifier

    def _read_type(self):
        """Read a GraphQL type.

        return GraphQlType - The type.
        """
        self._read_ignored_tokens(False)
        if self._document_str[self._offset] == '[':
            self._offset += 1
            t = self._read_type()
            self._read_ignored_tokens(False)
            if self._document_str[self._offset] != ']':
                self._raise_exception('Expected "]"', self._offset)
            self._offset += 1
            t = GraphQlListType(t)
        else:
            prev_offset = self._offset
            name = self._read_identifier()
            self._read_ignored_tokens(False)
            try:
                t = self._schema.get_type(name)
            except ValueError:
                self._raise_exception(
                    'There is no type named {:s}'.format(name), prev_offset)
        if self._document_str[self._offset] != '!':
            return t
        else:
            self._offset += 1
            return GraphQlNonNullType(t)

    def _read_field_query(self, base_type):
        """Read a field query.

        GraphQlBaseType base_type - The base type of the object
            containing the field.
        return GraphQlFieldQuery - The field query.
        """
        self._read_ignored_tokens(False)
        start = self._offset
        response_key = self._read_identifier()
        self._read_ignored_tokens(False)
        if self._document_str[self._offset] != ':':
            field_name = response_key
            field_offset = start
        else:
            self._offset += 1
            self._read_ignored_tokens(False)
            field_offset = self._offset
            field_name = self._read_identifier()

        # Compute the GraphQlFieldDescriptor
        field_descriptor = self._schema.common_field_descriptor(field_name)
        if (field_descriptor is None and
                base_type == self._schema.root_query_type()):
            field_descriptor = self._schema.implicit_root_field_descriptor(
                field_name)
        if field_descriptor is None:
            try:
                field_descriptor = base_type.field_descriptor(field_name)
            except ValueError:
                self._raise_exception(
                    '{:s} has no field named {:s}'.format(
                        base_type.name, field_name),
                    field_offset)

        args = self._read_args(field_descriptor.args)
        directives = self._read_directives(GraphQlDirectiveLocation.field)
        selection_set = self._read_selection_set(
            field_descriptor.field_type.base_type())
        field_query = GraphQlFieldQuery(
            response_key, field_descriptor, args, selection_set, directives)
        self._field_query_offsets[field_query] = start
        return field_query

    def _read_fragment_reference(self, base_type):
        """Read a fragment reference.

        GraphQlBaseType base_type - The base type of the object
            containing the fragment fields.
        return GraphQlFragmentReference - The fragment reference.
        """
        name = self._read_identifier()
        if name in self._fragments:
            fragment = self._fragments[name]
        else:
            fragment = GraphQlFragment()
            self._fragments[name] = fragment
        directives = self._read_directives(
            GraphQlDirectiveLocation.fragment_spread)
        fragment_reference = GraphQlFragmentReference(fragment, directives)
        self._fragment_reference_to_base_type[fragment_reference] = base_type
        return fragment_reference

    def _read_selection_set(self, base_type):
        """Read a selection set.

        GraphQlBaseType base_type - The base type of the object
            containing the fields in the selection set.
        return GraphQlSelectionSet - The selection set.
        """
        self._read_ignored_tokens(False)
        if isinstance(base_type, (GraphQlEnumType, GraphQlScalarType)):
            if self._document_str[self._offset] == '{':
                self._raise_exception(
                    'Scalar values do not have fields', self._offset)
            return None
        if self._document_str[self._offset] != '{':
            self._raise_exception(
                'Must specify the {:s} object fields to request'.format(
                    base_type.name),
                self._offset)

        # Read the field queries and fragment references
        field_queries_and_fragments = []
        self._offset += 1
        self._read_ignored_tokens(False)
        while self._document_str[self._offset] != '}':
            fragment_start = self._offset
            if self._document_str[self._offset] != '.':
                # Field query
                field_queries_and_fragments.append(
                    self._read_field_query(base_type))
            elif (self._offset + 2 >= len(self._document_str) or
                    self._document_str[self._offset:self._offset + 3] !=
                    '...'):
                self._raise_exception(
                    'Expected field name or "..."', self._offset)
            else:
                self._offset += 3
                prev_offset = self._offset
                name = self._read_identifier()
                self._offset = prev_offset
                if name == 'on':
                    # Anonymous fragment definition
                    fragment_reference = GraphQlFragmentReference(
                        self._read_fragment(False), [])
                else:
                    # Reference to a named fragment
                    fragment_reference = self._read_fragment_reference(
                        base_type)
                    self._fragment_to_references.setdefault(
                        name, []).append(fragment_reference)
                field_queries_and_fragments.append(fragment_reference)
                self._fragment_reference_offsets[fragment_reference] = (
                    fragment_start)
            self._read_ignored_tokens(False)
        self._offset += 1
        if not field_queries_and_fragments:
            self._raise_exception('Expected field name or "..."', self._offset)
        return GraphQlSelectionSet(base_type, field_queries_and_fragments)

    def _read_str_literal(self):
        """Read a literal string value.

        return basestring - The value.
        """
        self._read_ignored_tokens(False)
        start = self._offset
        if self._document_str[self._offset] != '"':
            self._raise_exception('Expected string literal', self._offset)
        self._offset += 1

        components = []
        while (self._offset < len(self._document_str) and
                self._document_str[self._offset] != '"'):
            prev_offset = self._offset
            char = self._document_str[self._offset]
            self._offset += 1
            if char < ' ' and char not in "\n\r\t":
                self._raise_exception(
                    'String literal contains illegal byte', start)
            elif char != '\\':
                components.append(char)
            elif self._offset >= len(self._document_str):
                self._raise_exception(
                    'Unexpected end of document', self._offset)
            else:
                char = self._document_str[self._offset]
                self._offset += 1
                if char in '"/\\':
                    components.append(char)
                elif char == 'b':
                    components.append("\b")
                elif char == 'f':
                    components.append("\f")
                elif char == 'n':
                    components.append("\n")
                elif char == 'r':
                    components.append("\r")
                elif char == 't':
                    components.append("\t")
                elif char == 'u':
                    if self._offset + 4 >= len(self._document_str):
                        self._raise_exception(
                            'Invalid Unicode escape sequence', prev_offset)
                    hex_code = self._document_str[
                        self._offset:self._offset + 4]
                    try:
                        code = int(hex_code, 16)
                    except ValueError:
                        self._raise_exception(
                            'Invalid Unicode escape sequence', prev_offset)
                    components.append(unichr(code))
                    self._offset += 4

        if self._offset >= len(self._document_str):
            self._raise_exception('Unexpected end of document', self._offset)
        self._offset += 1
        return ''.join(components)

    def _read_float_fraction(self):
        """Read the fractional component of a floating point literal.

        This consists of a decimal point followed by a sequence of
        digits.
        """
        if self._document_str[self._offset] != '.':
            self._raise_exception('Expected "."', self._offset)
        self._offset += 1
        if not ('0' <= self._document_str[self._offset] <= '9'):
            self._raise_exception('Expected digit', self._offset)
        self._offset += 1
        while (self._offset < len(self._document_str) and
                '0' <= self._document_str[self._offset] <= '9'):
            self._offset += 1

    def _read_float_exponent(self):
        """Read the exponent component of a floating point literal.

        This consists of the letter "e" followed by an optional sign and
        a sequence of digits.
        """
        if self._document_str[self._offset] not in 'eE':
            self._raise_exception('Expected "e"', self._offset)
        self._offset += 1
        if self._document_str[self._offset] in '+-':
            self._offset += 1
        if not ('0' <= self._document_str[self._offset] <= '9'):
            self._raise_exception('Expected digit', self._offset)
        self._offset += 1
        while (self._offset < len(self._document_str) and
                '0' <= self._document_str[self._offset] <= '9'):
            self._offset += 1

    def _read_number_literal(self):
        """Read an integer or floating point literal value.

        return number - The value.
        """
        self._read_ignored_tokens(False)
        start = self._offset
        if self._document_str[self._offset] == '-':
            self._offset += 1
            if self._offset >= len(self._document_str):
                self._raise_exception(
                    'Unexpected end of document', self._offset)
        if not ('0' <= self._document_str[self._offset] <= '9'):
            self._raise_exception('Could not parse number literal', start)
        starts_with_zero = self._document_str[self._offset] == '0'
        self._offset += 1

        # Read the integer component
        while self._offset < len(self._document_str):
            char = self._document_str[self._offset]
            if starts_with_zero and char == '0':
                self._raise_exception('Could not parse number literal', start)
            if not ('0' <= char <= '9'):
                break
            self._offset += 1

        is_float = False
        if self._offset < len(self._document_str):
            if self._document_str[self._offset] == '.':
                self._read_float_fraction()
                is_float = True
            if self._document_str[self._offset] in 'eE':
                self._read_float_exponent()
                is_float = True
        if is_float:
            return float(self._document_str[start:self._offset])
        else:
            value = int(self._document_str[start:self._offset])
            if not (-2 ** 31 <= value < 2 ** 31):
                self._raise_exception(
                    'Integer literals must be between -2^31 and 2^31 - 1',
                    start)
            return value

    @staticmethod
    def verified_graphql_to_python(value, scalar_descriptor):
        """Like scalar_descriptor.graphql_to_python(value), but with checks.

        Equivalent to scalar_descriptor.graphql_to_python(value), but it
        first validates the type of "value" if scalar_descriptor.name is
        one of the built-in types: 'String', 'ID', 'Int', 'Float', or
        'Boolean'.

        mixed value - The value.
        GraphQlScalarDescriptor scalar_descriptor - The scalar
            descriptor.
        return mixed - The Python object representation.
        """
        name = scalar_descriptor.name
        if name == 'String':
            if not isinstance(value, basestring):
                raise TypeError('Input is not a string')
        elif name == 'ID':
            if isinstance(value, bool):
                raise TypeError('Input is not a string or an integer')
            elif isinstance(value, (int, long)):
                if not (-2 ** 31 <= value < 2 ** 31):
                    raise ValueError(
                        'In GraphQL, integer values must be between -2^31 and '
                        '2^31 - 1')
            elif not isinstance(value, basestring):
                raise TypeError('Input is not a string or an integer')
        elif name == 'Int':
            if not isinstance(value, (int, long)):
                raise TypeError('Input is not an integer')
            if not (-2 ** 31 <= value < 2 ** 31):
                raise ValueError(
                    'In GraphQL, integer values must be between -2^31 and '
                    '2^31 - 1')
        elif name == 'Float':
            if not isinstance(value, (float, int, long)):
                raise TypeError('Input is not a number')
        elif name == 'Boolean':
            if not isinstance(value, bool):
                raise TypeError('Input is not a boolean')
        return scalar_descriptor.graphql_to_python(value)

    def _read_input_value_recursive(self, t, initial_type, start):
        """Read a variable or literal input value.

        This raises a GraphQlParseError if we read a literal value that
        is not of type "t".  This does not raise an exception if we read
        a variable reference, because we cannot determine the type of
        the variable yet.

        GraphQlType t - The type of the value to read.
        GraphQlType initial_value - The type of value we initially
            started reading.  This differs from "t" if this is a
            recursive call to _read_input_value_recursive.
        int offset - The index in _document_str of the start of the
            literal value we initially started reading.
        return object - The value, as in the entries of
            GraphQlFieldQuery.args.
        """
        self._read_ignored_tokens(False)
        if isinstance(t, GraphQlNonNullType):
            t = t.value_type

        # Handle values other than literal scalars
        if self._document_str[self._offset] == '$':
            # Variable
            prev_offset = self._offset
            self._offset += 1
            reference = GraphQlVariableReference(self._read_identifier())
            self._variable_reference_offsets[reference] = prev_offset
            return reference
        elif self._document_str[self._offset] == '[':
            # List
            if not isinstance(t, GraphQlListType):
                self._raise_exception(
                    'Input value must be of type {:s}'.format(
                        initial_type.type_str()),
                    start)
            value = []
            self._offset += 1
            self._read_ignored_tokens(False)
            while self._document_str[self._offset] != ']':
                value.append(
                    self._read_input_value_recursive(
                        t.element_type, initial_type, start))
                self._read_ignored_tokens(False)
            self._offset += 1
            return value
        elif self._document_str[self._offset] == '{':
            # Input object
            input_object_start = self._offset
            value = {}
            self._offset += 1
            self._read_ignored_tokens(False)
            while self._document_str[self._offset] != '}':
                prev_offset = self._offset
                key = self._read_identifier()
                if key in value:
                    self._raise_exception(
                        'Duplicate object field {:s}'.format(key), prev_offset)
                if key not in t.fields:
                    self._raise_exception(
                        'There is no such field {:s}.{:s}'.format(t.name, key),
                        prev_offset)
                self._read_ignored_tokens(False)
                if self._document_str[self._offset] != ':':
                    self._raise_exception('Expected ":"', self._offset)
                self._offset += 1
                value[key] = self._read_input_value_recursive(
                    t.fields[key], initial_type, start)
                self._read_ignored_tokens(False)
            self._offset += 1

            # Check for required keys
            for key, value_type in t.fields.iteritems():
                if (key not in value and
                        isinstance(value_type, GraphQlNonNullType)):
                    self._raise_exception(
                        'Missing required field {:s}.{:s}'.format(t.name, key),
                        input_object_start)

            return value

        # Read a scalar value
        if self._document_str[self._offset] == '"':
            value = self._read_str_literal()
        elif self._document_str[self._offset] in '-0123456789':
            value = self._read_number_literal()
        else:
            prev_offset = self._offset
            name = self._read_identifier()
            if name == 'true':
                value = True
            elif name == 'false':
                value = False
            elif isinstance(t, GraphQlEnumType):
                # Read an enum value
                try:
                    return t.graphql_to_python(name)
                except ValueError:
                    self._raise_exception(
                        'Expected an enum value of type {:s}'.format(t.name),
                        prev_offset)
            else:
                self._raise_exception('Expected input value', prev_offset)

        # Check whether the value has the desired type
        if isinstance(t, GraphQlScalarType):
            scalar_descriptor = t.scalar_descriptor()
            try:
                return GraphQlParser.verified_graphql_to_python(
                    value, scalar_descriptor)
            except (TypeError, ValueError):
                pass
        self._raise_exception(
            'Input value must be of type {:s}'.format(initial_type.type_str()),
            start)

    def _read_input_value(self, t):
        """Read a variable or literal input value.

        This raises a GraphQlParseError if we read a literal value that
        is not of type "t".  This does not raise an exception if we read
        a variable reference, because we cannot determine the type of
        the variable yet.

        GraphQlType t - The type of the value to read.
        return object - The value, as in the entries of
            GraphQlFieldQuery.args.
        """
        return self._read_input_value_recursive(t, t, self._offset)

    def _read_args(self, types):
        """Read an optional list of argument values.

        Raise a GraphQlParseError if we are missing a required argument.

        dict<basestring, GraphQlType> types - A map from the name of
            each of the available arguments to their types.
        return dict<basestring, GraphQlValue> - A map from the names of
            the variables to their values.
        """
        self._read_ignored_tokens(False)
        start = self._offset
        args = {}
        if self._document_str[self._offset] == '(':
            self._offset += 1
            self._read_ignored_tokens(False)
            while self._document_str[self._offset] != ')':
                # Read the argument name
                prev_offset = self._offset
                name = self._read_identifier()
                if name not in types:
                    self._raise_exception(
                        'Argument {:s} is not available'.format(name),
                        prev_offset)
                if name in args:
                    self._raise_exception(
                        'Duplicate argument {:s}'.format(name), prev_offset)

                self._read_ignored_tokens(False)
                if self._document_str[self._offset] != ':':
                    self._raise_exception('Expected ":"', self._offset)
                self._offset += 1

                # Read the argument value
                value = self._read_input_value(types[name])
                args[name] = value
                self._read_ignored_tokens(False)
            if not args:
                self._raise_exception('Expected argument name', self._offset)
            self._offset += 1

        # Check required arguments
        for name, t in types.iteritems():
            if name not in args and isinstance(t, GraphQlNonNullType):
                self._raise_exception(
                    'Missing required argument {:s}'.format(name), start)
        return args

    def _read_directives(self, location):
        """Read an optional list of directives.

        GraphQlDirectiveLocation location - The location from which we
            are reading.
        return list<GraphQlDirective> - The directives.
        """
        directives = []
        self._read_ignored_tokens(False)
        while self._document_str[self._offset] == '@':
            prev_offset = self._offset
            self._offset += 1
            name = self._read_identifier()
            directive_type = self._schema.directive(name)
            if directive_type is None:
                self._raise_exception(
                    'Unknown directive @{:s}'.format(name), prev_offset)
            if location not in directive_type.locations:
                self._raise_exception(
                    'The directive @{:s} is not supported in this '
                    'location'.format(name),
                    prev_offset)
            args = self._read_args(directive_type.args)
            directives.append(GraphQlDirective(directive_type, args))
            self._read_ignored_tokens(False)
        return directives

    def _has_variable_reference(self, value):
        """Return whether the specified value contains a variable reference.

        obj value - The value, formatted as in GraphQlFieldQuery.args.
        return - Whether the value has a variable reference.
        """
        if isinstance(value, GraphQlVariableReference):
            return True
        elif isinstance(value, list):
            for element in value:
                if self._has_variable_reference(element):
                    return True
            return False
        elif isinstance(value, dict):
            for entry in value.itervalues():
                if self._has_variable_reference(entry):
                    return True
            return False
        else:
            return False

    def _read_variable(self):
        """Read a variable definition.

        return GraphQlVariable - The variable.
        """
        self._read_ignored_tokens(False)
        start = self._offset
        if self._document_str[self._offset] != '$':
            self._raise_exception('Expected "$"', self._offset)
        self._offset += 1
        name = self._read_identifier()
        self._read_ignored_tokens(False)
        if self._document_str[self._offset] != ':':
            self._raise_exception('Expected ":"', self._offset)
        self._offset += 1

        # Read the type
        self._read_ignored_tokens(False)
        prev_offset = self._offset
        t = self._read_type()
        base_type = t.base_type()
        if (not isinstance(base_type, GraphQlScalarType) and
                not isinstance(base_type, GraphQlEnumType) and
                not isinstance(base_type, GraphQlInputObjectType)):
            self._raise_exception(
                'Variable does not have an input type', prev_offset)

        # Read the default value
        self._read_ignored_tokens(False)
        if self._document_str[self._offset] != '=':
            default_value = None
        elif isinstance(t, GraphQlNonNullType):
            self._raise_exception(
                'Variables that have default values may not have a non-null '
                'type',
                self._offset)
        else:
            self._offset += 1
            self._read_ignored_tokens(False)
            prev_offset = self._offset
            default_value = self._read_input_value(t)
            if self._has_variable_reference(default_value):
                self._raise_exception(
                    'The default value may not contain any variable '
                    'references',
                    prev_offset)

        variable = GraphQlVariable(name, t, default_value)
        self._variable_offsets[variable] = start
        return variable

    def _read_variables(self):
        """Read the variables definitions for a GraphQL operation.

        return dict<basestring, GraphQlVariable> - A map from the names
            of the variables to the variables.
        """
        self._read_ignored_tokens(False)
        variables = {}
        if self._document_str[self._offset] == '(':
            self._offset += 1
            self._read_ignored_tokens(False)
            while self._document_str[self._offset] != ')':
                prev_offset = self._offset
                variable = self._read_variable()
                if variable.name in variables:
                    self._raise_exception(
                        'Duplicate variable {:s}'.format(variable.name),
                        prev_offset)
                variables[variable.name] = variable
                self._read_ignored_tokens(False)
            if not variables:
                self._raise_exception('Expected "$"', self._offset)
            self._offset += 1
        return variables

    def _read_query(self):
        """Read a query operation.

        return GraphQlQuery - The query.
        """
        self._read_ignored_tokens(False)
        if self._document_str[self._offset] not in '(@{':
            prev_offset = self._offset
            if self._read_identifier() != 'query':
                self._raise_exception('Expected "query"', prev_offset)
            self._read_ignored_tokens(False)
        if self._document_str[self._offset] in '(@{':
            name = None
        else:
            name = self._read_identifier()
            self._read_ignored_tokens(False)

        variables = self._read_variables()
        directives = self._read_directives(GraphQlDirectiveLocation.query)
        selection_set = self._read_selection_set(
            self._schema.root_query_type())
        return GraphQlQuery(name, variables, selection_set, directives)

    def _read_mutation(self):
        """Read a mutation operation.

        return GraphQlMutation - The mutation.
        """
        self._read_ignored_tokens(False)
        prev_offset = self._offset
        if self._read_identifier() != 'mutation':
            self._raise_exception('Expected "mutation"', prev_offset)
        self._read_ignored_tokens(False)
        if self._document_str[self._offset] in '(@{':
            name = None
        else:
            name = self._read_identifier()
            self._read_ignored_tokens(False)
        variables = self._read_variables()
        directives = self._read_directives(GraphQlDirectiveLocation.mutation)
        mutation_type = self._schema.root_mutation_type()
        if mutation_type is None:
            self._raise_exception(
                'The GraphQL schema does not have any mutations', prev_offset)
        selection_set = self._read_selection_set(mutation_type)
        return GraphQlMutation(name, variables, selection_set, directives)

    def _read_fragment(self, is_named):
        """Read a fragment definition.

        boolean is_named - Whether to read a named fragment definition.
        return GraphQlFragment - The fragment.
        """
        if not is_named:
            location = GraphQlDirectiveLocation.inline_fragment
            fragment = GraphQlFragment()
        else:
            location = GraphQlDirectiveLocation.fragment_definition
            self._read_ignored_tokens(False)
            start = self._offset
            identifier = self._read_identifier()
            if identifier != 'fragment':
                self._raise_exception('Expected "fragment"', start)
            prev_offset = self._offset
            name = self._read_identifier()
            if name == 'on':
                self._raise_exception(
                    'A fragment may not be named "on"', prev_offset)
            fragment = self._fragments.setdefault(name, GraphQlFragment())
            if fragment.object_type is not None:
                self._raise_exception(
                    'Multiple fragments named {:s}'.format(name), prev_offset)
            self._fragment_offsets[fragment] = start

        self._read_ignored_tokens(False)
        prev_offset = self._offset
        identifier = self._read_identifier()
        if identifier != 'on':
            self._raise_exception('Expected "on"', prev_offset)
        self._read_ignored_tokens(False)
        prev_offset = self._offset
        t = self._read_type()
        if not isinstance(t, (GraphQlInterfaceType, GraphQlObjectType)):
            self._raise_exception(
                'Fragment type is not an object, interface, or union type',
                prev_offset)
        directives = self._read_directives(location)
        selection_set = self._read_selection_set(t)
        fragment.object_type = t
        fragment.selection_set = selection_set
        fragment.directives = directives
        return fragment

    def _read_operation_or_fragment(self):
        """Read an operation or a named fragment.

        return GraphQlOperation - The operation we read, or null if we
            read a fragment.
        """
        self._read_ignored_tokens(False)
        if self._document_str[self._offset] in '{(@':
            return self._read_query()
        else:
            prev_offset = self._offset
            identifier = self._read_identifier()
            self._offset = prev_offset
            if identifier == 'query':
                return self._read_query()
            elif identifier == 'mutation':
                return self._read_mutation()
            elif identifier == 'fragment':
                self._read_fragment(True)
                return None
            else:
                self._raise_exception(
                    'Expected "query", "mutation", or "fragment"', prev_offset)

    def _read_operations_and_fragments(self):
        """Read a sequence of operations and / or fragments.

        return list<GraphQlOperation> - The operations we read.
        """
        operations = []
        operation_names = set()
        self._read_ignored_tokens(False)
        anonymous_offset = None
        while self._offset < len(self._document_str):
            prev_offset = self._offset
            operation = self._read_operation_or_fragment()
            if operation is not None:
                # Validate the "one anonymous operation" rule
                if operation.name is None and anonymous_offset is None:
                    anonymous_offset = prev_offset
                if (operations and
                        (operation.name is None or None in operation_names)):
                    if operations:
                        self._raise_exception(
                            'An operation may only be anonymous if it is the '
                            'only one',
                            anonymous_offset)
                if operation.name in operation_names:
                    self._raise_exception(
                        'There are multiple operations named {:s}'.format(
                            operation.name),
                        prev_offset)

                operations.append(operation)
                operation_names.add(operation.name)
            self._read_ignored_tokens(True)
        return operations

    def _add_named_fragment_references(
            self, selection_set, named_fragments, fragments):
        """Add all named fragments the specified selection set references.

        Add all named fragments the specified selection set directly
        references to "fragments", including those appearing in nested
        anonymous fragments and selection sets, but excluding those
        appearing in nested references to named fragments.

        GraphQlSelectionSet selection_set - The selection set.
        set<GraphQlFragment> named_fragments - The named fragment
            definitions.  Equivalent to set(self._fragments.values()).
        set<GraphQlFragment> - The set to which to add the referenced
            fragments.
        """
        for field_query_or_fragment in (
                selection_set.field_queries_and_fragments):
            if isinstance(field_query_or_fragment, GraphQlFieldQuery):
                if field_query_or_fragment.selection_set is not None:
                    self._add_named_fragment_references(
                        field_query_or_fragment.selection_set, named_fragments,
                        fragments)
            elif field_query_or_fragment.fragment in named_fragments:
                fragments.add(field_query_or_fragment.fragment)
            else:
                self._add_named_fragment_references(
                    field_query_or_fragment.fragment.selection_set,
                    named_fragments, fragments)

    def _assert_no_fragment_cycle(
            self, fragment, path, path_set, fragment_to_references, visited):
        """Raise a GraphQlParseError if there is a fragment cycle.

        Raise a GraphQlParseError if the graph from fragment to
        referenced fragment forms a cycle.

        GraphQlFragment fragment - The fragment at which to begin the
            search.
        list<GraphQlFragment> path - The sequence of fragments we
            traversed to reach "fragment".  This does not contain
            "fragment" if the path does not have a cycle.  This method
            may alter "path", but it must restore the original value
            before it finishes.
        set<GraphQlFragment> path_set - The set of fragments in "path".
            This method may alter path_set, but it must restore the
            original value before it finishes.
        dict<GraphQlFragment, set<GraphQlFragment>>
            fragment_to_references - A map from each fragment to the
            fragments it references, as in
            _add_named_fragment_references.  This must have an entry for
            each named fragment, even if it is an empty set.
        set<GraphQlFragment> visited - The fragments we have reached so
            far.
        """
        if fragment in path_set:
            # Raise an exception
            cycle = path[path.index(fragment):]
            fragment_to_name = {}
            for name, fragment in self._fragments.iteritems():
                fragment_to_name[fragment] = name
            cycle_names = list(
                [fragment_to_name[fragment] for fragment in cycle])
            self._raise_exception(
                'Fragment cycle detected: {:s}'.format(
                    ' => '.join(cycle_names + [cycle_names[0]])),
                self._fragment_offsets[fragment])
        elif fragment not in visited:
            visited.add(fragment)
            path.append(fragment)
            path_set.add(fragment)
            for reference in fragment_to_references[fragment]:
                self._assert_no_fragment_cycle(
                    reference, path, path_set, fragment_to_references, visited)
            path.pop()
            path_set.remove(fragment)

    def _append_literal_variable_uses(
            self, arg_name, value, t, source, variable_uses):
        """Append the variable references in the specified value.

        Append information about the variable references appearing in
        the specified argument value to variable_uses.

        basestring arg_name - The name of the argument in which "value"
            appears.
        object value - The argument value, formatted as in the entries
            of GraphQlFieldQuery.args.
        GraphQlType t - The required type of "value".
        basestring source - A string indicating what this is the
            argument to, e.g. 'Foo{bar}'.  We only use this for
            exception messages.
        list<dict<basestring, object>> variable_uses - The list to which
            to append the variable references, formatted as in the
            variable_uses argument to _append_variable_uses.
        """
        if isinstance(value, GraphQlVariableReference):
            variable_uses.append({
                'arg': arg_name,
                'name': value.name,
                'offset': self._variable_reference_offsets[value],
                'source': source,
                'type': t,
            })
        else:
            if isinstance(t, GraphQlNonNullType):
                t = t.value_type
            if isinstance(value, list):
                for element in value:
                    self._append_literal_variable_uses(
                        arg_name, element, t.element_type, source,
                        variable_uses)
            elif isinstance(value, dict):
                for entry in value.itervalues():
                    self._append_literal_variable_uses(
                        arg_name, entry, t, source, variable_uses)

    def _append_arg_variable_uses(
            self, args, arg_values, source, variable_uses):
        """Append the variable references in the specified argument values.

        Append information about the variable references appearing in
        the specified argument values to variable_uses.

        dict<basestring, GraphQlType> args - A map from the name of each
            available argument to its required type.
        dict<basestring, object> arg_values - A map from the name of
            each supplied argument to its value, as in
            GraphQlFieldQuery.args.
        basestring source - A string indicating what these are the
            arguments to, e.g. 'Foo{bar}'.  We only use this for
            exception messages.
        list<dict<basestring, object>> variable_uses - The list to which
            to append the variable references, formatted as in the
            variable_uses argument to _append_variable_uses.
        """
        for name, arg in arg_values.iteritems():
            self._append_literal_variable_uses(
                name, arg, args[name], source, variable_uses)

    def _append_directive_variable_uses(self, directives, variable_uses):
        """Append the variable references in the specified directives.

        Append information about the variable references appearing in
        the argument values to the specified directives to
        variable_uses.

        list<GraphQlDirective> directives - The directives.
        list<dict<basestring, object>> variable_uses - The list to which
            to append the variable references, formatted as in the
            variable_uses argument to _append_variable_uses.
        """
        for directive in directives:
            self._append_arg_variable_uses(
                directive.directive_type.args, directive.args,
                'the {:s} directive'.format(directive.directive_type.name),
                variable_uses)

    def _append_variable_uses(
            self, selection_set, named_fragments, variable_uses):
        """Append the variable references in the specified selection set.

        Append information about the variable references appearing in
        the specified selection set to variable_uses.  We search all
        field queries, nested selection sets, and nested anonymous
        fragments, but not nested references to named fragments.

        GraphQlSelectionSet selection_set - The selection set.
        set<GraphQlFragment> named_fragments - The named fragment
            definitions.  Equivalent to set(self._fragments.values()).
        list<dict<basestring, object>> variable_uses - The list to which
            to append the variable references.  Each element has the
            following entries:

            arg: The name of the argument in which the variable
                reference appears.
            name: The name of the variable.
            offset: The index in _document_str of the start of the
                variable reference.
            source: A string indicating what the argument is to, e.g.
                'Foo{bar}'.  We only use this for exception messages.
            type: The required type of the variable.
        """
        for field_query_or_fragment in (
                selection_set.field_queries_and_fragments):
            self._append_directive_variable_uses(
                field_query_or_fragment.directives, variable_uses)
            if isinstance(field_query_or_fragment, GraphQlFieldQuery):
                field_descriptor = field_query_or_fragment.field_descriptor
                self._append_arg_variable_uses(
                    field_descriptor.args, field_query_or_fragment.args,
                    '{:s}{{{:s}}}'.format(
                        selection_set.base_type.name,
                        field_descriptor.name),
                    variable_uses)
                if field_query_or_fragment.selection_set is not None:
                    self._append_variable_uses(
                        field_query_or_fragment.selection_set, named_fragments,
                        variable_uses)
            elif field_query_or_fragment.fragment not in named_fragments:
                self._append_variable_uses(
                    field_query_or_fragment.fragment.selection_set,
                    named_fragments, variable_uses)

    def _validate_variable_uses(
            self, variables, variable_uses, fragments, fragment_to_references,
            fragment_to_variable_uses, visited_fragments, used_variables):
        """Raise if undefined or wrong type of variable.

        Raise a GraphQlParseError if the specified variable references
        include a reference to an undefined variable or a variable of an
        incompatible type.  This recursively checks all of the
        references in an operation or named fragment.

        dict<basestring, GraphQlVariable> variables - A map from the
            names of the variables to the variables.
        list<dict<basestring, object>> variable_uses - A list of the
            variable references in the operation or named fragment we
            are currently checking, as in the variable_uses argument to
            _append_variable_uses.
        set<GraphQlFragment> fragments - The fragments the operation or
            named fragment we are currently checking references.
        dict<GraphQlFragment, set<GraphQlFragment>>
            fragment_to_references - A map from each fragment to the
            fragments it references, as in
            _add_named_fragment_references.  This must have an entry for
            each named fragment, even if it is an empty set.
        dict<GraphQlFragment, list<dict<basestring, object>>>
            fragment_to_variable_uses - A map from each named fragment
            to the variable references it contains, as in the
            variable_uses argument to _append_variable_uses.
        set<GraphQlFragment> visited_fragments - The named fragments we
            have reached so far.
        set<basestring> used_variables - A set to which to add the
            variables to which we find references.
        """
        for use in variable_uses:
            name = use['name']
            if name not in variables:
                self._raise_exception(
                    'Undefined variable {:s}'.format(name), use['offset'])
            t = variables[name].variable_type
            if variables[name].default_value is not None:
                t = GraphQlNonNullType(t)
            if not t.is_subtype(use['type']):
                self._raise_exception(
                    'The reference to ${:s} in the {:s} argument to {:s} must '
                    'be a {:s} it is a {:s} instead'.format(
                        name, use['arg'], use['source'],
                        use['type'].type_str(), t.type_str()),
                    use['offset'])
            used_variables.add(name)

        # Recurse on referenced fragments
        for fragment in fragments:
            if fragment not in visited_fragments:
                visited_fragments.add(fragment)
                self._validate_variable_uses(
                    variables, fragment_to_variable_uses[fragment],
                    fragment_to_references[fragment], fragment_to_references,
                    fragment_to_variable_uses, visited_fragments,
                    used_variables)

    def _validate_single_field_selection_merging(self, selection_set, fields):
        """Raise if we cannot merge a selection set's field queries.

        Raise a GraphQlParseError if there is an error merging the field
        queries from a selection set, like in the document
        "{foo, foo: bar}".

        GraphQlSelectionSet selection_set - The selection set to merge.
            This is either the initial selection set we were checking or
            a nested selection set from one of its fragments.
        dict<basestring, dict<basestring, object>> fields - A map to the
            fields we have checked thus far from their response keys, as
            in GraphQlFieldQuery.response_key.  Each field has the
            following entries:

            args: A map from the names of the field's arguments to their
                values, as in GraphQlFieldQuery.args.
            fieldType: The GraphQlType of the field's value.
            name: The name of the field.
        """
        for field_query_or_fragment in (
                selection_set.field_queries_and_fragments):
            if not isinstance(field_query_or_fragment, GraphQlFieldQuery):
                # Recurse on a GraphQlFragment
                self._validate_single_field_selection_merging(
                    field_query_or_fragment.fragment.selection_set, fields)
            else:
                field_descriptor = field_query_or_fragment.field_descriptor
                field = {
                    'args': field_query_or_fragment.args,
                    'fieldType': field_descriptor.field_type,
                    'name': field_descriptor.name,
                }
                if field_query_or_fragment.response_key not in fields:
                    fields[field_query_or_fragment.response_key] = field
                elif field != fields[field_query_or_fragment.response_key]:
                    self._raise_exception(
                        'Error merging {:s} key in selection set.  The field '
                        'names, return type, or arguments do not '
                        'match.'.format(field_query_or_fragment.response_key),
                        self._field_query_offsets[field_query_or_fragment])

    def _validate_field_selection_merging(
            self, selection_set, named_fragments):
        """Raise if we cannot merge a selection set's field queries.

        Raise a GraphQlParseError if there is an error merging the field
        queries from a selection set, like in the document
        "{foo, foo: bar}".  Recursively check any nested selection sets
        and anonymous fragments.

        GraphQlSelectionSet selection_set - The selection set to check.
        set<GraphQlFragment> named_fragments - The named fragment
            definitions.  Equivalent to set(self._fragments.values()).
        """
        for field_query_or_fragment in (
                selection_set.field_queries_and_fragments):
            if isinstance(field_query_or_fragment, GraphQlFieldQuery):
                if field_query_or_fragment.selection_set is not None:
                    self._validate_single_field_selection_merging(
                        field_query_or_fragment.selection_set, {})
                    self._validate_field_selection_merging(
                        field_query_or_fragment.selection_set, named_fragments)
            elif field_query_or_fragment.fragment not in named_fragments:
                self._validate_field_selection_merging(
                    field_query_or_fragment.fragment.selection_set,
                    named_fragments)

    def parse(self):
        """Parse the document string passed to the constructor.

        Raise a GraphQlParseError if the document is malformed.  Whether
        the document is malformed depends on the schema, and not just on
        GraphQL syntax.  This method may only be called once on a given
        instance.

        return GraphQlDocument - The document.
        """
        operations = self._read_operations_and_fragments()

        # Check for unused or undefined fragments
        for fragment_name, fragment in self._fragments.iteritems():
            if fragment_name not in self._fragment_to_references:
                self._raise_exception(
                    'Unused fragment {:s}'.format(fragment_name),
                    self._fragment_offsets[fragment])
        for name, fragment_references in (
                self._fragment_to_references.iteritems()):
            if self._fragments[name].object_type is None:
                self._raise_exception(
                    'Reference to undefined fragment {:s}'.format(name),
                    self._fragment_reference_offsets[fragment_references[0]])

        # Compare fragment types with context types
        for fragment_reference, base_type in (
                self._fragment_reference_to_base_type.iteritems()):
            fragment_type = fragment_reference.fragment.object_type
            if (not self._schema.do_base_types_intersect(
                    base_type, fragment_type)):
                fragment_name = None
                for name, fragment in self._fragments.iteritems():
                    if fragment == fragment_reference.fragment:
                        fragment_name = name
                        break
                self._raise_exception(
                    'Type {:s} of fragment {:s} does not intersect the type '
                    '{:s} that references it'.format(
                        fragment_type.name, fragment_name, base_type.name),
                    self._fragment_reference_offsets[fragment_reference])

        # Check for fragment cycles
        named_fragments = set(self._fragments.values())
        fragment_to_references = {}
        fragment_to_variable_uses = {}
        for fragment in self._fragments.itervalues():
            fragments = set()
            self._add_named_fragment_references(
                fragment.selection_set, named_fragments, fragments)
            fragment_to_references[fragment] = fragments
            variable_uses = []
            self._append_variable_uses(
                fragment.selection_set, named_fragments, variable_uses)
            self._append_directive_variable_uses(
                fragment.directives, variable_uses)
            fragment_to_variable_uses[fragment] = variable_uses
        visited = set()
        for fragment in self._fragments.itervalues():
            self._assert_no_fragment_cycle(
                fragment, [], set(), fragment_to_references, visited)

        # Validate variable uses
        for operation in operations:
            fragments = set()
            self._add_named_fragment_references(
                operation.selection_set, named_fragments, fragments)
            variable_uses = []
            self._append_variable_uses(
                operation.selection_set, named_fragments, variable_uses)
            self._append_directive_variable_uses(
                operation.directives, variable_uses)
            used_variables = set()
            self._validate_variable_uses(
                operation.variables, variable_uses, fragments,
                fragment_to_references, fragment_to_variable_uses, set(),
                used_variables)
            for name, variable in operation.variables.iteritems():
                if name not in used_variables:
                    self._raise_exception(
                        'Variable ${:s} is defined, but not used'.format(name),
                        self._variable_offsets[variable])

        # Validate selection set merging
        for operation in operations:
            self._validate_single_field_selection_merging(
                operation.selection_set, {})
            self._validate_field_selection_merging(
                operation.selection_set, named_fragments)
        for fragment in self._fragments.itervalues():
            self._validate_single_field_selection_merging(
                fragment.selection_set, {})
            self._validate_field_selection_merging(
                fragment.selection_set, named_fragments)

        return GraphQlDocument(self._schema, operations)
