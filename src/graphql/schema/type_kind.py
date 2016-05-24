from graphql import graphql_enum


class GraphQlTypeKind(object):
    """An enumeration of the kinds of GraphQL types."""

    # The kind of GraphQlScalarType
    scalar = 1

    # The kind of GraphQlObjectType
    obj = 2

    # The kind of GraphQlInterfaceType
    interface = 3

    # The kind of GraphQlUnionType
    union = 4

    # The kind of GraphQlEnumType
    enum = 5

    # The kind of GraphQlInputObjectType
    input_object = 6

    # The kind of GraphQlListType
    list_type = 7

    # The kind of GraphQlNonNullType
    non_null = 8

    @staticmethod
    @graphql_enum('__TypeKind', 'An enumeration of the kinds of GraphQL types')
    def graphql_to_python():
        """Return a map from GraphQL constant name to GraphQlTypeKind constant.

        """
        return {
            'SCALAR': GraphQlTypeKind.scalar,
            'OBJECT': GraphQlTypeKind.obj,
            'INTERFACE': GraphQlTypeKind.interface,
            'UNION': GraphQlTypeKind.union,
            'ENUM': GraphQlTypeKind.enum,
            'INPUT_OBJECT': GraphQlTypeKind.input_object,
            'LIST': GraphQlTypeKind.list_type,
            'NON_NULL': GraphQlTypeKind.non_null,
        }
