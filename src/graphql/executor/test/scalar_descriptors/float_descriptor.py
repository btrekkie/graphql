from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('Float')
class BrokenGraphQlFloatDescriptor(GraphQlScalarDescriptor):
    """Broken GraphQlScalarDescriptor for the built-in Float type.

    It is broken in that its graphql_to_python method does not check the
    correctness of the type of the argument.
    """

    def graphql_to_python(self, value):
        return float(value)

    def python_to_graphql(self, value):
        if not isinstance(value, (float, int, long)):
            raise TypeError('Object is not a number')
        return float(value)
