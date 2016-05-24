class GraphQlDocument(object):
    """A GraphQL document.

    GraphQlSchema schema - The schema the document is using.
    list<GraphQlOperation> operations - The operations in the document.
    """

    def __init__(self, schema, operations):
        self.schema = schema
        self.operations = operations
