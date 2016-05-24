from graphql import graphql_field
from graphql import graphql_interface


@graphql_interface('StringManipulatorBaseInterface')
class TestStringManipulatorBase(object):
    """Performs string manipulation."""

    @graphql_field('manipulate', 'String', {'base': 'String!'})
    def manipulate(self, base, **kwargs):
        """Perform some string manipulation."""
        if base == 'foo':
            return None
        else:
            return base

    @graphql_field('brokenManipulate', 'String', {'base': 'String!'})
    def broken_manipulate(self, base, **kwargs):
        """Perform some string manipulation."""
        if base == 'foo':
            return None
        else:
            return base
