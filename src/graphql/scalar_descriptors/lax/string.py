from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('String', 'The built-in string type')
class GraphQlLaxStringDescriptor(GraphQlScalarDescriptor):
    """Lax GraphQlScalarDescriptor for strings.

    A non-strictly validating GraphQlScalarDescriptor for the built-in
    string type.
    """

    def graphql_to_python(self, value):
        if not isinstance(value, basestring):
            raise TypeError('Input is not a string')
        return value

    def python_to_graphql(self, value):
        return str(value)
