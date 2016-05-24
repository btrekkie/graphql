class GraphQlDirective(object):
    """A directive in a GraphQL document.

    Public attributes:

    dict<basestring, object> args - The arguments to the directive, as
        in GraphQlFieldQuery.args.
    GraphQlDirectiveType directive_type - The type of the directive.
    """

    def __init__(self, directive_type, arguments):
        self.directive_type = directive_type
        self.args = arguments
