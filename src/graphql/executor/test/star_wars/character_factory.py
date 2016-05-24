from droid import SwDroid
from episode import SwEpisode
from graphql import graphql_root_field
from human import SwHuman


class SwCharacterFactory(object):
    """Provides access to the SwCharacters."""

    # The cached return value of _get_characters().
    _characters = None

    @staticmethod
    def _get_characters():
        """Return a map from the IDs of the SwCharacters to the SwCharacters.
        """
        if SwCharacterFactory._characters is None:
            luke = SwHuman(
                '1000', 'Luke Skywalker', [
                    SwEpisode.A_NEW_HOPE,
                    SwEpisode.THE_EMPIRE_STRIKES_BACK,
                    SwEpisode.RETURN_OF_THE_JEDI],
                'Tatooine')
            darth_vader = SwHuman(
                '1001', 'Darth Vader', [
                    SwEpisode.A_NEW_HOPE,
                    SwEpisode.THE_EMPIRE_STRIKES_BACK,
                    SwEpisode.RETURN_OF_THE_JEDI],
                'Tatooine')
            han = SwHuman(
                '1002', 'Han Solo', [
                    SwEpisode.A_NEW_HOPE,
                    SwEpisode.THE_EMPIRE_STRIKES_BACK,
                    SwEpisode.RETURN_OF_THE_JEDI],
                None)
            leia = SwHuman(
                '1003', 'Leia Organa', [
                    SwEpisode.A_NEW_HOPE,
                    SwEpisode.THE_EMPIRE_STRIKES_BACK,
                    SwEpisode.RETURN_OF_THE_JEDI],
                'Alderaan')
            tarkin = SwHuman(
                '1004', 'Wilhuff Tarkin', [SwEpisode.A_NEW_HOPE], None)
            threepio = SwDroid(
                '2000', 'C-3PO', [
                    SwEpisode.A_NEW_HOPE,
                    SwEpisode.THE_EMPIRE_STRIKES_BACK,
                    SwEpisode.RETURN_OF_THE_JEDI],
                'Protocol')
            artoo = SwDroid(
                '2001', 'R2-D2', [
                    SwEpisode.A_NEW_HOPE,
                    SwEpisode.THE_EMPIRE_STRIKES_BACK,
                    SwEpisode.RETURN_OF_THE_JEDI],
                'Astromech')

            luke.add_friend(han)
            luke.add_friend(leia)
            luke.add_friend(threepio)
            luke.add_friend(artoo)
            darth_vader.add_friend(tarkin)
            han.add_friend(luke)
            han.add_friend(leia)
            han.add_friend(artoo)
            leia.add_friend(luke)
            leia.add_friend(han)
            leia.add_friend(threepio)
            leia.add_friend(artoo)
            threepio.add_friend(luke)
            threepio.add_friend(han)
            threepio.add_friend(leia)
            threepio.add_friend(artoo)
            artoo.add_friend(luke)
            artoo.add_friend(han)
            artoo.add_friend(leia)

            SwCharacterFactory._characters = {}
            characters = [
                luke, darth_vader, han, leia, tarkin, threepio, artoo]
            for character in characters:
                SwCharacterFactory._characters[character.character_id] = (
                    character)
        return SwCharacterFactory._characters

    @staticmethod
    @graphql_root_field(
        'human', 'Human', {'id': 'String!'}, [],
        'The human with the specified ID, if any')
    def human(id):
        """Return the SwHuman with the specified ID, if any."""
        character = SwCharacterFactory._get_characters().get(id)
        if isinstance(character, SwHuman):
            return character
        else:
            return None

    @staticmethod
    @graphql_root_field(
        'droid', 'Droid', {'id': 'String!'}, [],
        'The droid with the specified ID, if any')
    def droid(id):
        """Return the SwDroid with the specified ID, if any."""
        character = SwCharacterFactory._get_characters().get(id)
        if isinstance(character, SwDroid):
            return character
        else:
            return None

    @staticmethod
    def get_from_name(name):
        """Return the SwCharacter with the specified name, if any."""
        for character in SwCharacterFactory._get_characters().itervalues():
            if character.name == name:
                return character
        return None
