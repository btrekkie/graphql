from graphql.executor import GraphQlContext
from graphql.schema import GraphQlSchemaFactory


class GraphQlContextWithEmail(GraphQlContext):
    """A GraphQlContext with an email context argument.

    The context argument for "email" is the email address of the current
    user.  The schema is for the graphql.executor.test.star_wars_extra
    module.
    """

    def __init__(self, email):
        schema = GraphQlSchemaFactory.create_from_modules([
            'graphql.executor.test.star_wars',
            'graphql.executor.test.star_wars_extra',
            'graphql.scalar_descriptors.strict'])
        super(GraphQlContextWithEmail, self).__init__(schema)
        self._email = email

    def context_arg(self, name):
        if name == 'email':
            return self._email
        else:
            raise ValueError(u'Unknown context argument {:s}'.format(name))
