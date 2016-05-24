class GraphQlVariable(object):
    """A GraphQL variable definition.

    Public attributes:

    object default_value - A Python object indicating the default value
        of the variable, if any.
    basestring name - The name of the variable.
    GraphQlType variable_type - The type of the variable.
    """

    def __init__(self, name, variable_type, default_value):
        self.name = name
        self.variable_type = variable_type
        self.default_value = default_value
