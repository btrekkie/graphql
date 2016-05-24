from base_type import GraphQlBaseType
from enum_value import GraphQlEnumValue
from type_kind import GraphQlTypeKind


class GraphQlEnumType(GraphQlBaseType):
    """An enumeration GraphQL type.

    Public attributes:

    GraphQlFuncDescriptor<() -> dict<basestring, mixed>> func_descriptor
        - A description of a function for obtaining the elements of the
        enumeration.  The function takes no arguments and returns a map
        from the GraphQL constant name of each enum value to the Python
        object representation of the value.  It must be a one-to-one
        mapping whose values are hashable.
    """

    # Private attributes:
    # dict<basestring, mixed> _graphql_to_python - The cached return value of
    #     _graphql_to_python_map.
    # dict<mixed, basestring> _python_to_graphql - A map from the Python object
    #     representation of each enum value to the GraphQL constant name, or
    #     None if we have not computed this yet.

    def __init__(self, name, description, func_descriptor):
        super(GraphQlEnumType, self).__init__(name, description)
        self.func_descriptor = func_descriptor
        self._graphql_to_python = None
        self._python_to_graphql = None

    def _graphql_to_python_map(self):
        """Return a map from GraphQL to Python object.

        Return a map from the GraphQL constant name of each enum value
        to the Python object representation of the value.

        return dict<basestring, mixed> - The enum map.
        """
        if self._graphql_to_python is None:
            self._graphql_to_python = self.func_descriptor.load_func()()
        return self._graphql_to_python

    def graphql_to_python(self, graphql):
        """Return the Python object representation of the specified enum value.

        Return the Python object representation of the enum value with
        the specified GraphQL constant name.  Raise a ValueError if
        there is no such enum value.

        basestring graphql - The GraphQL constant name.
        return mixed - The Python object.
        """
        graphql_to_python = self._graphql_to_python_map()
        if graphql not in graphql_to_python:
            raise ValueError(
                'There is no GraphQL enum value {:s}'.format(graphql))
        return graphql_to_python[graphql]

    def python_to_graphql(self, python):
        """Return the GraphQL constant name for the specified enum value.

        Return the GraphQL constant name for the enum value with the
        specified Python object representation.  Raise a ValueError if
        there is no such enum value.

        mixed python - The Python object.
        return basestring - The GraphQL constant name.
        """
        if self._python_to_graphql is None:
            graphql_to_python = self._graphql_to_python_map()
            self._python_to_graphql = {}
            for graphql, python in graphql_to_python.iteritems():
                self._python_to_graphql[python] = graphql
        if python not in self._python_to_graphql:
            raise ValueError(
                'There is no GraphQL enum value for {:s}'.format(str(python)))
        return self._python_to_graphql[python]

    def field_descriptor(self, name):
        raise ValueError('Enum types do not have fields')

    def _type_kind(self):
        return GraphQlTypeKind.enum

    def _enum_values(self, include_deprecated=False):
        values = []
        for graphql in self._graphql_to_python_map().iterkeys():
            values.append(GraphQlEnumValue(graphql))
        return values
