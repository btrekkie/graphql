class GraphQlFragmentReference(object):
    """An anonymous fragment definition or a reference to a named fragment.

    An anonymous fragment definition or a reference to a named fragment
    in a GraphQL document.  This is not for named fragment definitions.

    Public attributes:

    list<GraphQlDirective> directives - The directives for the fragment
        reference.
    GraphQlFragment fragment - The fragment we are referencing.
    """

    def __init__(self, fragment, directives):
        self.fragment = fragment
        self.directives = directives
