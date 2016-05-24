from graphql.schema import GraphQlFuncDescriptor


class GraphQlRootQueryObject(object):
    """The root query object for GraphQL.

    This is the object whose fields we query at the root level of a
    GraphQL query operation.
    """

    # The singleton instance of GraphQlRootQueryObject, or None if we have not
    # created this yet.
    _instance = None

    def __init__(self):
        """Private constructor."""
        pass

    @staticmethod
    def instance():
        """Return the singleton instance of GraphQlRootQueryObject."""
        if GraphQlRootQueryObject._instance is None:
            GraphQlRootQueryObject._instance = GraphQlRootQueryObject()
        return GraphQlRootQueryObject._instance

    def field(self, module_name, class_name, func_name, **kwargs):
        """Return the value of a root field.

        basestring module_name - The name of the Python module containing
            the method or function that returns the field's value.
        basestring class_name - The name of the class containing the
            method that returns the field's value, or None if it is not
            implemented using a static method.
        basestring func_name - The name of the method or function that
            returns the field's value.
        dict<basestring, mixed> **kwargs - The keyword arguments to pass
            to the function.
        """
        return GraphQlFuncDescriptor(
            module_name, class_name, func_name).load_func()(**kwargs)
