import collections
import copy
import re
import sys

from errors import GraphQlBadScalarDescriptorError
from errors import GraphQlFieldTypeError
from errors import GraphQlOperationNameError
from errors import GraphQlSchemaMismatchError
from errors import GraphQlVariablesError
from graphql import GraphQlResultWithErrors
from graphql.document import GraphQlFieldQuery
from graphql.document import GraphQlFragmentReference
from graphql.document import GraphQlParseError
from graphql.document import GraphQlParser
from graphql.document import GraphQlQuery
from graphql.document import GraphQlVariableReference
from graphql.schema import GraphQlEnumType
from graphql.schema import GraphQlInputObjectType
from graphql.schema import GraphQlListType
from graphql.schema import GraphQlNonNullType
from graphql.schema import GraphQlObjectType
from graphql.schema import GraphQlScalarType
from root_mutation_object import GraphQlRootMutationObject
from root_query_object import GraphQlRootQueryObject


class GraphQlExecutor(object):
    """Provides the ability to execute a GraphQL document."""

    # Private attributes:
    # GraphQlContext _context - The context.
    # GraphQlDocument _document - The document to execute.
    # list<dict<basestring, object>> _errors - The GraphQL errors we have
    #     encountered thus far in executing the document.
    # mixed _graphql_variables - The variable values to pass to the document,
    #     as represented in GraphQL.  This is supposed to be a map from the
    #     names of the variables to the Python objects for their values.  This
    #     differs from _variables in that (a) default values are not filled in
    #     and (b) values appear as their GraphQL scalar representations, rather
    #     than their Python object representations.  Note that the user may
    #     supply _graphql_variables, so it might not be of the correct type.
    # basestring _operation_name - The name of the operation to execute.  This
    #     may be None if the document only has one operation.
    # dict<basestring, mixed> _variables - A map from each variable to the
    #     Python object representation of its value, including any default
    #     values, or None if we have not computed this yet.  We compute this
    #     before executing any operations.  Contrast with _graphql_variables.

    def __init__(self, document, context, operation_name, graphql_variables):
        """Private constructor."""
        self._document = document
        self._context = context
        self._operation_name = operation_name
        self._graphql_variables = graphql_variables
        self._errors = []
        self._variables = None

    @staticmethod
    def _exception_errors(context, exception, exception_info):
        """Return the GraphQL errors for the specified exception.

        This is the same as
        context.exception_errors(exception, exception_info), except that
        it compensates if exception_errors misbehaves.

        GraphQlContext context - The context.
        Exception exception - The exception.
        tuple<type, mixed, traceback> exception_info - Information about
            the exception, as returned by sys.exc_info().
        return list<dict<basestring, object>>> - The errors.  The return
            value is guaranteed not to be empty.
        """
        try:
            exception_errors = context.exception_errors(
                exception, exception_info)
        except:
            return [{'message': str(exception)}]
        if exception_errors:
            return exception_errors
        else:
            return [{'message': str(exception)}]

    def _append_exception_errors(self, exception, exception_info):
        """Append GraphQL errors for the specified exception to _errors.

        Exception exception - The exception.
        tuple<type, mixed, traceback> exception_info - Information about
            the exception, as returned by sys.exc_info().
        """
        self._errors += GraphQlExecutor._exception_errors(
            self._context, exception, exception_info)

    def _verified_python_to_graphql(self, value, scalar_descriptor):
        """Like scalar_descriptor.python_to_graphql(value), but with checks.

        Equivalent to scalar_descriptor.python_to_graphql(value), but it
        validates the type of the result.  If said validation fails, it
        raises a GraphQlBadScalarDescriptorError.

        mixed value - The value.
        GraphQlScalarDescriptor scalar_descriptor - The scalar
            descriptor.
        return object - The scalar value representation.
        """
        result = scalar_descriptor.python_to_graphql(value)
        name = scalar_descriptor.name
        if name == 'String' or name == 'ID':
            if not isinstance(result, basestring):
                raise GraphQlBadScalarDescriptorError(
                    '{:s}.python_to_graphql must return a basestring, because '
                    'it is for the {:s} type'.format(
                        scalar_descriptor.__class__.__name__, name))
        elif name == 'Int':
            if not isinstance(result, (int, long)):
                raise GraphQlBadScalarDescriptorError(
                    '{:s}.python_to_graphql must return an int or long, '
                    'because it is for the Int type'.format(
                        scalar_descriptor.__class__.__name__))
            if not (-2 ** 31 <= result < 2 ** 31):
                raise GraphQlBadScalarDescriptorError(
                    '{:s}.python_to_graphql returned a value that was not in '
                    'the range [2^31, 2^31).  In GraphQL, Int values must be '
                    'in this range.'.format(
                        scalar_descriptor.__class__.__name__))
        elif name == 'Float':
            if isinstance(result, (int, long)):
                raise GraphQlBadScalarDescriptorError(
                    '{:s}.python_to_graphql returned an integer, but the '
                    'Float type must return floating point numbers'.format(
                        scalar_descriptor.__class__.__name__))
            elif not isinstance(result, float):
                raise GraphQlBadScalarDescriptorError(
                    '{:s}.python_to_graphql must return a float, because it '
                    'is for the Float type'.format(
                        scalar_descriptor.__class__.__name__))
        elif name == 'Boolean':
            if not isinstance(result, bool):
                raise GraphQlBadScalarDescriptorError(
                    '{:s}.python_to_graphql must return a bool, because it is '
                    'for the Boolean type'.format(
                        scalar_descriptor.__class__.__name__))
        elif not isinstance(result, (basestring, bool, float, int, long)):
            raise GraphQlBadScalarDescriptorError(
                '{:s}.python_to_graphql must return a basestring, int, long, '
                'float, or bool'.format(scalar_descriptor.__class__.__name__))
        return result

    def _is_output_of_type(self, value, t):
        """Return whether the specified Python object is of the specified type.

        Assume "t" is not a GraphQLInputObjectType.

        mixed value - The value.
        GraphQlType t - The type.
        return bool - Whether the value is of the specified type.
        """
        if value is None:
            return not isinstance(t, GraphQlNonNullType)
        if isinstance(t, GraphQlNonNullType):
            t = t.value_type

        if isinstance(t, GraphQlEnumType):
            try:
                t.python_to_graphql(value)
            except ValueError:
                return False
            return True
        elif isinstance(t, GraphQlScalarType):
            scalar_descriptor = t.scalar_descriptor()
            try:
                self._verified_python_to_graphql(value, scalar_descriptor)
            except (TypeError, ValueError):
                return False
            return True
        elif not isinstance(t, GraphQlListType):
            object_type = self._document.schema.object_type(value)
            return object_type is not None and object_type.is_subtype(t)
        elif not isinstance(value, (list, tuple)):
            return False
        else:
            for element in value:
                if not self._is_output_of_type(element, t.element_type):
                    return False
            return True

    def _graphql_to_python(self, value, t):
        """Return the Python object representation of the specified value.

        Return the Python object representation of the specified value
        supplied using a GraphQL object representation.  This method
        replaces GraphQL string representations of enumeration values
        with the corresponding Python object representations.  Raise a
        TypeError or ValueError if "value" is not of type "t".

        mixed value - The GraphQL representation of the value.  This may
            be a user-supplied JSON value, so it might not have the
            appropriate format.
        GraphQlType t - The type of the value.
        return mixed - The Python object representation of the value.
        """
        if value is None:
            raise TypeError('null is not a valid input value')
        if isinstance(t, GraphQlNonNullType):
            t = t.value_type

        if isinstance(t, GraphQlEnumType):
            return t.graphql_to_python(value)
        elif isinstance(t, GraphQlScalarType):
            return GraphQlParser.verified_graphql_to_python(
                value, t.scalar_descriptor())
        elif isinstance(t, GraphQlInputObjectType):
            if not isinstance(value, dict):
                raise TypeError('Input must be a map')
            for key in value.iterkeys():
                if key not in t.fields:
                    raise ValueError(
                        u'There is no such field {:s}.{:s}'.format(
                            t.name, key))
            for key, field_type in t.fields.iteritems():
                if (isinstance(field_type, GraphQlNonNullType) and
                        key not in value):
                    raise ValueError(
                        'Input value is missing the required field '
                        '{:s}.{:s}'.format(t.name, key))

            python_value = {}
            for key, sub_value in value.iteritems():
                python_value[key] = self._graphql_to_python(
                    sub_value, t.fields[key])
            return python_value
        elif not isinstance(value, (list, tuple)):
            raise TypeError('Input must be a list')
        else:
            python_value = []
            for element in value:
                python_value.append(
                    self._graphql_to_python(element, t.element_type))
            return python_value

    def _evaluate_value(self, value):
        """Return the specified value after evaluating any variable references.

        mixed value - The value, formatted as in the entries of
            GraphQlFieldQuery.args.
        return mixed - The resulting value.
        """
        if isinstance(value, GraphQlVariableReference):
            return self._variables[value.name]
        elif isinstance(value, list):
            result = []
            for element in value:
                result.append(self._evaluate_value(element))
            return result
        elif isinstance(value, dict):
            result = {}
            for key, entry in value.iteritems():
                result[key] = self._evaluate_value(entry)
            return result
        else:
            return value

    def _execute_selection_sets(self, value, t, selection_sets):
        """Return the JSON value result of the specified selection sets.

        Return the JSON value result of executing the specified
        selection sets on the specified value.

        object value - The value whose fields we are querying.  This
            must be of type "t".
        GraphQlType t - The type of the value.
        list<GraphQlSelectionSet> selection_sets - The selection sets,
            in execution order.
        return object - The execution result.
        """
        if value is None:
            return None
        if isinstance(t, GraphQlNonNullType):
            t = t.value_type

        if isinstance(t, GraphQlEnumType):
            return t.python_to_graphql(value)
        elif isinstance(t, GraphQlScalarType):
            try:
                return self._verified_python_to_graphql(
                    value, t.scalar_descriptor())
            except (TypeError, ValueError):
                # This shouldn't happen, because we already verified that
                # "value" is of type "t", but in principle, a
                # GraphQlScalarDescriptor could randomly raise a ValueError
                # half of the time
                raise GraphQlFieldTypeError(
                    'A field returned an instance of {:s}, but it must return '
                    'a value of type {:s}'.format(
                        value.__class__.__name__, t.type_str()))
        elif isinstance(t, GraphQlListType):
            result = []
            for element in value:
                result.append(
                    self._execute_selection_sets(
                        element, t.element_type, selection_sets))
            return result
        else:
            return self._execute_selection_sets_base(value, selection_sets)

    @staticmethod
    def _camel_case_to_snake_case(s):
        """Convert the specified camelCase identifier to snake_case.

        basestring s - The camelCase string.
        return basestring - The snake_case string.
        """
        # Taken from http://stackoverflow.com/a/1176023
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _execute_field_queries_raise(
            self, value, field, arguments, field_queries):
        """Return the JSON value result of the specified field queries.

        Return the JSON value result of executing the specified field
        queries sharing the same response key on the specified value.
        This is like _execute_field_queries, except that it does not
        catch exceptions if the field has a nullable type.  See the
        comments for _execute_field_queries.
        """
        if field.attr is not None:
            non_context_kwargs = {}
        else:
            non_context_kwargs = field.partial_kwargs.copy()
            for name, arg in arguments.iteritems():
                non_context_kwargs[self._camel_case_to_snake_case(name)] = (
                    self._evaluate_value(arg))
        if isinstance(value, GraphQlRootMutationObject):
            self._context.mutation_start(
                field.descriptor.name, non_context_kwargs)

        # Compute the field's value
        try:
            if field.attr is not None:
                field_value = getattr(value, field.attr)
            else:
                kwargs = non_context_kwargs.copy()
                for name in field.context_args:
                    kwargs[name] = self._context.context_arg(name)
                field_value = getattr(value, field.method_name)(
                    *field.partial_args, **kwargs)
            field_value_with_errors = field_value
            if isinstance(field_value, GraphQlResultWithErrors):
                self._append_exception_errors(
                    field_value.exception, field_value.exception_info)
                field_value = field_value.result

            # Check the field's value's type
            field_type = field.descriptor.field_type
            if not self._is_output_of_type(field_value, field_type):
                object_type = self._document.schema.object_type(value)
                raise GraphQlFieldTypeError(
                    '{:s}{{{:s}}} returned an instance of {:s}, but it must '
                    'return a value of type {:s}'.format(
                        object_type.name, field.descriptor.name,
                        field_value.__class__.__name__, field_type.type_str()))
        except Exception as exception:
            if isinstance(value, GraphQlRootMutationObject):
                self._context.mutation_end(
                    field.descriptor.name, non_context_kwargs, None, exception,
                    sys.exc_info())
            raise
        if isinstance(value, GraphQlRootMutationObject):
            self._context.mutation_end(
                field.descriptor.name, non_context_kwargs,
                field_value_with_errors, None, None)

        # Execute the selection sets
        selection_sets = list(
            [field_query.selection_set for field_query in field_queries])
        return self._execute_selection_sets(
            field_value, field_type, selection_sets)

    def _execute_field_queries(self, value, field, arguments, field_queries):
        """Return the JSON value result of the specified field queries.

        Return the JSON value result of executing the specified field
        queries sharing the same response key on the specified value.

        mixed value - The value whose field we are querying.
        GraphQlField field - The field we are requesting.
        dict<basestring, object> arguments - A map from the name of each
            supplied argument to its value, as in
            GraphQlFieldQuery.args.
        list<GraphQlFieldQuery> field_queries - The field queries, in
            execution order.
        return object - The execution result.
        """
        if isinstance(field.descriptor.field_type, GraphQlNonNullType):
            return self._execute_field_queries_raise(
                value, field, arguments, field_queries)
        else:
            try:
                return self._execute_field_queries_raise(
                    value, field, arguments, field_queries)
            except Exception as exception:
                self._append_exception_errors(exception, sys.exc_info())
                return None

    def _append_field_queries(self, selection_set, object_type, field_queries):
        """Append applicable field queries to field_queries.

        Append all field queries in the specified selection set's field
        queries and fragments to field_queries, excluding any fragments
        that do not match object_type, and excluding any that we are to
        skip according to the GraphQlDirectives.

        GraphQlSelectionSet selection_set - The selection set.
        GraphQlObjectType object_type - The runtime type of the object
            we are querying.
        list<dict<basestring, object>> field_queries - The list to which
            to append the field queries.  Each field query has the
            following entries:

            fieldQuery: The GraphQlFieldQuery.
            type: The GraphQlBaseType on which the query is defined.
        """
        for field_query_or_fragment in (
                selection_set.field_queries_and_fragments):
            # Check @include and @skip directives
            directives = field_query_or_fragment.directives
            if isinstance(field_query_or_fragment, GraphQlFragmentReference):
                directives += field_query_or_fragment.fragment.directives
            include = True
            for directive in directives:
                if directive.directive_type.name == 'include':
                    if not self._evaluate_value(directive.args['if']):
                        include = False
                        break
                elif (directive.directive_type.name == 'skip' and
                        self._evaluate_value(directive.args['if'])):
                    include = False
                    break

            if include:
                if isinstance(field_query_or_fragment, GraphQlFieldQuery):
                    field_queries.append({
                        'fieldQuery': field_query_or_fragment,
                        'type': selection_set.base_type,
                    })
                elif (object_type.is_subtype(
                        field_query_or_fragment.fragment.object_type)):
                    # Recurse on the fragment
                    self._append_field_queries(
                        field_query_or_fragment.fragment.selection_set,
                        object_type, field_queries)

    def _execute_selection_sets_base(self, value, selection_sets):
        """Return the JSON value result of the specified selection sets.

        Return the JSON value result of executing the specified
        selection sets on the specified value of a base type.

        mixed value - The value whose fields we are querying.
        list<GraphQlSelectionSet> selection_sets - The selection sets,
            in execution order.
        return object - The execution result.
        """
        # Compute a map from response key to field queries
        object_type = self._document.schema.object_type(value)
        field_queries = []
        for selection_set in selection_sets:
            self._append_field_queries(
                selection_set, object_type, field_queries)
        response_key_to_field_queries = {}
        response_keys = []
        for field_query in field_queries:
            response_key = field_query['fieldQuery'].response_key
            if response_key not in response_key_to_field_queries:
                response_keys.append(response_key)
            response_key_to_field_queries.setdefault(response_key, []).append(
                field_query)

        # Compute the results
        results = collections.OrderedDict()
        for response_key in response_keys:
            field_queries = response_key_to_field_queries[response_key]
            name = field_queries[0]['fieldQuery'].field_descriptor.name
            args = field_queries[0]['fieldQuery'].args
            if name == '__typename':
                results[response_key] = object_type.name
            elif (object_type == self._document.schema.root_query_type() and
                    (name == '__schema' or name == '__type')):
                # Implicit root field
                schema = self._document.schema
                if name == '__schema':
                    field_value = schema
                else:
                    type_name = self._evaluate_value(args['name'])
                    try:
                        field_value = schema.get_type(type_name)
                    except ValueError:
                        field_value = None
                if field_value is None:
                    results[response_key] = None
                else:
                    results[response_key] = self._execute_selection_sets(
                        field_value, schema.object_type(field_value),
                        list([
                            field_query['fieldQuery'].selection_set
                            for field_query in field_queries]))
            else:
                if isinstance(field_queries[0]['type'], GraphQlObjectType):
                    has_field = name in field_queries[0]['type'].fields
                else:
                    has_field = (
                        name in field_queries[0]['type'].field_descriptors)
                if has_field:
                    field = object_type.fields[name]
                    results[response_key] = self._execute_field_queries(
                        value, field, args, list([
                            field_query['fieldQuery']
                            for field_query in field_queries]))
        return results

    def _execute_query(self, query):
        """Return the JSON value result of executing the given GraphQlQuery."""
        try:
            return self._execute_selection_sets_base(
                GraphQlRootQueryObject.instance(), [query.selection_set])
        except Exception as exception:
            self._append_exception_errors(exception, sys.exc_info())
            return None

    def _execute_mutation(self, mutation):
        """Execute the given GraphQlMutation and return its JSON value result.
        """
        try:
            return self._execute_selection_sets_base(
                GraphQlRootMutationObject.instance(), [mutation.selection_set])
        except Exception as exception:
            self._append_exception_errors(exception, sys.exc_info())
            return None

    def _graphql_variables_to_python(self, operation):
        """Return the Python object representation of the variables.

        In other words, return the value for _variables, based on the
        value of _graphql_variables and the specified operation.  Raise
        a GraphQlVariablesError if _graphql_variables does not contain
        valid variables for the specified GraphQlOperation.
        """
        if not isinstance(self._graphql_variables, dict):
            raise GraphQlVariablesError('Variables must be a dictionary')
        python_variables = {}
        for name, var in operation.variables.iteritems():
            if name not in self._graphql_variables:
                if isinstance(var.variable_type, GraphQlNonNullType):
                    raise GraphQlVariablesError(
                        'Missing required variable {:s}'.format(name))
                python_variables[name] = var.default_value

        for name, value in self._graphql_variables.iteritems():
            if name not in operation.variables:
                raise GraphQlVariablesError(
                    u'No such variable {:s}'.format(name))
            variable_type = operation.variables[name].variable_type
            try:
                python_variables[name] = self._graphql_to_python(
                    value, variable_type)
            except (TypeError, ValueError) as exception:
                raise GraphQlVariablesError(str(exception))
        return python_variables

    def _execute_document(self):
        """Return the JSON value result of executing _document.

        Raise a GraphQlOperationNameError or GraphQlVariablesError if
        there is an error with the operation name or variables.
        """
        # Find the operation with name _operation_name
        if self._operation_name is None:
            if len(self._document.operations) != 1:
                raise GraphQlOperationNameError(
                    'Must specify the operation name')
            operation = self._document.operations[0]
        else:
            operation = None
            for cur_operation in self._document.operations:
                if cur_operation.name == self._operation_name:
                    operation = cur_operation
                    break
            if operation is None:
                raise GraphQlOperationNameError(
                    u'There is no operation named {:s}'.format(
                        self._operation_name))

        self._variables = self._graphql_variables_to_python(operation)
        if isinstance(operation, GraphQlQuery):
            result = self._execute_query(operation)
        else:
            result = self._execute_mutation(operation)
        if self._errors:
            return {'data': result, 'errors': self._errors}
        else:
            return {'data': result}

    @staticmethod
    def execute(document_str, context, variables={}, operation_name=None):
        """Return the JSON value result of executing the specified document.

        basestring document_str - The document to execute.
        GraphQlContext context - The context.  See the comments for
            GraphQlContext.
        mixed variables - The variable values to pass to the document,
            as in _graphql_variables.
        basestring operation_name - The name of the operation to
            execute.  This may be None if the document only has one
            operation.
        return object - The JSON value.
        """
        try:
            context.execute_document_str_start(document_str, operation_name)
        except:
            pass
        try:
            document = GraphQlParser(document_str, context.schema).parse()
            context.parsed_document(document, operation_name)
            executor = GraphQlExecutor(
                document, context, operation_name, variables)
            result = executor._execute_document()
            exception = None
            exception_info = None
        except (GraphQlOperationNameError,
                GraphQlParseError,
                GraphQlVariablesError) as exception:
            exception_info = sys.exc_info()
            result = {
                'errors': GraphQlExecutor._exception_errors(
                    context, exception, exception_info),
            }
        try:
            context.execute_document_str_end(
                document_str, operation_name, copy.deepcopy(result),
                exception, exception_info)
        except:
            pass
        try:
            extensions = context.extensions(
                copy.deepcopy(result), exception, exception_info)
        except:
            extensions = None
        if extensions is not None:
            result['extensions'] = extensions
        return result

    @staticmethod
    def execute_document(document, context, variables={}, operation_name=None):
        """Return the JSON value result of executing the given GraphQlDocument.

        If the callsite has a document string rather than a
        GraphQlDocument, it should call execute instead, as execute
        handles errors properly in that case.  execute_document is
        useful as an optimization when executing a document multiple
        times.

        GraphQlDocument document - The document to execute.
        GraphQlContext context - The context.  See the comments for
            GraphQlContext.
        mixed variables - The variable values to pass to the document,
            as in _graphql_variables.
        basestring operation_name - The name of the operation to
            execute.  This may be None if the document only has one
            operation.
        return object - The JSON value.
        """
        try:
            if document.schema != context.schema:
                raise GraphQlSchemaMismatchError(
                    "The document's schema differs from that of the context")
            try:
                context.execute_document_start(document, operation_name)
            except:
                pass
            executor = GraphQlExecutor(
                document, context, operation_name, variables)
            result = executor._execute_document()
            exception = None
            exception_info = None
        except (GraphQlOperationNameError,
                GraphQlSchemaMismatchError,
                GraphQlVariablesError) as exception:
            exception_info = sys.exc_info()
            result = {
                'errors': GraphQlExecutor._exception_errors(
                    context, exception, exception_info),
            }
        try:
            context.execute_document_end(
                document, operation_name, copy.deepcopy(result),
                exception, exception_info)
        except:
            pass
        try:
            extensions = context.extensions(
                copy.deepcopy(result), exception, exception_info)
        except:
            extensions = None
        if extensions is not None:
            result['extensions'] = extensions
        return result
