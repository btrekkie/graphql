from graphql import graphql_field
from graphql import graphql_object
from graphql import graphql_root_field


@graphql_object('Math')
class TestGraphQlMath(object):
    @staticmethod
    @graphql_root_field('math', 'Math')
    def instance():
        return TestGraphQlMath()

    @graphql_field('sum', 'Float', {'numbers': '[Float!]!'})
    def float_sum(self, numbers):
        return sum(numbers)

    @graphql_field('intSum', 'Int', {'numbers': '[Int!]!'})
    def int_sum(self, numbers):
        return sum(numbers)
