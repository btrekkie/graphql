from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('ID')
class GraphQlLaxIdDescriptor(GraphQlScalarDescriptor):
    """Lax GraphQlScalarDescriptor for the "ID" type.

    A non-strictly validating GraphQlScalarDescriptor for the built-in
    ID type.
    """

    def graphql_to_python(self, value):
        if isinstance(value, bool):
            raise TypeError('Input is not a string or an integer')
        elif isinstance(value, (int, long)):
            if not (-2 ** 31 <= value < 2 ** 31):
                raise ValueError(
                    'In GraphQL, integer values must be between -2^31 and '
                    '2^31 - 1')
        elif not isinstance(value, basestring):
            raise TypeError('Input is not a string or an integer')
        return str(value)

    def python_to_graphql(self, value):
        return str(value)
