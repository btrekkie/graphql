from type import GraphQlType
from type_kind import GraphQlTypeKind


class GraphQlNonNullType(GraphQlType):
    """A non-null type in GraphQL.

    Public attributes:

    GraphQlType value_type - The type of the value.  This may not be a
        GraphQlNonNullType.
    """

    def __init__(self, value_type):
        self.value_type = value_type

    def is_subtype(self, other):
        if isinstance(other, GraphQlNonNullType):
            return self.is_subtype(other.value_type)
        else:
            return self.value_type.is_subtype(other)

    def type_str(self):
        return '{:s}!'.format(self.value_type.type_str())

    def base_type(self):
        return self.value_type.base_type()

    def _type_kind(self):
        return GraphQlTypeKind.non_null

    def _description(self):
        return None

    def _wrapped_type(self):
        return self.value_type

    def __eq__(self, other):
        return (
            isinstance(other, GraphQlNonNullType) and
            self.value_type == other.value_type)

    def __ne__(self, other):
        return not (self == other)
