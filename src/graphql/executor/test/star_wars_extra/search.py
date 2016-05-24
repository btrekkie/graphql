from graphql import graphql_root_field
from graphql import graphql_union
from graphql.executor.test.star_wars import SwCharacterFactory
from ship import SwShip


class SwSearch(object):
    """Provides the ability to search for objects."""

    @staticmethod
    @graphql_union('SearchResult', 'An object located in a search')
    def graphql_search_result():
        """GraphQL union for the objects located in a search."""
        return ['Character', 'Ship']

    @staticmethod
    @graphql_root_field(
        'search', 'SearchResult', {'name': 'String!'}, [],
        'Searches for an object with the specified name')
    def search(name):
        """Return the object with the specified name, if any.

        return SwCharacter|SwShip - The object.
        """
        character = SwCharacterFactory.get_from_name(name)
        if character is not None:
            return character
        else:
            return SwShip.get_from_name(name)
