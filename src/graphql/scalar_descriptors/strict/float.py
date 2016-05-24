from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('Float', 'The built-in floating point number type')
class GraphQlStrictFloatDescriptor(GraphQlScalarDescriptor):
    """Strict GraphQlScalarDescriptor for floating point numbers.

    A strictly validating GraphQlScalarDescriptor for the built-in
    floating point number type.
    """

    def graphql_to_python(self, value):
        if not isinstance(value, (float, int, long)):
            raise TypeError('Input is not a number')
        return float(value)

    def python_to_graphql(self, value):
        if not isinstance(value, (float, int, long)):
            raise TypeError('Object is not a number')
        return float(value)
