from graphql import graphql_attr_field
from graphql import graphql_input_object
from graphql import graphql_mutation
from graphql import graphql_object
from ship import SwShip


@graphql_object('IntroduceShipPayload', 'The payload type for introduceShip')
@graphql_attr_field('ship', 'ship', 'Ship!', 'The ship we introduced')
@graphql_attr_field(
    'mutation_id', 'clientMutationId', 'String!', 'The Relay mutation ID')
class SwIntroduceShipMutation(object):
    """Mutation for introducing ships to our records.

    Public attributes:

    basestring mutation_id - The Relay mutation ID.
    SwShip ship - The ship we introduced.
    """

    def __init__(self, mutation_id, ship):
        self.mutation_id = mutation_id
        self.ship = ship

    @staticmethod
    @graphql_input_object(
        'IntroduceShipInput', 'The input type for introduceShip')
    def input_type():
        """Describe the input type for introduce ship mutations.

        return dict<basestring, basestring> - A map from the names of
            the input object fields to their type strings.
        """
        return {
            'clientMutationId': 'String!',
            'name': 'String!',
        }

    @staticmethod
    @graphql_mutation(
        'introduceShip', 'IntroduceShipPayload',
        {'input': 'IntroduceShipInput!'}, [],
        'Adds a ship with the specified name to our records')
    def introduce_ship(input):
        """Add a ship to our records.

        dict<basestring, object> input - The input object, formatted as
            suggested in the return value of input_type().
        return IntroduceShipMutation - The results of the mutation.
        """
        ship = SwShip.introduce_ship(input['name'])
        return SwIntroduceShipMutation(input['clientMutationId'], ship)

    @staticmethod
    @graphql_mutation(
        'introduceShipWithName', 'Ship!', {'name': 'String!'}, [],
        'Adds a ship with the specified name to our records', True)
    def introduce_ship_with_name(name):
        """Add a ship to our records.

        basestring name - The name of the ship.
        return Ship - The ship.
        """
        mutation = SwIntroduceShipMutation.introduce_ship(
            {'clientMutationId': '', 'name': name})
        return mutation.ship
