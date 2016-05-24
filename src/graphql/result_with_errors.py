class GraphQlResultWithErrors(object):
    """An object indicating a GraphQL field value with errors.

    When a method that returns the value of a GraphQL field returns a
    GraphQlResultWithErrors object, we add the errors for
    GraphQlResultWithErrors.exception to the execution results, and we
    take the value of the field to be GraphQlResultWithErrors.result.
    The normal way to report errors is by raising the exception, but
    sometimes we need to both emit an error and return a field value.

    <T> - The type of "result".

    Public attributes:

    Exception exception - The exception for which to emit errors.
    tuple<type, mixed, traceback> exception_info - Information about the
        exception, as returned by sys.exc_info().
    T result - The field value.
    """

    def __init__(self, result, exception, exception_info):
        self.result = result
        self.exception = exception
        self.exception_info = exception_info
