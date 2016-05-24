from character import SwCharacter
from graphql import graphql_attr_field
from graphql import graphql_object


@graphql_object('Human', 'A humanoid creature in the Star Wars universe.')
@graphql_attr_field(
    'home_planet', 'homePlanet', 'String',
    'The home planet of the human, or null if unknown.')
class SwHuman(SwCharacter):
    """A human in the Star Wars universe.

    Public attributes:

    basestring home_planet - The planet on which the character was
        raised, if this is known.
    """

    def __init__(self, character_id, name, appears_in, home_planet):
        super(SwHuman, self).__init__(character_id, name, appears_in)
        self.home_planet = home_planet
