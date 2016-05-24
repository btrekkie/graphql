from base_type import GraphQlBaseType
from input_value import GraphQlInputValue
from type_kind import GraphQlTypeKind


class GraphQlInputObjectType(GraphQlBaseType):
    """An input object GraphQL type.

    Public attributes:

    dict<basestring, GraphQlType> fields - A map from the object's
        fields' names to their types.
    """

    def __init__(self, name, description):
        super(GraphQlInputObjectType, self).__init__(name, description)
        self.fields = {}

    def add_field(self, name, t):
        """Add the specified field to this.

        basestring name - The name of the field.
        GraphQlType - The type of the field.
        """
        if name in self.fields:
            raise ValueError(
                'Duplicate field {:s}.{:s}'.format(self.name, name))
        self.fields[name] = t

    def field_descriptor(self, name):
        raise ValueError('Input objects do not have result fields')

    def _type_kind(self):
        return GraphQlTypeKind.input_object

    def _input_fields(self):
        fields = []
        for field, t in self.fields.iteritems():
            fields.append(GraphQlInputValue(field, t))
        return fields
