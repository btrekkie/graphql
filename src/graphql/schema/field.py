class GraphQlField(object):
    """A GraphQL field.

    Consists of a GraphQlFieldDescriptor describing the field's
    "interface" as well as other attributes indicating the
    "implementation" - the way to determine the field's value.  This is
    also for GraphQL mutations, which are basically like fields.

    Public attributes:

    basestring attr - The name of the attribute containing the field's
        value, as in getattr.  This is None if we obtain the field's
        value using a method.
    list<basestring> context_args - A list of the context arguments to
        include in the keyword arguments to method_name.  This is None
        if we obtain the field's value using an attribute.  See
        GraphQlContext.context_arg.
    GraphQlFieldDescriptor descriptor - A descriptor describing the
        field's "interface".
    basestring method_name - The name of the method to call to determine
        the field's value.  This is None if we obtain the field's value
        using an attribute.
    tuple partial_args - The positional arguments to pass to
        method_name.  Each element must be a JSON value.  This is None
        if we obtain the field's value using an attribute.
    dict<basestring, object> partial_kwargs - The keyword arguments to
        pass to method_name, which we pass in addition to the arguments
        indicated in the GraphQL document.  Each entry must be a JSON
        value.  This is None if we obtain the field's value using an
        attribute.
    """

    def __init__(
            self, descriptor, method_name, partial_args, partial_kwargs,
            context_args, attr):
        self.descriptor = descriptor
        self.method_name = method_name
        self.partial_args = partial_args
        self.partial_kwargs = partial_kwargs
        if context_args is not None:
            self.context_args = list(set(context_args))
        else:
            self.context_args = None
        self.attr = attr

    @staticmethod
    def create_from_method(
            descriptor, method_name, partial_args, partial_kwargs,
            context_args):
        """Return a GraphQlField for a field we obtain using a method call."""
        return GraphQlField(
            descriptor, method_name, partial_args, partial_kwargs,
            context_args, None)

    @staticmethod
    def create_from_attr(descriptor, attr):
        """Return a GraphQlField for a field we obtain by using an attribute.
        """
        return GraphQlField(descriptor, None, None, None, None, attr)
