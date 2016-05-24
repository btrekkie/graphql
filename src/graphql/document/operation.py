class GraphQlOperation(object):
    """Abstract base class for GraphQL operations (queries and mutations).

    Public attributes:

    list<GraphQlDirective> directives - The directives for the
        operation.
    basestring name - The name of the operation, or None if it is
        anonymous.
    GraphQlSelectionSet selection_set - The selection set indicating the
        field requests to make in the operation.
    dict<basestring, GraphQlVariable> variables - A map from the names
        of the variables for the operation to the variables.
    """

    def __init__(self, name, variables, selection_set, directives):
        self.name = name
        self.variables = variables
        self.selection_set = selection_set
        self.directives = directives
