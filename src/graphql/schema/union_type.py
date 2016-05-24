from base_type import GraphQlBaseType
from interface_type import GraphQlInterfaceType
from type_kind import GraphQlTypeKind


class GraphQlUnionType(GraphQlBaseType):
    """A union GraphQL type.

    The essential information about a union is in child_types.
    """

    def _type_kind(self):
        return GraphQlTypeKind.union

    def _possible_types(self):
        concrete_types = []
        for leaf_type in self.leaf_types():
            if (not isinstance(
                    leaf_type, (GraphQlInterfaceType, GraphQlUnionType))):
                concrete_types.append(leaf_type)
        return concrete_types
