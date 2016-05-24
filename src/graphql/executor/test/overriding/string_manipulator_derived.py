from graphql import graphql_field
from graphql import graphql_object
from graphql import graphql_root_field
from string_manipulator_middle import TestStringManipulatorMiddle


@graphql_object('StringManipulatorDerived')
class TestStringManipulatorDerived(TestStringManipulatorMiddle):
    @graphql_field(
        'manipulate', 'String!',
        {'base': 'String!', 'prefix': 'String', 'suffix': 'String'})
    def manipulate(self, base, prefix=None, suffix=None):
        if prefix is None:
            prefix = ''
        if suffix is None:
            suffix = ''
        return u'{:s}{:s}{:s}'.format(prefix, base, suffix)

    @graphql_field(
        'brokenManipulate', 'String!',
        {'base': 'String!', 'prefix': 'String', 'suffix': 'String'})
    def broken_manipulate(self, base, prefix=None, suffix=None):
        # This is broken in GraphQL because it fails to return a non-null
        # value, even though such a value is acceptable in the superclass
        return None

    @staticmethod
    @graphql_root_field(
        'stringManipulatorDerived', 'StringManipulatorDerived!')
    def instance():
        return TestStringManipulatorDerived()
