class GraphQlFragment(object):
    """A named or anonymous fragment definition.

    When we first encounter a named fragment or a reference to it, we
    initialize the fields to be None.  We set the fields if and when we
    finish reading the fragment's definition.

    list<GraphQlDirective> directives - The directives for the fragment
        definition.
    GraphQlBaseType object_type - The type on which the fragment is
        conditioned.
    GraphQlSelectionSet selection_set - The selection set indicating the
        information to request wherever we reference the fragment.
    """
    def __init__(self):
        self.object_type = None
        self.selection_set = None
        self.directives = None
