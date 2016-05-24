class GraphQlFieldQuery(object):
    """A request for the value of a GraphQL object's field.

    dict<basestring, object> args - The arguments to the field.  The
        entries are the Python object representations of the arguments'
        values, with GraphQlVariableReference objects for variable
        references.  The entries are not None and do not contain the
        value None.
    list<GraphQlDirective> directives - The directives for the field
        query.
    FieldDescriptor field_descriptor - The description of the field we
        are querying.
    basestring response_key - The key that maps to the field's value in
        the GraphQL response.
    GraphQlSelectionSet selection_set - The selection set indicating the
        information to request from the field.
    """

    def __init__(
            self, response_key, field_descriptor, arguments, selection_set,
            directives):
        self.response_key = response_key
        self.field_descriptor = field_descriptor
        self.args = arguments
        self.selection_set = selection_set
        self.directives = directives
