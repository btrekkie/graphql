from graphql import graphql_attr_field
from graphql import graphql_field
from graphql import graphql_interface


@graphql_interface('Character', 'A character in the Star Wars Trilogy')
@graphql_attr_field(
    'character_id', 'id', 'String!', 'The id of the character.')
@graphql_attr_field('name', 'name', 'String', 'The name of the character.')
@graphql_attr_field(
    'appears_in', 'appearsIn', '[Episode]', 'Which movies they appear in.')
class SwCharacter(object):
    """A character in the Star Wars universe.

    Public attributes:

    list<int> appears_in - A list of the SwEpisode constants indicating
        the films of the original trilogy in which the character
        appears, in chronological order.
    basestring character_id - The ID of the character.
    basestring name - The name of the character.
    """

    # Private attributes:
    # list<SwCharacter> _friends - The character's friends.

    def __init__(self, character_id, name, appears_in):
        self.character_id = character_id
        self.name = name
        self.appears_in = appears_in
        self._friends = []

    def add_friend(self, character):
        self._friends.append(character)

    @graphql_field(
        'friends', '[Character]', {}, [],
        'The friends of the character, or an empty list if they have none.')
    def friends(self):
        return self._friends
