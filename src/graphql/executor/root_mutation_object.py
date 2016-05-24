from graphql.schema import GraphQlFuncDescriptor


class GraphQlRootMutationObject(object):
    """The root mutation object for GraphQL.

    This is the object whose fields we "query" at the root level of a
    GraphQL mutation operation.
    """

    # The singleton instance of GraphQlRootMutationObject, or None if we have
    # not created this yet.
    _instance = None

    def __init__(self):
        """Provate constructor."""
        pass

    @staticmethod
    def instance():
        """Return the singleton instance of GraphQlRootMutationObject."""
        if GraphQlRootMutationObject._instance is None:
            GraphQlRootMutationObject._instance = GraphQlRootMutationObject()
        return GraphQlRootMutationObject._instance

    def execute_mutation(self, module_name, class_name, func_name, **kwargs):
        """Execute a mutation and return its value.

        basestring module_name - The name of the Python module containing
            the method or function that executes the mutation
        basestring class_name - The name of the class containing the
            method that executes the mutation, or None if it is not
            implemented using a static method.
        basestring func_name - The name of the method or function that
            executes the mutation.
        dict<basestring, mixed> **kwargs - The keyword arguments to pass
            to the function.
        """
        return GraphQlFuncDescriptor(
            module_name, class_name, func_name).load_func()(**kwargs)
