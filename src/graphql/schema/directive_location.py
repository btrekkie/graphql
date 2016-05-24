from graphql import graphql_enum


class GraphQlDirectiveLocation(object):
    """A location where a directive may appear in a GraphQL document."""

    # Directive location for queries.
    query = 1

    # Directive location for mutations.
    mutation = 2

    # Directive location for subscriptions.
    subscription = 3

    # Directive location for fields.
    field = 4

    # Directive location for definitions of named fragments.
    fragment_definition = 5

    # Directive location for references to named fragments.
    fragment_spread = 6

    # Directive location for definitions of anonymous fragments.
    inline_fragment = 7

    @staticmethod
    @graphql_enum(
        '__DirectiveLocation',
        'A location where a directive may appear in a GraphQL document.')
    def graphql_to_python():
        """Return a map from GraphQL constant name to GraphQlDirectiveLocation.
        """
        return {
            'FIELD': GraphQlDirectiveLocation.field,
            'FRAGMENT_DEFINITION':
                GraphQlDirectiveLocation.fragment_definition,
            'FRAGMENT_SPREAD': GraphQlDirectiveLocation.fragment_spread,
            'INLINE_FRAGMENT': GraphQlDirectiveLocation.inline_fragment,
            'MUTATION': GraphQlDirectiveLocation.mutation,
            'QUERY': GraphQlDirectiveLocation.query,
            'SUBSCRIPTION': GraphQlDirectiveLocation.subscription,
        }
