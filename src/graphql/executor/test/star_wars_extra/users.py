import sys

from graphql import graphql_mutation
from graphql import graphql_root_field
from graphql import GraphQlResultWithErrors
from graphql.executor.test.star_wars import SwCharacterFactory


class SwUsers(object):
    """Provides functionality pertaining to user accounts."""

    # A set of all of the email addresses for the accounts
    _emails = set(['foo@example.com'])

    @staticmethod
    @graphql_mutation(
        'register', 'Boolean!',
        {'captchaToken': 'String!', 'email': 'String!', 'password': 'String!'},
        [],
        'Registers a new user account.  Returns whether we verified the '
        'CAPTCHA token.')
    def register(email, password, captcha_token):
        """Register a new user account.

        basestring email - The email address for the account.
        basestring password - The password for the account.
        basestring captcha_token - A single-use token demonstrating that
            the user has solved a CAPTCHA.
        return bool|GraphQlResultWithErrors<bool> - Whether we verified
            captcha_token.  If verify it, but there are errors
            registering an account, then the user will need to solve
            another CAPTCHA in order to register again.
        """
        checked_captcha = False
        try:
            if len(password) < 6:
                raise ValueError('Password must be at least 6 characters')
            elif '@' not in email:
                raise ValueError('Invalid email address')

            checked_captcha = True
            if captcha_token != 'abc123':
                raise ValueError('Invalid CAPTCHA token')

            if email in SwUsers._emails:
                raise ValueError(
                    'There is already a user with that email address')
            SwUsers._emails.add(email)
            return checked_captcha
        except Exception as exception:
            return GraphQlResultWithErrors(
                checked_captcha, exception, sys.exc_info())

    @staticmethod
    def reset():
        """Undo all prior mutations."""
        SwUsers._emails = set(['foo@example.com'])

    @staticmethod
    @graphql_root_field(
        'favoriteCharacter', 'Character', {}, ['email'],
        "The user's favorite character")
    def favorite_character(email):
        """Return the user's favorite SwCharacter.

        basestring email - The user's email address.
        return SwCharacter - The favorite character.
        """
        if email == 'foo@example.com':
            return SwCharacterFactory.human('1001')
        else:
            return SwCharacterFactory.droid('2001')
