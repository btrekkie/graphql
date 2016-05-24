from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('Int', 'The built-in integer type')
class GraphQlLaxIntDescriptor(GraphQlScalarDescriptor):
    """Lax GraphQlScalarDescriptor for integers.

    A non-strictly validating GraphQlScalarDescriptor for the built-in
    integer type.
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
        int_value = int(value)
        if not (-2 ** 31 <= int_value < 2 ** 31):
            raise ValueError(
                'In GraphQL, integer values must be between -2^31 and '
                '2^31 - 1')
        return int_value
