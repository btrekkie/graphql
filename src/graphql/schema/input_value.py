from graphql import graphql_attr_field
from graphql import graphql_field
from graphql import graphql_object


@graphql_object('__InputValue', 'A (GraphQL identifier, GraphQL type) pair')
@graphql_attr_field('field_type', 'type', '__Type!', 'The type')
@graphql_attr_field('name', 'name', 'String!', 'The identifier')
class GraphQlInputValue(object):
    """A (GraphQL identifier, GraphQL type) pair.

    Describes an argument or input object field.

    Public attributes:

    GraphQlType field_type - The type.
    basestring name - The identifier.
    """

    def __init__(self, name, field_type):
        self.name = name
        self.field_type = field_type

    @graphql_field(
        'description', 'String', {}, [],
        'A description of the value, or null.  GraphQL favors the Markdown '
        'format.')
    def _description(self):
        """Return a description of this value, or None.

        GraphQL favors the Markdown format.

        return basestring - The description.
        """
        return None

    @graphql_field(
        'defaultValue', 'String', {}, [],
        'The GraphQL document string representation of the default value of '
        'this field, if any, or null')
    def _default_value(self):
        """Return the string representation of the default value of this field.

        Return the GraphQL document string representation of the default
        value of this field, if any, or None.
        """
        return None
