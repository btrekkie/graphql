from graphql import graphql_attr_field
from graphql import graphql_field
from graphql import graphql_object
from ship import get_sw_ship


@graphql_object('Faction', 'A political / military faction')
@graphql_attr_field(
    'short_name', 'name', 'String!', 'The name of the faction', True,
    'Replaced with shortName and longName')
@graphql_attr_field(
    'short_name', 'shortName', 'String!',
    'The short form of the name of the faction')
@graphql_attr_field(
    'long_name', 'longName', 'String!',
    'The long form of the name of the faction')
class SwFaction(object):
    """A political / military faction.

    Public attributes:

    basestring long_name - The long form of the name of the faction.
    basestring short_name - The short form of the name of the faction.
    """

    def __init__(self, short_name, long_name, most_powerful_ship_id):
        self.short_name = short_name
        self.long_name = long_name
        self._most_powerful_ship_id = most_powerful_ship_id

    @graphql_field(
        'mostPowerfulShip', 'Ship!', {}, [],
        "The most powerful ship in the faction's fleet")
    def most_powerful_ship(self):
        """Return the most powerful ship in the faction's fleet."""
        get_sw_ship(self._most_powerful_ship_id)

    @graphql_field(
        'bestShip', 'Ship!', {}, [],
        "The most powerful ship in the faction's fleet", True)
    def best_ship(self):
        """Return the most powerful ship in the faction's fleet."""
        return self.most_powerful_ship()
