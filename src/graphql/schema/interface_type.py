from base_type import GraphQlBaseType
from type_kind import GraphQlTypeKind


class GraphQlInterfaceType(GraphQlBaseType):
    """An interface GraphQL type.

    Public attributes:

    dict<basestring, GraphQlFieldDescriptor> field_descriptors - A map
        from the interface's fields' names to their descriptions.  This
        does not include entries for fields common to all objects, such
        as "__typename".
    """

    def __init__(self, name, description):
        super(GraphQlInterfaceType, self).__init__(name, description)
        self.field_descriptors = {}

    def add_field_descriptor(self, field_descriptor):
        """Add the specified field to field_descriptors.

        GraphQlFieldDescriptor field_descriptor - The field's
            description.
        """
        if field_descriptor.name in self.field_descriptors:
            raise RuntimeError(
                'Duplicate field {:s}{{{:s}}}'.format(
                    self.name, field_descriptor.name))
        self.field_descriptors[field_descriptor.name] = (
            field_descriptor)

    def field_descriptor(self, name):
        if name not in self.field_descriptors:
            raise ValueError('There is no field named {:s}'.format(name))
        return self.field_descriptors[name]

    def _type_kind(self):
        return GraphQlTypeKind.interface

    def _explicit_field_descriptors(self, include_deprecated=False):
        field_descriptors = []
        for field_descriptor in self.field_descriptors.itervalues():
            if not field_descriptor.is_deprecated or include_deprecated:
                field_descriptors.append(field_descriptor)
        return field_descriptors

    def _possible_types(self):
        concrete_types = []
        for leaf_type in self.leaf_types():
            if not isinstance(leaf_type, GraphQlInterfaceType):
                concrete_types.append(leaf_type)
        return concrete_types
