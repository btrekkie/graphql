from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('Int')
class BrokenGraphQlIntDescriptor(GraphQlScalarDescriptor):
    """Broken GraphQlScalarDescriptor for the built-in Int type.

    It is broken in that its python_to_graphql method does not return an
    int or a long.
    """

    def graphql_to_python(self, value):
        if not isinstance(value, (int, long)):
            raise TypeError('Input is not an integer')
        if not (-2 ** 31 <= value < 2 ** 31):
            raise ValueError(
                'In GraphQL, integer values must be between -2^31 and '
                '2^31 - 1')
        return value

    def python_to_graphql(self, value):
        return '123'
