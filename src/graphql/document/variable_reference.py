class GraphQlVariableReference(object):
    """A reference to a GraphQL variable.

    This appears in argument values, like in GraphQlFieldQuery.args.

    Public attributes:

    basestring name - The name of the variable.
    """
    def __init__(self, name):
        self.name = name
