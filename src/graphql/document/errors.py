class GraphQlParseError(Exception):
    """An error parsing a malformed GraphQL document string.

    Whether the document is malformed depends on the schema, and not
    just on GraphQL syntax.

    Public attributes:

    int column - The column number at which the error is located in
        document_str.
    basestring document_str - The document string.
    int line - The line number at which the error is located in
        document_str.
    """

    def __init__(self, message, document_str, line, column):
        super(GraphQlParseError, self).__init__(message)
        self.document_str = document_str
        self.line = line
        self.column = column
