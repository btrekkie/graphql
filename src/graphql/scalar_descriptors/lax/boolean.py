from graphql import graphql_scalar
from graphql import GraphQlScalarDescriptor


@graphql_scalar('Boolean', 'The built-in boolean type')
class GraphQlLaxBooleanDescriptor(GraphQlScalarDescriptor):
    """Lax GraphQlScalarDescriptor for booleans.

    A non-strictly validating GraphQlScalarDescriptor for the built-in
    boolean type.
    """

    def graphql_to_python(self, value):
        if not isinstance(value, bool):
            raise TypeError('Input is not an boolean')
        return value

    def python_to_graphql(self, value):
        return bool(value)
