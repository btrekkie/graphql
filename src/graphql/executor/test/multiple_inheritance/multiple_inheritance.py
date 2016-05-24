from graphql import graphql_interface
from graphql import graphql_object
from graphql import graphql_root_field


@graphql_interface('MultipleInheritanceInterface')
class MultipleInheritanceTestRoot(object):
    pass


@graphql_interface('MultipleInheritanceInterfaceF')
@graphql_object('MultipleInheritanceF')
class MultipleInheritanceTestF(MultipleInheritanceTestRoot):
    pass


@graphql_object('MultipleInheritanceE')
class MultipleInheritanceTestE(MultipleInheritanceTestRoot):
    pass


@graphql_object('MultipleInheritanceD')
class MultipleInheritanceTestD(MultipleInheritanceTestRoot):
    pass


class MultipleInheritanceTestC(
        MultipleInheritanceTestD, MultipleInheritanceTestF):
    @staticmethod
    @graphql_root_field('getC', 'MultipleInheritanceInterface')
    def instance():
        return MultipleInheritanceTestA()


class MultipleInheritanceTestB(
        MultipleInheritanceTestD, MultipleInheritanceTestE):
    @staticmethod
    @graphql_root_field('getB', 'MultipleInheritanceInterface')
    def instance():
        return MultipleInheritanceTestA()


class MultipleInheritanceTestA(
        MultipleInheritanceTestB, MultipleInheritanceTestC):
    @staticmethod
    @graphql_root_field('getA', 'MultipleInheritanceInterface')
    def instance():
        return MultipleInheritanceTestA()

    @staticmethod
    @graphql_root_field('getAAsF', 'MultipleInheritanceInterfaceF')
    def broken_get_as_f():
        """Return an instance of MultipleInheritanceTestA.

        This is broken as a GraphQL field, because even though
        MultipleInheritanceTestA is a subclass of
        MultipleInheritanceTestF, the GraphQL type
        MultipleInheritanceD does not implement the GraphQL interface
        MultipleInheritanceInterfaceF.
        """
        return MultipleInheritanceTestA()
