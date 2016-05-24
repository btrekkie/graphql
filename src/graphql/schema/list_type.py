from type import GraphQlType
from type_kind import GraphQlTypeKind


class GraphQlListType(GraphQlType):
    """A list type in GraphQL.

    Public attributes:

    GraphQlType element_type - The type of the elements of the list.
    """

    def __init__(self, element_type):
        self.element_type = element_type

    def is_subtype(self, other):
        return (
            isinstance(other, GraphQlListType) and
            self.element_type.is_subtype(other.element_type))

    def type_str(self):
        return '[{:s}]'.format(self.element_type.type_str())

    def base_type(self):
        return self.element_type.base_type()

    def _type_kind(self):
        return GraphQlTypeKind.list_type

    def _description(self):
        return None

    def _wrapped_type(self):
        return self.element_type

    def __eq__(self, other):
        return (
            isinstance(other, GraphQlListType) and
            self.element_type == other.element_type)

    def __ne__(self, other):
        return not (self == other)
