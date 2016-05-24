from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('Float', 'The built-in floating point number type')
class GraphQlLaxFloatDescriptor(GraphQlScalarDescriptor):
    """Lax GraphQlScalarDescriptor for floating point numbers.

    A non-strictly validating GraphQlScalarDescriptor for the built-in
    floating point number type.
    """

    def graphql_to_python(self, value):
        if not isinstance(value, (float, int, long)):
            raise TypeError('Input is not a number')
        return value

    def python_to_graphql(self, value):
        return float(value)
