from graphql import graphql_attr_field
from graphql import graphql_field
from graphql import graphql_object
from input_value import GraphQlInputValue


@graphql_object('__Field', 'A GraphQL field')
@graphql_attr_field('name', 'name', 'String!', 'The name of the field')
@graphql_attr_field(
    'field_type', 'type', '__Type!', "The type of the field's value")
@graphql_attr_field(
    'description', 'description', 'String',
    'A description of the field, or null.  GraphQL favors the Markdown '
    'format.')
@graphql_attr_field(
    'is_deprecated', 'isDeprecated', 'Boolean!',
    'Whether the field is deprecated')
@graphql_attr_field(
    'deprecation_reason', 'deprecationReason', 'String',
    'An indication of why the field is deprecated, or null.  This is null if '
    'the field is not deprecated.')
class GraphQlFieldDescriptor(object):
    """A description of the "interface" of a GraphQL field.

    By contrast to GraphQlField, this does not give an indication of how
    to determine the field's value.  It only indicates how the field is
    presented in GraphQL.  This is also for GraphQL mutations, which are
    basically like fields.

    dict<basestring, GraphQlType> args - A map from the names of the
        arguments to the field in GraphQL to their GraphQL types.
    basestring deprecation_reason - An indication of why the field is
        deprecated, or None.  This is None if is_deprecated is False.
    basestring description - A description of this field, or None.
        GraphQL favors the Markdown format.
    GraphQlType field_type - The type of the field's value.
    bool is_deprecated - Whether the field is deprecated.
    basestring name - The name of the field.
    """
    def __init__(
            self, name, field_type, arguments, description,
            is_deprecated, deprecation_reason):
        self.name = name
        self.field_type = field_type
        self.args = arguments
        self.description = description
        self.is_deprecated = is_deprecated
        self.deprecation_reason = deprecation_reason

    @graphql_field(
        'args', '[__InputValue!]!', {}, [], 'The arguments to the field')
    def _args(self):
        """Return the arguments to the field, as a list of GraphQlInputValues.
        """
        args = []
        for name, t in self.args.iteritems():
            args.append(GraphQlInputValue(name, t))
        return args
