from graphql import graphql_attr_field
from graphql import graphql_field
from graphql import graphql_mutation
from graphql import graphql_object
from graphql import graphql_root_field


@graphql_object('Ship', 'A space ship')
@graphql_attr_field('name', 'name', 'String!', 'The name of the ship')
@graphql_attr_field('ship_id', 'id', 'ID!', 'The ID of the ship')
class SwShip(object):
    """A space ship.

    Public attributes:

    basestring name - The name of the ship.
    basestring ship_id - The ID of the ship.
    """

    # The ID of the user's favorite ship
    _favorite_ship_id = '3001'

    # The ID of the next ship we introduce, before casting to a string
    _next_id = 3002

    # A map from the IDs of the ships of which we have a record to their names
    _ships = {
        '3000': 'Millennium Falcon',
        '3001': 'X-wing',
    }

    def __init__(self, ship_id, name):
        self.ship_id = ship_id
        self.name = name

    @graphql_field('brokenId', 'ID!', {}, [], 'The ID of the ship')
    def broken_id(self):
        """Broken method that is supposed to return the ID of the ship."""
        return int(self.ship_id)

    @staticmethod
    def introduce_ship(name):
        """Add a ship with the specified name to our records."""
        SwShip._ships[str(SwShip._next_id)] = name
        ship = SwShip(str(SwShip._next_id), name)
        SwShip._next_id += 1
        return ship

    @staticmethod
    def reset():
        """Undo all prior mutations."""
        SwShip._ships = {
            '3000': 'Millennium Falcon',
            '3001': 'X-wing',
        }
        SwShip._next_id = 3002
        SwShip._favorite_ship_id = '3001'

    @staticmethod
    @graphql_root_field(
        'shipFromName', 'Ship', {'name': 'String!'}, [],
        'The ship with the specified name, or null if there is no such ship.',
        True, 'Use Query{search} instead')
    def get_from_name(name):
        """Return the SwShip with the specified name, if any."""
        for ship_id, ship_name in SwShip._ships.iteritems():
            if ship_name == name:
                return SwShip(ship_id, ship_name)
        return None

    @staticmethod
    @graphql_root_field(
        'fastestShip', 'Ship!', {}, [],
        'Return the fastest ship in the galaxy')
    def broken_get_fastest_ship():
        """Broken method supposed to return the fastest SwShip in the galaxy.
        """
        return 'Mellennium Falcon'

    @staticmethod
    @graphql_root_field(
        'slowestShip', 'Ship!', {}, [],
        'Return the slowest ship in the galaxy')
    def broken_get_slowest_ship():
        """Broken method supposed to return the slowest SwShip in the galaxy.
        """
        return None

    @staticmethod
    @graphql_root_field(
        'allShips', '[Ship!]!', {}, [],
        'Return all of the ships in our records')
    def broken_get_all_ships():
        """Broken method supposed to return all the SwShips in our records.

        return list<SwShip> - The ships.
        """
        ships = []
        for ship_id, name in SwShip._ships.iteritems():
            ships.append(SwShip(ship_id, name))
        ships.append(None)
        return ships

    @staticmethod
    @graphql_root_field(
        'largestShip', 'Ship', {}, [], 'Return the largest ship in the galaxy')
    def broken_get_largest_ship():
        """Broken method supposed to return the largest SwShip in the galaxy.
        """
        raise RuntimeError()

    @staticmethod
    def favorite_ship():
        """Return the user's favorite SwShip."""
        return SwShip(
            SwShip._favorite_ship_id, SwShip._ships[SwShip._favorite_ship_id])

    @staticmethod
    @graphql_mutation(
        'setFavoriteShip', 'Ship', {'id': 'ID!'}, [],
        "Sets the user's favorite ship to be the one with the specified ID, "
        'and returns the ship.  If there is no ship with the specified ID, '
        'this returns null without altering the favorite ship.')
    def set_favorite_ship(id):
        """Set the user's favorite ship to be the one with the specified ID.

        Return the SwShip.  If there is no ship with the specified ID,
        return None without altering the favorite ship.
        """
        if id not in SwShip._ships:
            return None
        else:
            SwShip._favorite_ship_id = id
            return SwShip.favorite_ship()


@graphql_root_field(
    'ship', 'Ship!', {'id': 'ID!'}, [],
    'The ship with the specified ID.  Emits an error if there is no such '
    'ship.')
def get_sw_ship(id):
    """Return the SwShip with the given ID.  Raise if there is no such ship."""
    if id not in SwShip._ships:
        raise ValueError(u'There is no ship with ID {:s}'.format(id))
    return SwShip(id, SwShip._ships[id])
