class GraphQlExecutionError(Exception):
    """Abstract base class for an error in the GraphQL execution process.

    This is not for errors raised by application code - by methods
    decorated by graphql_field and the like or by GraphQlContext
    methods.  Rather, it is for all other types of errors that may occur
    during execution, excluding GraphQlParseErrors.
    """
    pass


class GraphQlFieldTypeError(GraphQlExecutionError):
    """Indicates that a GraphQL field method returned the wrong type of value.

    Indicates that a method or attribute that returns the value of a
    GraphQL field returned the wrong type of value - a value of a type
    that does not match the GraphQL field type.
    """
    pass


class GraphQlOperationNameError(GraphQlExecutionError):
    """Indicates that the operation name is invalid.

    Indicates that the value passed in for the name of the operation to
    execute is invalid.  Either it is None and the GraphQL document has
    multiple operations, or it is not the name of any operation in the
    document.
    """
    pass


class GraphQlSchemaMismatchError(GraphQlExecutionError):
    """A mismatch between GraphQlDocument.schema and GraphQlContext.schema.

    We raise this if the GraphQlSchema of the GraphQlDocument passed to
    GraphQlExecutor.execute_document does not match that of the
    GraphQlContext passed to the method.
    """
    pass


class GraphQlVariablesError(GraphQlExecutionError):
    """Indicates that the variables are invalid.

    Indicates that the value passed in for the variables to the GraphQL
    document are invalid.  Either they have the wrong type, they include
    an undefined variable, or they do not include a required variable.
    """
    pass


class GraphQlBadScalarDescriptorError(GraphQlExecutionError):
    """A bad GraphQlScalarDescriptor.python_to_graphql implementation.

    Indicates that a GraphQlScalarDescriptor.python_to_graphql call
    resulted in the wrong type of value - either a value that is not a
    scalar value, or if the scalar descriptor is for a built-in type
    (String, ID, Int, Float, or Boolean), a value that is not of the
    scalar type appropriate to the built-in type.
    """
    pass
