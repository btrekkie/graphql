from graphql import graphql_attr_field
from graphql import graphql_field
from graphql import graphql_object
from input_value import GraphQlInputValue


@graphql_object(
    '__Directive',
    'A type of directive in a GraphQL document, such as @include or @skip')
@graphql_attr_field(
    'name', 'name', 'String!',
    'The name of the directive, excluding the "@" symbol')
@graphql_attr_field(
    'description', 'description', 'String',
    'A description of the directive, or null.  GraphQL favors the Markdown '
    'format.')
class GraphQlDirectiveType(object):
    """A type of directive in a GraphQL document, such as @include or @skip.

    Despite the name, GraphQlDirectiveType does not subclass
    GraphQlType.

    Public attributes:

    dict<basestring, GraphQlType> args - A map from the names of the
        arguments to the directive to their GraphQL types.
    basestring description - A description of the directive, or None.
        GraphQL favors the Markdown format.
    set<GraphQlDirectiveLocation> locations - The locations where the
        directive may appear in a GraphQL document.
    basestring name - The name of the directive, excluding the "@"
        symbol.
    """

    def __init__(self, name, arguments, locations, description):
        self.name = name
        self.args = arguments
        self.locations = locations
        self.description = description

    @graphql_field(
        'locations', '[__DirectiveLocation!]!', {}, [],
        'The locations where the directive may appear in a GraphQL document')
    def _locations(self):
        """Equivalent implementation is contractual."""
        return list(self.locations)

    @graphql_field(
        'args', '[__InputValue!]!', {}, [], 'The arguments to this directive')
    def _args(self):
        """Return the arguments to this, as a list of GraphQlInputValues."""
        args = []
        for name, t in self.args.iteritems():
            args.append(GraphQlInputValue(name, t))
        return args
