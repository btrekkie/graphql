from graphql.executor import GraphQlContext


class TrackingGraphQlContext(GraphQlContext):
    """A GraphQlContext that keeps track of which methods were called.

    The "extensions" entry is a map from "mutationCount" to the number
    of mutations we executed for the document.

    Public attributes:

    list<basestring> calls - The names of the methods we have called, in
        order.
    """

    # Private attributes:
    # int _mutation_count - The number of mutations we have performed since we
    #     started execution.  This is unspecified if we are not currently
    #     executing a document.

    def __init__(self, schema):
        super(TrackingGraphQlContext, self).__init__(schema)
        self.calls = []
        self._mutation_count = 0

    def exception_errors(self, exception, exception_info):
        self.calls.append('exception_errors')
        return [{'message': str(exception)}]

    def execute_document_str_start(self, document_str, operation_name):
        self.calls.append('execute_document_str_start')
        self._mutation_count = 0

    def parsed_document(self, document, operation_name):
        self.calls.append('parsed_document')

    def execute_document_str_end(
            self, document_str, operation_name, result, exception,
            exception_info):
        self.calls.append('execute_document_str_end')

    def execute_document_start(self, document, operation_name):
        self.calls.append('execute_document_start')
        self._mutation_count = 0

    def execute_document_end(
            self, document, operation_name, result, exception, exception_info):
        self.calls.append('execute_document_end')

    def extensions(self, result, exception, exception_info):
        self.calls.append('extensions')
        return {'mutationCount': self._mutation_count}

    def mutation_start(self, name, arguments):
        self.calls.append('mutation_start')
        self._mutation_count += 1

    def mutation_end(
            self, name, arguments, result, exception, exception_info):
        self.calls.append('mutation_end')
