from character_factory import SwCharacterFactory
from episode import SwEpisode
from graphql import graphql_root_field


class SwHeroes(object):
    """Provides access to the heroes of Star Wars."""

    @staticmethod
    @graphql_root_field(
        'hero', 'Character', {'episode': 'Episode'}, [],
        'The hero of the specified episode.  If the episode is null, this is '
        'the hero of the original trilogy.')
    def hero(episode=None):
        """Return the hero of the specified episode.

        If "episode" is None, return the hero of the original trilogy.

        int episode - A SwEpisode constant indicating the episode.
        return SwCharacter - The hero.
        """
        if episode == SwEpisode.THE_EMPIRE_STRIKES_BACK:
            return SwCharacterFactory.human('1000')
        else:
            return SwCharacterFactory.droid('2001')
