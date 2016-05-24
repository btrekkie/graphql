from base_type import GraphQlBaseType
from interface_type import GraphQlInterfaceType
from type_kind import GraphQlTypeKind


class GraphQlObjectType(GraphQlBaseType):
    """A concrete GraphQL type, for objects of a certain Python type.

    Public attributes:

    GraphQlClassDescriptor class_descriptor - Identifies the class of
        the objects that are of this type.
    dict<basestring, GraphQlField> fields - A map from the field names
        to the fields.  This does not include entries for fields common
        to all objects, such as "__typename".
    """

    def __init__(self, name, description, class_descriptor):
        super(GraphQlObjectType, self).__init__(name, description)
        self.class_descriptor = class_descriptor
        self.fields = {}

    def add_field(self, field):
        """Add the specified field to "fields".

        GraphQlField field - The field.
        """
        if field.descriptor.name in self.fields:
            raise RuntimeError(
                'Duplicate field {:s}{{{:s}}}'.format(
                    self.name, field.descriptor.name))
        self.fields[field.descriptor.name] = field

    def field_descriptor(self, name):
        if name not in self.fields:
            raise ValueError('There is no field named {:s}'.format(name))
        return self.fields[name].descriptor

    def _type_kind(self):
        return GraphQlTypeKind.obj

    def _explicit_field_descriptors(self, include_deprecated=False):
        field_descriptors = []
        for field in self.fields.itervalues():
            if not field.descriptor.is_deprecated or include_deprecated:
                field_descriptors.append(field.descriptor)
        return field_descriptors

    def _interfaces(self):
        interfaces = []
        for parent_type in self.ancestor_types():
            if isinstance(parent_type, GraphQlInterfaceType):
                interfaces.append(parent_type)
        return interfaces
