from base_type import GraphQlBaseType
from type_kind import GraphQlTypeKind


class GraphQlScalarType(GraphQlBaseType):
    """A GraphQL scalar type.

    A scalar type is any type other than an enumeration type whose JSON
    value representation is limited to scalars.  It wraps a
    GraphQlScalarDescriptor class.

    Public attributes:

    GraphQlClassDescriptor scalar_descriptor_class_descriptor -
        Identifies the GraphQlScalarDescriptor class that this wraps.
    """

    # Private attributes:
    # GraphQlScalarDescriptor _scalar_descriptor - The cached return value of
    #     scalar_descriptor().

    def __init__(self, name, description, scalar_descriptor_class_descriptor):
        super(GraphQlScalarType, self).__init__(name, description)
        self.scalar_descriptor_class_descriptor = (
            scalar_descriptor_class_descriptor)
        self._scalar_descriptor = None

    def scalar_descriptor(self):
        """Return the GraphQlScalarDescriptor that this wraps."""
        if self._scalar_descriptor is None:
            scalar_descriptor_class = (
                self.scalar_descriptor_class_descriptor.load_class())
            self._scalar_descriptor = scalar_descriptor_class(self.name)
        return self._scalar_descriptor

    def field_descriptor(self, name):
        raise ValueError('Scalar types do not have fields')

    def _type_kind(self):
        return GraphQlTypeKind.scalar
