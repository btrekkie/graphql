from graphql import graphql_enum


class SwEpisode(object):
    """An enumeration of the episodes in the original Star Wars trilogy."""

    # Constants for the episodes
    A_NEW_HOPE = 4
    THE_EMPIRE_STRIKES_BACK = 5
    RETURN_OF_THE_JEDI = 6

    @staticmethod
    @graphql_enum('Episode', 'One of the films in the Star Wars Trilogy')
    def graphql_episode_enum():
        """GraphQL enumeration for the episodes."""
        return {
            'NEWHOPE': SwEpisode.A_NEW_HOPE,
            'EMPIRE': SwEpisode.THE_EMPIRE_STRIKES_BACK,
            'JEDI': SwEpisode.RETURN_OF_THE_JEDI,
        }
