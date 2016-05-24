from graphql import graphql_attr_field
from graphql import graphql_field
from graphql import graphql_object


@graphql_object('__EnumValue', 'A value in a GraphQL enumeration.')
@graphql_attr_field(
    'value', 'name', 'String!', 'The GraphQL constant for the value')
class GraphQlEnumValue(object):
    """A value in a GraphQL enumeration.

    Public attributes:

    basestring value - The GraphQL constant for the value.
    """

    def __init__(self, value):
        self.value = value

    @graphql_field(
        'description', 'String', {}, [],
        'A description of this value, or null.  GraphQL favors the Markdown '
        'format.')
    def _description(self):
        """Return a reader-friendly description of this value, or None.

        return basestring - The description.
        """
        return None

    @graphql_field(
        'isDeprecated', 'Boolean!', {}, [], 'Whether the value is deprecated.')
    def _is_deprecated(self):
        return False

    @graphql_field(
        'deprecationReason', 'String', {}, [],
        'An indication of why the value is deprecated, or null.  This is null '
        'if the value is not deprecated.')
    def _deprecation_reason(self):
        """Return a reader-friendly string indicating why this is deprecated.

        Return None if the enum value is not deprecated.
        """
        return None
