import logging

from graphql.document import GraphQlParseError

logger = logging.getLogger(__name__)


class GraphQlContext(object):
    """Provides context to GraphQlExecutor and controls execution.

    A context object is passed to the GraphQlExecutor execution methods.
    We may use GraphQlContext directly, or we may subclass
    GraphQlContext.  GraphQlContext serves three purposes.  First, it
    exposes the GraphQlSchema that the GraphQL documents use.  Second,
    GraphQlContext has hooks for listening to and controlling certain
    events in the execution process.  Third, it exposes "context
    arguments", which are values that methods that return the values of
    GraphQL fields may obtain.  For example, on a web server, a context
    argument might be an object representing the user or the HTTP
    request.

    Public attributes:

    GraphQlSchema schema - The schema the GraphQL documents use.
    """

    def __init__(self, schema):
        self.schema = schema

    def context_arg(self, name):
        """Return the context argument with the specified name.

        Raise a ValueError if there is no such context argument.  The
        set of available context arguments depends on the particular
        GraphQlContext subclass.  The base class does not support any
        context arguments.

        "Context arguments" are values that methods that return the
        values of GraphQL fields may obtain.  For example, on a web
        server, a context argument might be an object representing the
        user or the HTTP request.  Typically, the context arguments are
        passed to the GraphQlContext subclass's constructor.  The name
        of a context argument is the same as its name when passed as a
        keyword argument.

        basestring name - The name.
        return mixed - The context argument.
        """
        raise ValueError(u'Unknown context argument {:s}'.format(name))

    def exception_errors(self, exception, exception_info):
        """Return the GraphQL errors for the specified exception.

        This may have side effects pertaining to encountering such an
        exception, such as logging information information about the
        exception.

        Exception exception - The exception.
        tuple<type, mixed, traceback> exception_info - Information about
            the exception, as returned by sys.exc_info().
        return list<dict<basestring, object>>> - The errors.  The return
            value must not be empty.
        """
        logger.error('Exception in GraphQL execution', exc_info=exception_info)
        if isinstance(exception, GraphQlParseError):
            return [{
                'locations': [{
                    'column': exception.column,
                    'line': exception.line,
                }],
                'message': str(exception),
            }]
        else:
            return [{'message': str(exception)}]

    def execute_document_str_start(self, document_str, operation_name):
        """Respond to starting to execute a document from a document string.

        We do not call this when we execute a document from a
        GraphQlDocument object rather than a document string.

        basestring document_str - The document we are executing.
        basestring operation_name - The name of the operation we are
            executing.  This may be None if the document only has one
            operation.
        """
        pass

    def parsed_document(self, document, operation_name):
        """Respond to successfully parsing a document from a document string.

        This is for when we execute a document from a document string.
        We do not call this when we execute a document from a
        GraphQlDocument object rather than a string.

        GraphQlDocument document - The document we are executing.
        basestring operation_name - The name of the operation we are
            executing.  This may be None if the document only has one
            operation.
        """
        pass

    def execute_document_str_end(
            self, document_str, operation_name, result, exception,
            exception_info):
        """Respond to finishing executing a document from a document string.

        We do not call this when we execute a document from a
        GraphQlDocument object rather than a document string.

        basestring document_str - The document we are executing.
        basestring operation_name - The name of the operation we are
            executing.  This may be None if the document only has one
            operation.
        dict<basestring, object> result - The execution response,
            excluding the "extensions" entry.
        Exception exception - The exception we encountered, if any.
            This is only for exceptions that propagate to the root
            level: GraphQlParseErrors, GraphQlOperationNameErrors, and
            GraphQlVariablesErrors.
        tuple<type, mixed, traceback> exception_info - Information about
            the exception we encountered, as returned by sys.exc_info(),
            or None if "excepction" is None.
        """
        pass

    def execute_document_start(self, document, operation_name):
        """Respond to starting to execute a document from a GraphQlDocument.

        We do not call this when we execute a document from a document
        string rather than a GraphQlDocument object.

        GraphQlDocument document - The document we are executing.
        basestring operation_name - The name of the operation we are
            executing.  This may be None if the document only has one
            operation.
        """
        pass

    def execute_document_end(
            self, document, operation_name, result, exception, exception_info):
        """Respond to finishing executing a document from a GraphQlDocument.

        We do not call this when we execute a document from a document
        string rather than a GraphQlDocument object.

        GraphQlDocument document - The document we are executing.
        basestring operation_name - The name of the operation we are
            executing.  This may be None if the document only has one
            operation.
        dict<basestring, object> result - The execution response,
            excluding the "extensions" entry.
        Exception exception - The exception we encountered, if any.
            This is only for exceptions that propagate to the root
            level: GraphQlParseErrors, GraphQlOperationNameErrors,
            GraphQlVariablesErrors, and GraphQlSchemaMismatchErrors.
        tuple<type, mixed, traceback> exception_info - Information about
            the exception we encountered, as returned by sys.exc_info(),
            or None if "excepction" is None.
        """
        pass

    def extensions(self, result, exception, exception_info):
        """Return the "extensions" entry for the response.

        Return None if we should not include an "extensions" entry.  We
        call this after calling execute_document_str_end or
        execute_document_end.

        dict<basestring, object> result - The execution response,
            excluding the "extensions" entry.
        Exception exception - The exception we encountered, if any.
            This is only for exceptions that propagate to the root
            level: GraphQlParseErrors, GraphQlOperationNameErrors,
            GraphQlVariablesErrors, and GraphQlSchemaMismatchErrors.
        tuple<type, mixed, traceback> exception_info - Information about
            the exception we encountered, as returned by sys.exc_info(),
            or None if "excepction" is None.
        return dict<basestring, object> - The "extensions" entry.
        """
        return None

    def mutation_start(self, name, arguments):
        """Respond to starting to perform a mutation.

        We call this immediately before calling a method annotated with
        graphql_mutation.

        basestring name - The name of the mutation field.
        dict<basestring, mixed> arguments - The keyword arguments to the
            mutation method, excluding context arguments.
        """
        pass

    def mutation_end(
            self, name, arguments, result, exception, exception_info):
        """Respond to finishing performing a mutation.

        We call this immediately after calling a method annotated with
        graphql_mutation, before we start obtaining any fields from the
        Python object for the mutation field.

        basestring name - The name of the mutation field.
        dict<basestring, mixed> arguments - The keyword arguments to the
            mutation method, excluding context arguments.
        mixed result - The return value of the mutation method, or None
            if it raised an exception.  This may be a
            GraphQlResultWithErrors object, in which case "exception"
            and exception_info are None.
        Exception exception - The exception the mutation method raised,
            or the GraphQlFieldTypeError for the mutation method, if
            any.
        tuple<type, mixed, traceback> exception_info - Information about
            "exception", as returned by sys.exc_info(), or None if
            "excepction" is None.
        """
        pass
