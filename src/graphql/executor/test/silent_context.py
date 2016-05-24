from graphql.executor import GraphQlContext


class SilentGraphQlContext(GraphQlContext):
    """GraphQlContext whose exception_errors method does not log the exception.

    It includes a "type" field in each error object, which is the name
    of the class of the exception.
    """

    def exception_errors(self, exception, exception_info):
        return [
            {'message': str(exception), 'type': exception.__class__.__name__}]
