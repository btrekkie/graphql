class GraphQlSelectionSet(object):
    """A selection set in a GraphQL document.

    A selection set consists of field queries and / or fragment
    references.

    GraphQlBaseType base_type - The base type of the object whose fields
        we are requesting.
    list<GraphQlFieldQuery|GraphQlFragmentReference>
        field_queries_and_fragments - The field queries and / or
        fragment references that comprise this selection set.
    """
    def __init__(self, base_type, field_queries_and_fragments):
        self.base_type = base_type
        self.field_queries_and_fragments = field_queries_and_fragments
