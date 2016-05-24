from graphql import graphql_field
from graphql import graphql_interface
from graphql import graphql_object
from graphql import graphql_root_field
from string_manipulator_base import TestStringManipulatorBase


@graphql_interface('StringManipulatorMiddleInterface')
@graphql_object('StringManipulatorMiddle')
class TestStringManipulatorMiddle(TestStringManipulatorBase):
    @graphql_field(
        'manipulate', 'String', {'base': 'String!', 'prefix': 'String'})
    def manipulate(self, base, prefix=None):
        if prefix is None:
            return None
        else:
            return u'{:s}{:s}'.format(prefix, base)

    @graphql_field(
        'brokenManipulate', 'String', {'base': 'String!', 'prefix': 'String'})
    def broken_manipulate(self, base, prefix=None):
        if prefix is None:
            return None
        else:
            return u'{:s}{:s}'.format(prefix, base)

    @staticmethod
    @graphql_root_field('stringManipulatorMiddle', 'StringManipulatorMiddle!')
    def instance():
        return TestStringManipulatorMiddle()
