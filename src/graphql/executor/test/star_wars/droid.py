from character import SwCharacter
from graphql import graphql_attr_field
from graphql import graphql_object


@graphql_object('Droid', 'A mechanical creature in the Star Wars universe.')
@graphql_attr_field(
    'primary_function', 'primaryFunction', 'String',
    'The primary function of the droid.')
class SwDroid(SwCharacter):
    """A droid in the Star Wars universe.

    Public attributes:

    basestring primary_function - A string describing the droid's
        primary function.
    """

    def __init__(self, character_id, name, appears_in, primary_function):
        super(SwDroid, self).__init__(character_id, name, appears_in)
        self.primary_function = primary_function
